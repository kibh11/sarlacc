from setup import pd, rn, np, Path, SeqIO, opxl, mp, partial
import utils as util

def retrieve_fragments(excel_file):
    df = pd.read_excel(excel_file, engine='openpyxl')
    filtered_df = df.loc[(df.iloc[:, 1].notna()) & (df.iloc[:, 2].notna()), :]
    return filtered_df

def update_table(fasta_file, excel_file, protease):
    sequence = util.fasta_sequence(fasta_file)

    protease_sheet = util.protease_file(protease)

    fragments_df = retrieve_fragments(excel_file)
    fragments = fragments_df.iloc[:, 0].tolist()
    start_indices = [int(idx) for idx in fragments_df.iloc[:, 1].tolist()]
    end_indices = [int(idx) for idx in fragments_df.iloc[:, 2].tolist()]

    print(sequence)
    print(fragments)
    print(start_indices)
    print(end_indices)

    with (pd.ExcelFile(protease_sheet) as xls):
        totals_table = pd.read_excel(xls, sheet_name='totals', index_col=0)
        cleavage_table = pd.read_excel(xls, sheet_name='cleavages', index_col=0)
        print("init actual: " + str(cleavage_table.at['W', 'W']))
        print("init occur: " + str(totals_table.at['W', 'W']))

        for i in range(len(sequence) - 1):
            p1 = sequence[i]
            p1p = sequence[i+1]
            p1_start = i + 1
            p1p_end = i + 2
            for j, fragment in enumerate(fragments):
                start_index = start_indices[j]
                end_index = end_indices[j]
                if start_index == p1p_end or end_index == p1_start:
                    cleavage_table.at[p1p, p1] += 1
                    totals_table.at[p1p, p1] += 1
                elif start_index <= p1_start and end_index >= p1p_end:
                    totals_table.at[p1p, p1] += 1

        print("final actual: " + str(cleavage_table.at['W', 'W']))
        print("final occur: " + str(totals_table.at['W', 'W']))

    with pd.ExcelWriter(protease_sheet, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        totals_table.to_excel(writer, sheet_name='totals')
        cleavage_table.to_excel(writer, sheet_name='cleavages')