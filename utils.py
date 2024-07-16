from setup import Path, SeqIO, pd


def fasta_sequence(fasta_file):
    with open(fasta_file, 'r') as file:
        protein_seq = SeqIO.read(file, 'fasta').seq
    return protein_seq


def protease_file(protease):
    protease_file = Path('utility/data') / protease / f'{protease}.xlsx'
    return protease_file


def load_protease(protease='pepsin'):
    protease_sheet = protease_file(protease)

    cleavage_table = pd.read_excel(protease_sheet, sheet_name=['cleavages', 'totals'], index_col=0)

    cleavages = cleavage_table['cleavages']
    totals = cleavage_table['totals']

    cleavages = cleavages.astype(float)
    totals = totals.astype(float)

    prob_table = cleavages.div(totals)

    prob_table = prob_table.fillna(0)

    return prob_table
