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

import experimental as exp
from experimental import global_heatmap
from simulation import simulate_and_show_table

def home(request):
    return redirect('data_input')

def data_input(request):
    print("View called")
    global_heatmap_url = None
    simulation_table = None
    excel_files = []
    form = DataInputForm()
    simulation_form = SimulationForm()
    protease = None

    if request.method == 'POST':
        print("POST request received")
        print("POST data:", request.POST)
        print("FILES:", request.FILES)

        if 'layer' in request.POST:
            print("Handling layer request")
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
            print("Simulation form submitted")
            simulation_form = SimulationForm(request.POST, request.FILES)
            if simulation_form.is_valid():
                print("Simulation form is valid")
                fasta_file = simulation_form.cleaned_data['simulation_fasta_file']
                protease = simulation_form.cleaned_data['simulation_protease']
                runs = simulation_form.cleaned_data['simulation_runs']

                temp_fasta_path = default_storage.save('temp_simulation_fasta.fasta', ContentFile(fasta_file.read()))
                temp_fasta_full_path = os.path.join(settings.MEDIA_ROOT, temp_fasta_path)

                try:
                    print("Generating simulation table")
                    simulation_table = simulate_and_show_table(temp_fasta_full_path, protease, n=runs)
                    print("Generating global heatmap")
                    global_heatmap_base64, excel_files = global_heatmap(protease)
                    global_heatmap_url = f"data:image/png;base64,{global_heatmap_base64}"
                    print("Simulation completed successfully")
                except Exception as e:
                    print(f"Error in simulation: {str(e)}")
                    messages.error(request, f'Error in simulation: {str(e)}')
                finally:
                    default_storage.delete(temp_fasta_path)
            else:
                print("Simulation form is invalid")
                print("Form errors:", simulation_form.errors)
        else:
            print("Data input form submitted")
            form = DataInputForm(request.POST, request.FILES)
            if form.is_valid():
                fasta_file = form.cleaned_data['fasta_file']
                excel_file = form.cleaned_data['excel_file']
                protease = form.cleaned_data['protease']
                protein_name = form.cleaned_data['protein_name']

                temp_fasta_path = default_storage.save('temp_fasta.fasta', ContentFile(fasta_file.read()))
                temp_excel_path = default_storage.save('temp_excel.xlsx', ContentFile(excel_file.read()))

                temp_fasta_full_path = os.path.join(settings.MEDIA_ROOT, temp_fasta_path)
                temp_excel_full_path = os.path.join(settings.MEDIA_ROOT, temp_excel_path)

                try:
                    exp.update_table(temp_fasta_full_path, temp_excel_full_path, protease, protein_name)
                    messages.success(request, 'Files processed successfully.')

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

    context = {
        'form': form,
        'simulation_form': simulation_form,
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