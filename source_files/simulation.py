import random as rn
import math
import sys
import os
import statistics
import pandas as pd
from tabulate import tabulate
from Bio.Seq import Seq

current_dir = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.join(current_dir, '..')))

import source_files.utilities as utils


def digest(fasta_file, protease='pepsin', exponent = 1, n=10):
    sequence = utils.fasta_sequence(fasta_file)

    cleavage_table = utils.load_protease(protease)

    peptides = []
    peptides_dict = {}
    for i in range(n):
        prev = 0
        for j in range(len(sequence) - 2):
            p1 = sequence[j]
            p1p = sequence[j + 1]
            prob = cleavage_table.loc[p1p, p1]
            if rn.random() < math.pow(prob, exponent) and j + 1 - prev >= 4:
                peptides.append(sequence[prev:j + 1])
                if sequence[prev:j + 1] in peptides_dict:
                    prev_count = peptides_dict[sequence[prev:j + 1]]
                    new_count = (prev_count[0], prev_count[1], prev_count[2] + 1)
                    peptides_dict[sequence[prev:j + 1]] = new_count
                else:
                    peptides_dict[sequence[prev:j + 1]] = (prev + 1, j + 1, 1)
                prev = j + 1

    return peptides_dict

def show_table(peptides_dict, n):
    table_data = []

    for peptide, (start, end, count) in peptides_dict.items():
        length = end - start + 1
        frequency = count / n

        if isinstance(peptide, Seq):
            clean_peptide = str(peptide)
        else:
            clean_peptide = peptide

        clean_peptide = ''.join(c for c in clean_peptide if c.isalpha())

        table_data.append([start, end, clean_peptide, length, count, f"{frequency*100:.2f}%"])

    df = pd.DataFrame(table_data, columns=['Start', 'End', 'Peptide', 'Length', 'Count', 'Frequency'])
    df = df.sort_values('Count', ascending=False)

    html_table = df.to_html(index=False, classes='table', border=0, escape=False)

    return html_table

# Usage example:
def simulate_and_show_table(fasta_file, protease='pepsin', exponent=1, n=10):
    peptides_dict = digest(fasta_file, protease, exponent, n)
    return show_table(peptides_dict, n)

