from setup import plt, sns
import simul, exper

fasta_file = "S100b.fasta"
fragments = simul.digest(fasta_file, n=1000)

# Print the distribution of the first two letters of each sequence
fragment_lengths = [len(fragment) for fragment in fragments]


fragment_counts = {}
for fragment in fragments:
    fragment_counts[fragment] = fragment_counts.get(fragment, 0) + 1

# Sort the dictionary by values (frequencies) in descending order
sorted_fragment_counts = dict(sorted(fragment_counts.items(), key=lambda item: item[1], reverse=True))

# Get the top 100 most common fragments
top_100_fragments = list(sorted_fragment_counts.keys())[:100]

# Print the list of top 100 fragments
print("Top 100 fragments:")
for fragment in top_100_fragments:
    print(fragment)

# plt.subplot(2, 1, 1)
# sns.violinplot(y=fragment_lengths, color='skyblue')
#
# # Add labels and title
# plt.xlabel('Density')
# plt.ylabel('Fragment Length')
# plt.title('Distribution of Fragment Lengths')
#
# # Show plot
# plt.show(block=True)
#
#
# filtered_fragments = [fragment for fragment in fragments if len(fragment) > 1]
#
# # Extract the first two letters of each sequence
# first_two_letters = [str(fragment)[:2] for fragment in filtered_fragments]
#
# # Count the frequency of each pair of letters
# letter_counts = {}
# for letters in first_two_letters:
#     letter_counts[letters] = letter_counts.get(letters, 0) + 1
#
# # Sort the dictionary by values (frequencies) in descending order
# sorted_letter_counts = dict(sorted(letter_counts.items(), key=lambda item: item[1], reverse=True))
#
# # Get the top 25 most common two-letter starts
# top_10_starts = list(sorted_letter_counts.items())[:10]
#
# # Extract letters and frequencies for the top 25 starts
# letters = [start[0] for start in top_10_starts]
# frequencies = [start[1] for start in top_10_starts]
#
# # Determine the number of bars
# num_bars = len(letters)
#
# # Set the width of each bar
# bar_width = 0.8
#
#
# # Create the bar plot (histogram) with adjusted bar width
# plt.subplot(2, 1, 2)
# plt.bar(letters, frequencies, width=bar_width, color='skyblue')
#
# # Add labels and title
# plt.xlabel('First Two Letters')
# plt.ylabel('Frequency')
# plt.title('Frequency of First Two Letters in Sequences (Top 10)')
#
# # Rotate x-axis labels for better visibility if needed
# plt.xticks(rotation=45)
#
# # Show plot
# plt.show(block=True)