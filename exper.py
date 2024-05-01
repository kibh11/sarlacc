from setup import pd, rn, np, Path, SeqIO, opxl, mp, partial

def incr_occurences(fasta_file, protease):
    protease_file = Path('data') / protease / f'{protease}.xlsx'

    with open(fasta_file, 'r') as file:
        protein_seq = SeqIO.read(file, 'fasta').seq

    with pd.ExcelFile(protease_file) as xls:
        totals_table = pd.read_excel(xls, sheet_name='totals', index_col=0)
        for j in range(len(protein_seq) - 2):
            p1 = protein_seq[j]
            p1p = protein_seq[j+1]
            totals_table.at[(p1, p1p), 'Count'] += 1
        totals_table.to_excel(protease_file, sheet_name='totals')



def incr_cleavage(p1, p1p, protease):
    protease_file = Path('data') / protease / f'{protease}.xlsx'

    with pd.ExcelFile(protease_file) as xls:
        cleavage_table = pd.read_excel(xls, sheet_name='cleavages', index_col=0)
        cleavage_table.at[(p1, p1p), 'Count'] += 1
        cleavage_table.to_excel(protease_file, sheet_name='cleavages')



def retreive_fragments(fasta_file, excel_file):
    df = pd.read_excel(excel_file, engine='openpyxl')
    fragments = df.iloc[:, 0].tolist()
    return fragments