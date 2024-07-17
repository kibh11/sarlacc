import source_files.utilities as utils
import pandas as pd
import os
from datetime import datetime
import shutil


def retrieve_peptides(excel_file):
    df = pd.read_excel(excel_file, engine='openpyxl')
    filtered_df = df.loc[(df.iloc[:, 1].notna()) & (df.iloc[:, 2].notna()), :]
    return filtered_df


def update_table(fasta_file, excel_file, protease, protein_name):
    sequence = utils.fasta_sequence(fasta_file)

    protease_sheet = utils.protease_file(protease)

    peptides_df = retrieve_peptides(excel_file)
    peptides = peptides_df.iloc[:, 0].tolist()
    start_indices = [int(idx) for idx in peptides_df.iloc[:, 1].tolist()]
    end_indices = [int(idx) for idx in peptides_df.iloc[:, 2].tolist()]

    with (pd.ExcelFile(protease_sheet) as xls):
        totals_table = pd.read_excel(xls, sheet_name='totals', index_col=0)
        cleavage_table = pd.read_excel(xls, sheet_name='cleavages', index_col=0)

        for i in range(len(sequence) - 1):
            p1 = sequence[i]
            p1p = sequence[i + 1]
            p1_start = i + 1
            p1p_end = i + 2
            for j, peptide in enumerate(peptides):
                start_index = start_indices[j]
                end_index = end_indices[j]
                if start_index == p1p_end or end_index == p1_start:
                    cleavage_table.at[p1p, p1] += 1
                    totals_table.at[p1p, p1] += 1
                elif start_index <= p1_start and end_index >= p1p_end:
                    totals_table.at[p1p, p1] += 1

    with pd.ExcelWriter(protease_sheet, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        totals_table.to_excel(writer, sheet_name='totals')
        cleavage_table.to_excel(writer, sheet_name='cleavages')

    current_dir = os.path.dirname(protease_sheet)

    dest_dir = os.path.join(current_dir, "history")
    os.makedirs(dest_dir, exist_ok=True)

    history_files = sorted(os.listdir(dest_dir))

    max_aa_count = 0
    for file in history_files:
        try:
            aa_count = int(file.split("_")[0])
            if aa_count > max_aa_count:
                max_aa_count = aa_count
        except ValueError:
            continue

    new_aa_count = max_aa_count + len(sequence)

    now = datetime.now()
    new_file_name = f"{new_aa_count}_{protease}_{protein_name}_{now.strftime('%Y%m%d_%H%M%S')}.xlsx"
    dest_file_path = os.path.join(dest_dir, new_file_name)

    shutil.copy(protease_sheet, dest_file_path)
