from setup import pd, rn, np, Path, SeqIO, opxl, mp, partial
import utils as util

def incr_occurences(fasta_file, protease):
    sequence = util.fasta_sequence(fasta_file)

    protease_sheet = util.protease_file(protease)

    with pd.ExcelFile(protease_file) as xls:
        totals_table = pd.read_excel(xls, sheet_name='totals', index_col=0)
        for j in range(len(protein_seq) - 2):
            p1 = sequence[j]
            p1p = sequence[j+1]
            totals_table.at[p1, p1p] += 1
        totals_table.to_excel(protease_sheet, sheet_name='totals')

def retrieve_fragments(excel_file):
    df = pd.read_excel(excel_file, engine='openpyxl')
    filtered_df = df.loc[(df.iloc[:, 1].notna()) & (df.iloc[:, 2].notna()), :]
    return filtered_df

def incr_cleavage(fasta_file, excel_file, protease):
    sequence = util.fasta_sequence(fasta_file)

    protease_sheet = util.protease_file(protease)

    with pd.ExcelFile(protease_sheet) as xls:
        cleavage_table = pd.read_excel(xls, sheet_name='cleavages', index_col=0)

    print(cleavage_table)

    fragments_df = retrieve_fragments(excel_file)
    fragments = fragments_df.iloc[:, 0].tolist()
    start_indices = [int(idx) for idx in fragments_df.iloc[:, 1].tolist()]

    for i, fragment in enumerate(fragments):
        start_index = start_indices[i]
        if start_index > 1:
            p1_index = start_index - 2  # Adjusting for 0-based indexing in sequence
            p1p_index = start_index - 1  # Adjusting for 0-based indexing in sequence
            p1 = sequence[p1_index]
            p1p = sequence[p1p_index]
            cleavage_table.at[p1, p1p] += 1

    with pd.ExcelWriter(protease_sheet, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        cleavage_table.to_excel(writer, sheet_name='cleavages')