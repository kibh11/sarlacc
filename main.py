from setup import plt, sns, SeqIO, tk, ttk, filedialog
import utils as util
import simulation as sim
import experimental as exp

def open_fasta_file():
    global fasta_file
    fasta_file = filedialog.askopenfilename(title="Select FASTA file", filetypes=[("FASTA files", "*.fasta")], parent=root)
    if fasta_file:
        print(f"Selected FASTA file: {fasta_file}")
        fasta_status.set("FASTA File Uploaded")

def open_excel_file():
    global excel_file
    excel_file = filedialog.askopenfilename(title="Select Excel file", filetypes=[("Excel files", "*.xlsx")], parent=root)
    if excel_file:
        print(f"Selected Excel file: {excel_file}")
        excel_status.set("Excel File Uploaded")

def process_files():
    if fasta_file and excel_file and protease.get():
        print("Both files have been selected, and the protease has been selected.")

        exp.update_table(fasta_file, excel_file, protease.get())

        print(sim.load_protease(protease.get()))

        peptides = sim.digest(fasta_file, protease.get(), 1000)

        peptide_counts = {}
        for peptide in peptides:
            peptide_counts[peptide] = peptide_counts.get(peptide, 0) + 1

        sorted_peptide_counts = dict(sorted(peptide_counts.items(), key=lambda item: item[1], reverse=True))

        top_10_peptides = list(sorted_peptide_counts.keys())[:10]

        print("Top 10 simulated peptides:")
        for peptide in top_10_peptides:
            print(peptide)
    else:
        print("Please select both FASTA and Excel files.")

root = tk.Tk()
root.title("File Upload")
root.geometry("300x300")

fasta_file = None
excel_file = None

open_fasta_button = tk.Button(root, text="Open FASTA File", command=open_fasta_file)
open_fasta_button.pack(pady=10)

fasta_status = tk.StringVar()
fasta_status_label = ttk.Label(root, textvariable=fasta_status)
fasta_status_label.pack(pady=(0, 10))

open_excel_button = tk.Button(root, text="Open Experimental Results", command=open_excel_file)
open_excel_button.pack(pady=10)

excel_status = tk.StringVar()
excel_status_label = ttk.Label(root, textvariable=excel_status)
excel_status_label.pack(pady=(0, 10))

proteases = ["pepsin", "trypsin", "chymotrypsin", "proteinase K"]

protease_label = ttk.Label(root, text="Select a protease:")
protease_label.pack(pady=(10, 0))

protease = tk.StringVar()
protease_dropdown = ttk.Combobox(root, textvariable=protease, values=proteases, state="readonly")
protease_dropdown.pack(pady=10)


process_button = tk.Button(root, text="Process Files", command=process_files)
process_button.pack(pady=10)

root.mainloop()


