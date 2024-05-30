from setup import plt, sns, SeqIO
import utils as util
import simulation as sim
import experimental as exp

import tkinter as tk
from tkinter import filedialog


def open_fasta_file():
    global fasta_file
    fasta_file = filedialog.askopenfilename(title="Select FASTA file", filetypes=[("FASTA files", "*.fasta")], parent=root)
    if fasta_file:
        print(f"Selected FASTA file: {fasta_file}")

def open_excel_file():
    global excel_file
    excel_file = filedialog.askopenfilename(title="Select Excel file", filetypes=[("Excel files", "*.xlsx")], parent=root)
    if excel_file:
        print(f"Selected Excel file: {excel_file}")

def process_files():
    if fasta_file and excel_file:
        print("Both files have been selected.")
        
        exp.update_table(fasta_file, excel_file, 'pepsin')

        peptides = sim.digest(fasta_file, n=1000)

        peptide_counts = {}
        for peptide in peptides:
            peptide_counts[peptide] = peptide_counts.get(peptide, 0) + 1

        sorted_peptide_counts = dict(sorted(peptide_counts.items(), key=lambda item: item[1], reverse=True))

        top_10_peptides = list(sorted_peptide_counts.keys())[:10]

        print("Top 10 peptides:")
        for peptide in top_10_peptides:
            print(peptide)
        print("Processing files...")
    else:
        print("Please select both FASTA and Excel files.")

root = tk.Tk()
root.title("File Upload")

fasta_file = None
excel_file = None

open_fasta_button = tk.Button(root, text="Open FASTA File", command=open_fasta_file)
open_fasta_button.pack(pady=10)

open_excel_button = tk.Button(root, text="Open Excel File", command=open_excel_file)
open_excel_button.pack(pady=10)

process_button = tk.Button(root, text="Process Files", command=process_files)
process_button.pack(pady=10)

root.mainloop()


