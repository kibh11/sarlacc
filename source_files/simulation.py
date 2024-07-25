import random as rn
import sys
import os


current_dir = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.join(current_dir, '..')))

import source_files.utilities as utils


def digest(fasta_file, protease='pepsin', n=1000):
    sequence = utils.fasta_sequence(fasta_file)

    cleavage_table = utils.load_protease(protease)

    peptides = []
    for i in range(n):
        prev = 0
        for j in range(len(sequence) - 2):
            p1 = sequence[j]
            p1p = sequence[j + 1]
            prob = cleavage_table.loc[p1p, p1]
            if rn.random() < prob and j + 1 - prev >= 4 and rn.random() < 0.5:
                peptides.append(sequence[prev:j + 1])
                prev = j + 1

    return peptides
