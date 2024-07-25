from django.shortcuts import render
from django.http import HttpResponse
import os
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib import messages
from .forms import DataInputForm, LayerSelectForm
import sys

current_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))

source_files_dir = os.path.join(project_root, 'source_files')
sys.path.append(source_files_dir)

import experimental as exp
from experimental import global_heatmap
import simulation as sim


def data_input(request):
    global_heatmap_url = None
    layer_form = None
    experiment_heatmap_url = None
    simulation_table = None

    try:
        global_heatmap_base64, excel_files = global_heatmap()
        global_heatmap_url = f"data:image/png;base64,{global_heatmap_base64}"
        layer_form = LayerSelectForm(excel_files=excel_files)

        if request.method == 'POST':
            form = DataInputForm(request.POST, request.FILES)
            layer_form = LayerSelectForm(request.POST, excel_files=excel_files)
            if form.is_valid():
                fasta_file = request.FILES['fasta_file']
                excel_file = request.FILES['excel_file']
                protease = form.cleaned_data['protease']
                protein_name = form.cleaned_data['protein_name']

                # Save uploaded files temporarily
                temp_fasta_path = default_storage.save('temp_fasta.fasta', ContentFile(fasta_file.read()))
                temp_excel_path = default_storage.save('temp_excel.xlsx', ContentFile(excel_file.read()))

                # Get the full file paths
                temp_fasta_full_path = os.path.join(settings.MEDIA_ROOT, temp_fasta_path)
                temp_excel_full_path = os.path.join(settings.MEDIA_ROOT, temp_excel_path)

                # Process the files
                try:
                    exp.update_table(temp_fasta_full_path, temp_excel_full_path, protease, protein_name)
                    messages.success(request, 'Files processed successfully.')

                    # Generate experiment heatmap
                    experiment_heatmap = exp.experiment_heatmap()
                    experiment_heatmap_url = plot_to_img(experiment_heatmap)

                    # Generate simulation table
                    simulation_table = sim.show_table()

                except Exception as e:
                    messages.error(request, f'Error processing files: {str(e)}')
                finally:
                    # Clean up temporary files
                    default_storage.delete(temp_fasta_path)
                    default_storage.delete(temp_excel_path)

            if layer_form.is_valid():
                selected_layer = layer_form.cleaned_data['layer']
                global_heatmap_base64, _ = global_heatmap(selected_layer)
                global_heatmap_url = f"data:image/png;base64,{global_heatmap_base64}"
        else:
            form = DataInputForm()

    except FileNotFoundError as e:
        messages.error(request, str(e))
        form = DataInputForm()

    context = {
        'form': form,
        'layer_form': layer_form,
        'experiment_heatmap_url': experiment_heatmap_url,
        'global_heatmap_url': global_heatmap_url,
        'simulation_table': simulation_table,
    }

    return render(request, 'data_input/data_input.html', context)

def plot_to_img(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    return 'data:image/png;base64,' + urllib.parse.quote(string)