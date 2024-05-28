from setup import plt, sns, SeqIO
import utils as util
import simulation as sim
import experimental as exp

fasta_file = "utility/testing/edited_S100b.fasta"
excel_file = "utility/testing/edited_20240129-PepsinDigestionformatted.xlsx"

fragments = sim.digest(fasta_file, n=1000)

fragment_counts = {}
for fragment in fragments:
    fragment_counts[fragment] = fragment_counts.get(fragment, 0) + 1

sorted_fragment_counts = dict(sorted(fragment_counts.items(), key=lambda item: item[1], reverse=True))

top_10_fragments = list(sorted_fragment_counts.keys())[:10]

print("Top 10 fragments:")
for fragment in top_10_fragments:
    print(fragment)

exp.update_table(fasta_file, excel_file, 'pepsin')

fragments = sim.digest(fasta_file, n=1000)

fragment_counts = {}
for fragment in fragments:
    fragment_counts[fragment] = fragment_counts.get(fragment, 0) + 1

sorted_fragment_counts = dict(sorted(fragment_counts.items(), key=lambda item: item[1], reverse=True))

top_10_fragments = list(sorted_fragment_counts.keys())[:10]

print("Top 10 fragments:")
for fragment in top_10_fragments:
    print(fragment)


