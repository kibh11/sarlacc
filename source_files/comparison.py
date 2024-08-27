import pandas as pd
from Bio.Seq import Seq
import os
import sys

current_dir = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.join(current_dir, '..')))

from source_files.simulation import digest

def simulate_digestion(fasta_file, protease, n=999):
    peptides_dict = digest(fasta_file, protease, n=n)
    df = pd.DataFrame([(str(pep), count) for pep, (_, _, count) in peptides_dict.items()],
                      columns=['Peptide', 'Count'])
    return df.sort_values('Count', ascending=False).head(100)

def process_experimental_data(excel_file):
    df = pd.read_excel(excel_file)

    # Ensure the DataFrame has at least 3 columns
    if df.shape[1] < 3:
        raise ValueError("Excel file must contain at least 3 columns: Sequence, Start, and End")

    # Assume the first three columns are Sequence, Start, and End, respectively
    df_processed = df.iloc[:, :3]
    df_processed.columns = ['Peptide', 'Start', 'End']

    # Ensure Start and End are integers
    df_processed['Start'] = df_processed['Start'].astype(int)
    df_processed['End'] = df_processed['End'].astype(int)

    return df_processed[['Start', 'End', 'Peptide']]

def is_partial_match(seq1, seq2):
    # Convert Seq objects to strings if necessary
    seq1 = str(seq1) if isinstance(seq1, Seq) else seq1
    seq2 = str(seq2) if isinstance(seq2, Seq) else seq2

    if seq1 == seq2:
        return False  # This is an exact match, not a partial match

    # Check if the length difference is at most 1
    if abs(len(seq1) - len(seq2)) > 1:
        return False

    # Check if one sequence is a substring of the other with at most one extra amino acid
    if len(seq1) < len(seq2):
        return seq2.startswith(seq1) or seq2.endswith(seq1)
    else:
        return seq1.startswith(seq2) or seq1.endswith(seq2)

def compare_results(experimental_df, simulation_df):
    # Ensure experimental DataFrame has the necessary columns
    required_exp_columns = ['Peptide', 'Start', 'End']
    missing_columns = set(required_exp_columns) - set(experimental_df.columns)
    if missing_columns:
        raise ValueError(f"Experimental data is missing required columns: {', '.join(missing_columns)}")

    # Ensure simulation DataFrame has the Peptide column
    if 'Peptide' not in simulation_df.columns:
        raise ValueError("Simulation data is missing the required 'Peptide' column")

    # Convert Seq objects to strings in both DataFrames
    experimental_df['Peptide'] = experimental_df['Peptide'].apply(lambda x: str(x) if isinstance(x, Seq) else x)
    simulation_df['Peptide'] = simulation_df['Peptide'].apply(lambda x: str(x) if isinstance(x, Seq) else x)

    merged_df = experimental_df.merge(simulation_df, on='Peptide', how='left', suffixes=('_exp', '_sim'))

    def match_type(row):
        if pd.notna(row.get('Count', pd.NA)):  # 'Count' column from simulation data
            return 'exact', None
        for sim_peptide in simulation_df['Peptide']:
            if is_partial_match(row['Peptide'], sim_peptide):
                return 'partial', sim_peptide
        return 'none', None

    merged_df['Match'], merged_df['Sim_Peptide'] = zip(*merged_df.apply(match_type, axis=1))

    # Generate HTML table with color coding
    html_table = '<table border="1" class="dataframe">\n'
    html_table += '<thead><tr>'
    for col in merged_df.columns:
        if col != 'Sim_Peptide':  # Don't add a separate column for Sim_Peptide
            if col == 'Peptide':
                html_table += f'<th>{col} (simulated)</th>'
            else:
                html_table += f'<th>{col}</th>'
    html_table += '</tr></thead>\n'
    html_table += '<tbody>\n'

    for _, row in merged_df.iterrows():
        if row['Match'] == 'exact':
            bg_color = 'lightgreen'
        elif row['Match'] == 'partial':
            bg_color = 'yellow'
        else:
            bg_color = 'lightcoral'

        html_table += f'<tr style="background-color: {bg_color};">'
        for col in merged_df.columns:
            if col == 'Peptide':
                peptide_text = row[col]
                if row['Match'] == 'partial':
                    peptide_text += f" ({row['Sim_Peptide']})"  # Single parentheses added here
                html_table += f'<td>{peptide_text}</td>'
            elif col != 'Sim_Peptide':  # Don't add a separate column for Sim_Peptide
                html_table += f'<td>{row[col]}</td>'
        html_table += '</tr>\n'

    html_table += '</tbody></table>'

    return html_table