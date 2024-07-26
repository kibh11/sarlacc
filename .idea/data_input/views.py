from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
import os
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib import messages
from .forms import DataInputForm
import sys
import io
import base64
import urllib.parse
import matplotlib
matplotlib.use('Agg')
from django.shortcuts import redirect
from django.core.cache import cache
from django.views.decorators.cache import cache_page

# Add this function at the top of your views.py
def home(request):
    return redirect('data_input')


current_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))

source_files_dir = os.path.join(project_root, 'source_files')
sys.path.append(source_files_dir)

import experimental as exp
from experimental import global_heatmap
from simulation import simulate_and_show_table

def data_input(request):
    global_heatmap_url = None
    experiment_heatmap_url = None
    simulation_table = None
    excel_files = []
    protease = None

    if request.method == 'POST':
        if 'layer' in request.POST:
            # Handle AJAX request for updating global heatmap
            selected_layer = request.POST.get('layer')
            protease = request.POST.get('protease')
            if protease and selected_layer:
                # Create a unique cache key
                cache_key = f'heatmap_{protease}_{selected_layer}'

                # Try to get the cached heatmap
                cached_heatmap = cache.get(cache_key)

                if cached_heatmap:
                    global_heatmap_url, excel_files = cached_heatmap
                else:
                    # If not in cache, generate the heatmap
                    global_heatmap_base64, excel_files = global_heatmap(protease, selected_layer)
                    global_heatmap_url = f"data:image/png;base64,{global_heatmap_base64}"

                    # Cache the result for 1 hour (3600 seconds)
                    cache.set(cache_key, (global_heatmap_url, excel_files), 3600)

                return JsonResponse({
                    'global_heatmap_url': global_heatmap_url,
                    'excel_files': excel_files
                })
            else:
                return JsonResponse({'error': 'Invalid request'}, status=400)
        else:
            # Handle regular form submission
            form = DataInputForm(request.POST, request.FILES)
            if form.is_valid():
                fasta_file = form.cleaned_data['fasta_file']
                excel_file = form.cleaned_data['excel_file']
                protease = form.cleaned_data['protease']
                protein_name = form.cleaned_data['protein_name']

                # Process the files
                temp_fasta_path = default_storage.save('temp_fasta.fasta', ContentFile(fasta_file.read()))
                temp_excel_path = default_storage.save('temp_excel.xlsx', ContentFile(excel_file.read()))

                temp_fasta_full_path = os.path.join(settings.MEDIA_ROOT, temp_fasta_path)
                temp_excel_full_path = os.path.join(settings.MEDIA_ROOT, temp_excel_path)

                try:
                    exp.update_table(temp_fasta_full_path, temp_excel_full_path, protease, protein_name)
                    messages.success(request, 'Files processed successfully.')

                    # experiment_heatmap = exp.experiment_heatmap()
                    # experiment_heatmap_url = plot_to_img(experiment_heatmap)
                    #
                    simulation_table = simulate_and_show_table(temp_fasta_full_path, protease)

                    global_heatmap_base64, excel_files = global_heatmap(protease)
                    global_heatmap_url = f"data:image/png;base64,{global_heatmap_base64}"

                except Exception as e:
                    messages.error(request, f'Error processing files: {str(e)}')
                finally:
                    default_storage.delete(temp_fasta_path)
                    default_storage.delete(temp_excel_path)

                cache.clear()

            else:
                messages.error(request, 'Invalid form submission. Please check your inputs.')
    else:
        form = DataInputForm()

    context = {
        'form': form,
        'experiment_heatmap_url': experiment_heatmap_url,
        'global_heatmap_url': global_heatmap_url,
        'simulation_table': simulation_table,
        'excel_files': excel_files,
        'protease': protease,
    }

    return render(request, 'data_input/data_input.html', context)

def plot_to_img(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    return 'data:image/png;base64,' + urllib.parse.quote(string)