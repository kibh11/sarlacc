# data_input/forms.py
from django import forms

class DataInputForm(forms.Form):
    fasta_file = forms.FileField(
        label='FASTA File',
        widget=forms.FileInput(attrs={'accept': '.fasta,.fa,.fna'}),
        required=True
    )
    excel_file = forms.FileField(
        label='Excel File',
        widget=forms.FileInput(attrs={'accept': '.xlsx,.xls'}),
        required=True
    )
    protease = forms.ChoiceField(
        choices=[('pepsin', 'Pepsin')],
        label='Select a protease',
        required=True
    )
    protein_name = forms.CharField(
        max_length=100,
        label='Protein Name',
        required=True
    )
