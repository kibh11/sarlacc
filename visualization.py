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
from matplotlib.widgets import Slider


def show_heatmap_with_slider():
    # Create a new Tkinter window
    window = tk.Tk()
    window.title("Heatmap Viewer")

    # Create a Matplotlib figure
    fig, ax = plt.subplots(figsize=(10, 8))
    plt.subplots_adjust(bottom=0.2)  # Adjust bottom to make room for the slider

    # Function to update the heatmap
    def update(val):
        layer_idx = int(slider.val)
        selected_file = df_3d.index.levels[0][layer_idx]
        df_2d = df_3d.xs(selected_file, level='file')
        ax.clear()
        sns.heatmap(df_2d, annot=True, cmap="viridis", ax=ax, cbar=False)
        ax.xaxis.set_ticks_position('top')
        ax.xaxis.set_label_position('top')
        ax.set_xlabel("Amino Acids", labelpad=20)
        ax.set_ylabel("Amino Acids")
        ax.set_title(f"Heatmap of Layer ({selected_file})", pad=40)
        canvas.draw()

    # Initial heatmap
    initial_file = df_3d.index.levels[0][0]
    df_2d = df_3d.xs(initial_file, level='file')
    sns.heatmap(df_2d, annot=True, cmap="viridis", ax=ax, cbar=False)
    ax.xaxis.set_ticks_position('top')
    ax.xaxis.set_label_position('top')
    ax.set_xlabel("Amino Acids", labelpad=20)
    ax.set_ylabel("Amino Acids")
    ax.set_title(f"Heatmap of Layer ({initial_file})", pad=40)

    # Create a Canvas to embed the Matplotlib figure
    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    # Create a Slider
    ax_slider = plt.axes([0.2, 0.05, 0.6, 0.03], facecolor='lightgoldenrodyellow')
    slider = Slider(ax_slider, 'Layer', 0, len(df_3d.index.levels[0]) - 1, valinit=0, valfmt='%0.0f')

    # Update the heatmap when the slider value changes
    slider.on_changed(update)

    # Create a Quit button
    quit_button = ttk.Button(window, text="Quit", command=window.destroy)
    quit_button.pack(side=tk.BOTTOM)

    # Start the Tkinter main loop
    window.mainloop()

# Call the function to show the heatmap with a slider
show_heatmap_with_slider()