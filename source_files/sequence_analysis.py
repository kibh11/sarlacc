import random as rn
import math
import sys
import os
from typing import List, Dict, Tuple, Union
from Bio.Seq import Seq

current_dir = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.join(current_dir, '..')))

import source_files.utilities as utils

def calculate_resolutions(sequence: str, peptides_dict: Dict[Union[str, Seq], Tuple[int, int, int]]) -> List[int]:
    """
    Calculate resolution values for each position in a sequence based on overlapping peptides.

    Args:
        sequence (str): The amino acid sequence (can be string or Bio.Seq)
        peptides_dict (Dict[Union[str, Seq], Tuple[int, int, int]]): Dictionary of peptides with their positions and counts
            Format: {peptide: (start_position, end_position, count)}

    Returns:
        List[int]: Resolution values for each position in the sequence
    """
    resolutions = [float('inf')] * len(sequence)
    # Convert dictionary to list format and ignore the count
    peptides_data = [(peptide, start, end) for peptide, (start, end, count) in peptides_dict.items()]

    def update_resolutions(start, end, length):
        for i in range(start - 1, end):
            resolutions[i] = min(resolutions[i], length)

    def add_peptide(peptide, start, end):
        if (peptide, start, end) not in peptides_data:
            peptides_data.append((peptide, start, end))
            return True
        return False

    # Initial update of resolutions based on input peptides
    for peptide, start, end in peptides_data:
        update_resolutions(start, end, end - start + 1)

    while True:
        new_peptide_added = False
        peptides_data.sort(key=lambda x: x[2] - x[1] + 1)

        for i, (peptide1, start1, end1) in enumerate(peptides_data):
            length1 = end1 - start1 + 1

            for peptide2, start2, end2 in peptides_data[i+1:]:
                length2 = end2 - start2 + 1
                # Case 1: Peptide2 starts at the same position as Peptide1 and ends after
                if start1 == start2 and end1 < end2:
                    update_resolutions(start1, end1, length1)
                    update_resolutions(end1 + 1, end2, length2 - length1)
                    new_peptide = sequence[end1:end2]
                    if add_peptide(new_peptide, end1 + 1, end2):
                        new_peptide_added = True

                # Case 2: Peptide2 ends at the same position as Peptide1 and starts before
                elif end1 == end2 and start1 > start2:
                    update_resolutions(start1, end1, length1)
                    update_resolutions(start2, start1 - 1, length2 - length1)
                    new_peptide = sequence[start2-1:start1-1]
                    if add_peptide(new_peptide, start2, start1 - 1):
                        new_peptide_added = True

        if not new_peptide_added:
            break

    return resolutions

def visualize_sequence_coverage(sequence: str, peptides_dict: Dict[Union[str, Seq], Tuple[int, int, int]], line_length: int = 50) -> str:
    """Visualizes sequence with resolution values in a linear format."""
    html = ['<div style="font-family: monospace; font-size: 16px;">']
    html.append('<style>')
    html.append('''
        .sequence-block {
            display: grid;
            grid-template-columns: repeat(50, 1fr);
            gap: 0.1em;
            margin-bottom: 2em;
        }
        .position-unit {
            text-align: center;
            display: inline-block;
        }
        .position-number {
            font-size: 10px;
            color: #888888;
        }
        .resolution-value {
            font-size: 10px;
            vertical-align: super;
        }
    ''')
    html.append('</style>')

    resolutions = calculate_resolutions(sequence, peptides_dict)

    for i in range(0, len(sequence), line_length):
        html.append('<div class="sequence-block">')
        chunk = sequence[i:i + line_length]
        chunk_res = resolutions[i:i + line_length]

        for j in range(line_length):
            if j < len(chunk):
                aa = chunk[j]
                res = chunk_res[j]
                pos = i + j + 1
                res_display = '∞' if res == float('inf') else res
                html.append(f'''
                    <div class="position-unit">
                        <div class="position-number">{pos}</div>
                        {aa}<sup class="resolution-value">{res_display}</sup>
                    </div>
                ''')
            else:
                html.append('<div class="position-unit"></div>')


        html.append('</div>')

    html.append('</div>')

    return '\n'.join(html)