from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
import os
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib import messages
from .forms import DataInputForm, SimulationForm
import sys
import io
import base64
import urllib.parse
import matplotlib
matplotlib.use('Agg')
from django.core.cache import cache
from django.views.decorators.cache import cache_page

current_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))

source_files_dir = os.path.join(project_root, 'source_files')
sys.path.append(source_files_dir)

from experimental import update_table, global_heatmap
from simulation import simulate_and_show_table
from comparison import simulate_digestion, process_experimental_data, compare_results

def home(request):
    return redirect('data_input')

def data_input(request):
    global_heatmap_url = None
    peptide_table = None
    excel_files = []
    form = DataInputForm()
    simulation_form = SimulationForm()
    protease = None

    if request.method == 'POST':
        if 'layer' in request.POST:
            # Handle AJAX request for updating global heatmap
            selected_layer = request.POST.get('layer')
            protease = request.POST.get('protease')
            if protease and selected_layer:
                cache_key = f'heatmap_{protease}_{selected_layer}'
                cached_heatmap = cache.get(cache_key)

                if cached_heatmap:
                    global_heatmap_url, excel_files = cached_heatmap
                else:
                    global_heatmap_base64, excel_files = global_heatmap(protease, selected_layer)
                    global_heatmap_url = f"data:image/png;base64,{global_heatmap_base64}"
                    cache.set(cache_key, (global_heatmap_url, excel_files), 3600)

                return JsonResponse({
                    'global_heatmap_url': global_heatmap_url,
                    'excel_files': excel_files
                })
            else:
                return JsonResponse({'error': 'Invalid request'}, status=400)
        elif 'simulate_digestion' in request.POST:
            simulation_form = SimulationForm(request.POST, request.FILES)
            if simulation_form.is_valid():
                fasta_file = simulation_form.cleaned_data['simulation_fasta_file']
                protease = simulation_form.cleaned_data['simulation_protease']
                runs = simulation_form.cleaned_data['simulation_runs']

                temp_fasta_path = default_storage.save('temp_simulation_fasta.fasta', ContentFile(fasta_file.read()))
                temp_fasta_full_path = os.path.join(settings.MEDIA_ROOT, temp_fasta_path)

                try:
                    simulation_table = simulate_and_show_table(temp_fasta_full_path, protease, n=runs)
                    global_heatmap_base64, excel_files = global_heatmap(protease)
                    global_heatmap_url = f"data:image/png;base64,{global_heatmap_base64}"
                    peptide_table = simulation_table
                    messages.success(request, 'Simulation completed successfully.')
                except Exception as e:
                    messages.error(request, f'Error in simulation: {str(e)}')
                finally:
                    default_storage.delete(temp_fasta_path)
            else:
                messages.error(request, 'Invalid simulation form submission. Please check your inputs.')
        else:
            # This is for experimental data input
            form = DataInputForm(request.POST, request.FILES)
            if form.is_valid():
                fasta_file = form.cleaned_data['fasta_file']
                excel_file = form.cleaned_data['excel_file']
                protease = form.cleaned_data['protease']
                protein_name = form.cleaned_data['protein_name']
                compare_with_simulation = form.cleaned_data['compare_with_simulation']

                temp_fasta_path = default_storage.save('temp_fasta.fasta', ContentFile(fasta_file.read()))
                temp_excel_path = default_storage.save('temp_excel.xlsx', ContentFile(excel_file.read()))

                temp_fasta_full_path = os.path.join(settings.MEDIA_ROOT, temp_fasta_path)
                temp_excel_full_path = os.path.join(settings.MEDIA_ROOT, temp_excel_path)

                try:
                    if compare_with_simulation:
                        simulation_results = simulate_digestion(temp_fasta_full_path, protease, n=10)
                        experimental_results = process_experimental_data(temp_excel_full_path)
                        peptide_table = compare_results(experimental_results, simulation_results)
                        messages.success(request, 'Experimental data processed and compared with simulation successfully.')
                    else:
                        update_table(temp_fasta_full_path, temp_excel_full_path, protease, protein_name)
                        messages.success(request, 'Experimental data processed successfully.')

                    global_heatmap_base64, excel_files = global_heatmap(protease)
                    global_heatmap_url = f"data:image/png;base64,{global_heatmap_base64}"

                except Exception as e:
                    messages.error(request, f'Error processing experimental data: {str(e)}')
                finally:
                    default_storage.delete(temp_fasta_path)
                    default_storage.delete(temp_excel_path)

                cache.clear()
            else:
                messages.error(request, 'Invalid experimental data form submission. Please check your inputs.')

    context = {
        'form': form,
        'simulation_form': simulation_form,
        'global_heatmap_url': global_heatmap_url,
        'peptide_table': peptide_table,
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