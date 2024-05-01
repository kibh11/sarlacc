from setup import plt, sns
import simul, exper

fasta_file = "utility/testing/S100b.fasta"
fragments = simul.digest(fasta_file, n=1000)


fragment_counts = {}
for fragment in fragments:
    fragment_counts[fragment] = fragment_counts.get(fragment, 0) + 1

sorted_fragment_counts = dict(sorted(fragment_counts.items(), key=lambda item: item[1], reverse=True))

top_100_fragments = list(sorted_fragment_counts.keys())[:100]

print("Top 100 fragments:")
for fragment in top_100_fragments:
    print(fragment)
