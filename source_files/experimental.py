import pandas as pd
import os
from datetime import datetime
import shutil
import sys
import re
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

current_dir = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.join(current_dir, '..')))

import source_files.utilities as utils

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

def natural_sort_key(s):
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', s)]

def load_protease(path_name):
    cleavage_table = pd.read_excel(path_name, sheet_name=['cleavages', 'totals'], index_col=0)

    cleavages = cleavage_table['cleavages']
    totals = cleavage_table['totals']

    cleavages = cleavages.astype(float)
    totals = totals.astype(float)

    table = cleavages.div(totals)

    table = table.fillna(0)

    return table

def global_heatmap(protease, selected_layer=None):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    directory = os.path.join(parent_dir, 'resources', 'data', protease, 'history')

    if not os.path.exists(directory):
        raise FileNotFoundError(f"The directory {directory} does not exist.")

    excel_files = sorted([f for f in os.listdir(directory) if f.endswith('.xlsx') or f.endswith('.xls')],
                         key=natural_sort_key, reverse=True)

    if not excel_files:
        raise FileNotFoundError(f"No Excel files found in {directory}")

    dfs = []

    for file in excel_files:
        file_path = os.path.join(directory, file)
        try:
            prob_table = load_protease(file_path)
            dfs.append(prob_table)
        except Exception as e:
            print(f"Error processing file {file}: {str(e)}")

    df_3d = pd.concat(dfs, keys=excel_files, names=['file', 'row_index'])

    fig, ax = plt.subplots(figsize=(12, 10))
    plt.subplots_adjust(bottom=0.2)

    if selected_layer and selected_layer in excel_files:
        heatmap_data = df_3d.xs(selected_layer, level='file')
        title = f"Heatmap of {selected_layer}"
    else:
        selected_layer = excel_files[0]  # Default to the most recent layer
        heatmap_data = df_3d.xs(selected_layer, level='file')
        title = f"Heatmap of {selected_layer} (current)"

    sns.heatmap(heatmap_data, annot=True, cmap="viridis", ax=ax, cbar=False)
    ax.xaxis.set_ticks_position('top')
    ax.xaxis.set_label_position('top')
    ax.set_xlabel("Amino Acids", labelpad=20)
    ax.set_ylabel("Amino Acids")
    ax.set_title(title, pad=40)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)

    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')

    plt.close(fig)
    plt.close('all')

    return image_base64, excel_files