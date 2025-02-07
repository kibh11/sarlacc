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
    return df.sort_values('Count', ascending=False).head(100), peptides_dict

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

def is_close_match(seq1, seq2):
    # Convert Seq objects to strings if necessary
    seq1 = str(seq1) if isinstance(seq1, Seq) else seq1
    seq2 = str(seq2) if isinstance(seq2, Seq) else seq2

    if seq1 == seq2:
        return False  # This is an exact match, not a close match

    # Check if the length difference is exactly 1
    if abs(len(seq1) - len(seq2)) != 1:
        return False

    # Check if one sequence is a substring of the other with exactly one extra amino acid
    if len(seq1) < len(seq2):
        return seq2.startswith(seq1) or seq2.endswith(seq1)
    else:
        return seq1.startswith(seq2) or seq1.endswith(seq2)

def is_partial_match(seq1, seq2):
    # Convert Seq objects to strings if necessary
    seq1 = str(seq1) if isinstance(seq1, Seq) else seq1
    seq2 = str(seq2) if isinstance(seq2, Seq) else seq2

    if seq1 == seq2:
        return False  # This is an exact match, not a partial match

    # Check if the length difference is exactly 2
    if abs(len(seq1) - len(seq2)) != 2:
        return False

    # Check for the three cases of partial matches
    if len(seq1) < len(seq2):
        return seq2[2:] == seq1 or seq2[:-2] == seq1 or (seq2[1:-1] == seq1)
    else:
        return seq1[2:] == seq2 or seq1[:-2] == seq2 or (seq1[1:-1] == seq2)

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
        if pd.notna(row.get('Count', pd.NA)):  # exact match
            return 'exact', None, row.get('Count')

        # Check for close and partial matches
        for _, sim_row in simulation_df.iterrows():
            sim_peptide = sim_row['Peptide']
            sim_count = sim_row['Count']

            if is_close_match(row['Peptide'], sim_peptide):
                return 'close', sim_peptide, sim_count
            if is_partial_match(row['Peptide'], sim_peptide):
                return 'partial', sim_peptide, sim_count

        return 'none', None, None

    # Unpack three values now instead of two
    merged_df['Match'], merged_df['Sim_Peptide'], merged_df['Matched_Count'] = zip(*merged_df.apply(match_type, axis=1))

    # Count the occurrences of each match type
    match_counts = merged_df['Match'].value_counts()
    total_count = len(merged_df)

    # Calculate percentages
    match_percentages = (match_counts / total_count * 100).round(2)

    # Create the percentage bar HTML with fixed order
    bar_html = '<div style="width:100%; height:30px; display:flex; margin-bottom:10px;">'
    colors = {'exact': 'lightgreen', 'close': 'yellow', 'partial': '#ff8209', 'none': 'lightcoral'}

    # Fixed order of match types
    ordered_match_types = ['none', 'partial', 'close', 'exact']

    for match_type in ordered_match_types:
        if match_type in match_percentages:
            percentage = match_percentages[match_type]
            count = match_counts[match_type]
        else:
            percentage = 0
            count = 0
        bar_html += f'<div style="width:{percentage}%; height:100%; background-color:{colors[match_type]}; display:flex; align-items:center; justify-content:center; font-size:12px;">{percentage}% ({count})</div>'
    bar_html += '</div>'

    # Generate HTML table with color coding
    html_table = '<style>\n'
    html_table += 'table.comparison-table { font-size: 14px; border-collapse: collapse; width: 100%; }\n'  # Added font-size and table styling
    html_table += 'table.comparison-table th, table.comparison-table td { padding: 5px; border: 1px solid #ddd; }\n'  # Added padding
    html_table += 'table.comparison-table th { background-color: #f5f5f5; font-weight: bold; }\n'
    html_table += '</style>\n'

    html_table += '<table border="1" class="comparison-table">\n'
    html_table += '<thead><tr>'
    for col in merged_df.columns:
        if col != 'Sim_Peptide' and col != 'Matched_Count':  # Don't add separate columns for these
            if col == 'Peptide':
                html_table += f'<th>Peptide (Simulated)</th>'
            elif col == 'Count':
                html_table += '<th>Simulation Count</th>'
            else:
                html_table += f'<th>{col}</th>'
    html_table += '</tr></thead>\n'
    html_table += '<tbody>\n'

    for _, row in merged_df.iterrows():
        if row['Match'] == 'exact':
            bg_color = 'lightgreen'
        elif row['Match'] == 'close':
            bg_color = 'yellow'
        elif row['Match'] == 'partial':
            bg_color = '#ff8209'
        else:
            bg_color = 'lightcoral'

        html_table += f'<tr style="background-color: {bg_color};">'
        for col in merged_df.columns:
            if col == 'Peptide':
                peptide_text = row[col]
                if row['Match'] in ['close', 'partial']:
                    peptide_text += f" ({row['Sim_Peptide']})"
                html_table += f'<td>{peptide_text}</td>'
            elif col == 'Count':
                # Use Matched_Count for close/partial matches, otherwise use regular Count
                count_value = row['Matched_Count'] if (row['Match'] in ['close', 'partial']) else row[col]
                html_table += f'<td>{count_value}</td>'
            elif col not in ['Sim_Peptide', 'Matched_Count']:  # Don't show these helper columns
                html_table += f'<td>{row[col]}</td>'
        html_table += '</tr>\n'

    html_table += '</tbody></table>'

    # Combine the percentage bar and the table
    full_html = bar_html + html_table

    return full_html