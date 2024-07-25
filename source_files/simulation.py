import random as rn
import math
import sys
import os
import statistics


current_dir = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.join(current_dir, '..')))

import source_files.utilities as utils


def digest(fasta_file, protease='pepsin', exponent = 6, n=1000):
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
                    peptides_dict[sequence[prev:j + 1]] = (prev + 1, j + 2, 1)
                prev = j + 1

    #test
    result_list = []

    for tuple_value in peptides_dict.values():
        if len(tuple_value) >= 2:
            calculation = (tuple_value[1] + 1) - tuple_value[0]
            result_list.append(calculation)

    return peptides_dict

def main():
    # Hardcoded example paths and parameters
    example_fasta_file = 'S100b.fasta'
    example_protease = 'pepsin'
    example_exponent = 5
    example_n = 1000

    # Call the digest function with hardcoded values
    peptides_dict = digest(example_fasta_file, protease=example_protease, exponent=example_exponent, n=example_n)
    print("Peptides Dictionary:")
    for peptide, (start, end, count) in peptides_dict.items():
        print(f"Peptide: {peptide}, Start: {start}, End: {end}, Count: {count}")


    total_length = 0
    total_count = 0

    for peptide, (start, end, count) in peptides_dict.items():
        length = end - start
        total_length += length * count
        total_count += count

    if total_count > 0:
        weighted_average_length = total_length / total_count
    else:
        weighted_average_length = 0

    print(f"Mean peptide length: {weighted_average_length}")

# Ensure the main function is called when the script is run
if __name__ == "__main__":
    main()