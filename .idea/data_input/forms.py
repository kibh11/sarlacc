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
        choices=[('pepsin', 'Pepsin'), ('nepenthesinii', 'Nepenthesin II')],
        label='Select a protease',
        required=True
    )
    protein_name = forms.CharField(
        max_length=100,
        label='Protein Name',
        required=True
    )
    compare_with_simulation = forms.BooleanField(
        label='Compare with simulation',
        required=False,
        initial=False
    )

class SimulationForm(forms.Form):
    simulation_fasta_file = forms.FileField(
        label='FASTA File',
        widget=forms.FileInput(attrs={'accept': '.fasta,.fa,.fna'}),
        required=True
    )
    simulation_protease = forms.ChoiceField(
        choices=[('pepsin', 'Pepsin'), ('nepenthesinii', 'Nepenthesin II')],
        label='Select a protease',
        required=True
    )
    simulation_runs = forms.IntegerField(
        label='Number of runs',
        min_value=1,
        max_value=100,
        initial=10,
        required=True,
        widget=forms.NumberInput(attrs={'type': 'number', 'min': '1', 'max': '999'})
    )