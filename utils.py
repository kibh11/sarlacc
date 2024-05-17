from setup import Path, SeqIO, pd

def fasta_sequence(fasta_file):
    with open(fasta_file, 'r') as file:
        protein_seq = SeqIO.read(file, 'fasta').seq
    return protein_seq

def protease_file(protease):
    protease_file = Path('utility/data') / protease / f'{protease}.xlsx'
    return protease_file

