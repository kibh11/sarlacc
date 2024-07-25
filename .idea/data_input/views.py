from django.shortcuts import render
from django.http import HttpResponse
import os
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib import messages
from .forms import DataInputForm
import sys

current_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))


source_files_dir = os.path.join(project_root, 'source_files')
sys.path.append(source_files_dir)

import experimental as exp
import simulation as sim

# Create your views here.
def data_input(request):
    if request.method == 'POST':
        form = DataInputForm(request.POST, request.FILES)
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
            except Exception as e:
                messages.error(request, f'Error processing files: {str(e)}')
            finally:
                # Clean up temporary files
                default_storage.delete(temp_fasta_path)
                default_storage.delete(temp_excel_path)
    else:
        form = DataInputForm()

    return render(request, 'data_input/data_input.html', {'form': form})