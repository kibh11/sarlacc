import pandas as pd
import os
import numpy as np
import utils as util
import re

def natural_sort_key(s):
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', s)]

def load_protease(file_path):
    cleavage_table = pd.read_excel(file_path, sheet_name=['cleavages', 'totals'], index_col=0)

    cleavages = cleavage_table['cleavages']
    totals = cleavage_table['totals']

    cleavages = cleavages.astype(float)
    totals = totals.astype(float)

    prob_table = cleavages.div(totals)

    prob_table = prob_table.fillna(0)

    return prob_table

# Replace with the actual directory path containing the Excel files
directory = 'utility/data/pepsin/history'

# Sort files using natural sorting
excel_files = sorted([f for f in os.listdir(directory) if f.endswith('.xlsx') or f.endswith('.xls')],
                     key=natural_sort_key)

# Initialize an empty list to store DataFrames
dfs = []

# Process each Excel file
for file in excel_files:
    file_path = os.path.join(directory, file)

    # Load the protease data
    try:
        prob_table = load_protease(file_path)
        dfs.append(prob_table)
    except Exception as e:
        print(f"Error processing file {file}: {str(e)}")

# Create a 3D DataFrame
df_3d = pd.concat(dfs, keys=excel_files, names=['file', 'row_index'])

# Print all slices in order
# for i, file in enumerate(df_3d.index.levels[0]):
#     print(f"\nSlice {i}: Data for file: {file}")
#     print(df_3d.loc[file])
#     print("\n" + "="*50 + "\n")  # Separator between slices



import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import seaborn as sns


def show_heatmap():
    # Extract the second "slice" (file) from the MultiIndex DataFrame
    try:
        second_layer_file = df_3d.index.levels[0][1]  # Assuming the second layer corresponds to the second file
        df_2d = df_3d.xs(second_layer_file, level='file')
    except IndexError:
        print("Not enough files to extract the second layer.")
        return

    # Create a new Tkinter window
    window = tk.Tk()
    window.title("Heatmap of the Second Layer of df_3d")

    # Create a Matplotlib figure
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(df_2d, annot=True, cmap="viridis", ax=ax)

    ax.xaxis.set_ticks_position('top')
    ax.xaxis.set_label_position('top')

    # Create a Canvas to embed the Matplotlib figure
    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    # Create a Quit button
    quit_button = ttk.Button(window, text="Quit", command=window.destroy)
    quit_button.pack(side=tk.BOTTOM)

    # Start the Tkinter main loop
    window.mainloop()

# Call the function to show the heatmap
show_heatmap()