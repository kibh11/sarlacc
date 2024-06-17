from setup import pd, rn, np, Path, SeqIO, opxl, mp, partial
import utils as util

#load_protease uses the protease param to load an excel sheet containing two sheets, with one counting the number of experimentally observed cleavages, and the other containing the total number of potential cleavage sites observed, the function then returns the number of cleavages divided by the number of total occurences as a probability table




#digest reads in a fasta file, loads the probability table for cleavages between residues specific to the protease param, and then iterates through the sequence and uses the probabilities from the table to determine where "cleavages" happen, these peptides are added to the list, and the entire sequence is digested n times (given by param n, default 1000) and the list containing all the peptides is returned
def digest(fasta_file, protease='pepsin', n=1000):

    sequence = util.fasta_sequence(fasta_file)

    cleavage_table = util.load_protease(protease)

    peptides = []
    for i in range(n):
        prev = 0
        for j in range(len(sequence) - 2):
            p1 = sequence[j]
            p1p = sequence[j+1]
            prob = cleavage_table.loc[p1p, p1]
            if rn.random() < prob and j + 1 - prev >= 4 and rn.random() < 0.5:
                peptides.append(sequence[prev:j+1])
                prev = j + 1

    return peptides