# data_input/forms.py
from django import forms

class DataInputForm(forms.Form):
    fasta_file = forms.FileField(label='FASTA File')
    excel_file = forms.FileField(label='Excel File')
    protease = forms.ChoiceField(choices=[('pepsin', 'Pepsin')], label='Select a protease')
    protein_name = forms.CharField(max_length=100, label='Protein Name')