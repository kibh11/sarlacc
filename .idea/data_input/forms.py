# data_input/forms.py
from django import forms

class DataInputForm(forms.Form):
    fasta_file = forms.FileField(label='FASTA File')
    excel_file = forms.FileField(label='Excel File')
    protease = forms.ChoiceField(choices=[('pepsin', 'Pepsin')], label='Select a protease')
    protein_name = forms.CharField(max_length=100, label='Protein Name')

class LayerSelectForm(forms.Form):
    layer = forms.ChoiceField(label='Select Excel File', required=False)

    def __init__(self, *args, **kwargs):
        excel_files = kwargs.pop('excel_files', [])
        super().__init__(*args, **kwargs)
        self.fields['layer'].choices = [(f, f"{f} (current)" if i == 0 else f) for i, f in enumerate(excel_files)]