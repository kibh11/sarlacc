import os
import pandas as pd
import seaborn as sns
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import tkinter as tk
from tkinter import ttk

# Replace with the actual directory path containing the Excel files
directory = 'utility/data/pepsin/history'


def read_excel_sheet(file_path):
    data = pd.read_excel(file_path, sheet_name='probs', header=0, index_col=0)
    data = data.rename_axis("Amino Acids", axis=1).rename_axis("Amino Acids")
    data = data.fillna(0)  # Replace NaN values with 0
    return data

# List of Excel file paths in sorted order
file_paths = sorted([os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.xlsx')])

# Create the main window
root = tk.Tk()
root.title("Heatmap Viewer")

# Create a figure and a canvas to display the plot
fig = Figure(figsize=(10, 8))
ax = fig.add_subplot(111)
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

# Create a slider
slider = ttk.Scale(root, from_=0, to=len(file_paths)-1, value=0, orient=tk.HORIZONTAL, command=lambda x: update_heatmap(int(slider.get())))
slider.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

# Function to update the heatmap
def update_heatmap(file_index):
    file_path = file_paths[file_index]
    data = read_excel_sheet(file_path)

    # Clear the previous plot
    ax.clear()

    # Create the new heatmap
    sns.heatmap(data, annot=False, cmap='YlGnBu', ax=ax)

    # Remove the legend if it exists
    legend = ax.get_legend()
    if legend is not None:
        legend.remove()

    ax.set_title(os.path.basename(file_path))

    # Redraw the canvas
    canvas.draw()
# Start the GUI main loop
root.mainloop()