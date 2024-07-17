import re
import pandas as pd
import os
import tkinter as tk
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.widgets import Slider
from tkinter import ttk


def natural_sort_key(s):
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', s)]


def load_protease(path_name):
    cleavage_table = pd.read_excel(path_name, sheet_name=['cleavages', 'totals'], index_col=0)

    cleavages = cleavage_table['cleavages']
    totals = cleavage_table['totals']

    cleavages = cleavages.astype(float)
    totals = totals.astype(float)

    table = cleavages.div(totals)

    table = table.fillna(0)

    return table


directory = 'utility/data/pepsin/history'

excel_files = sorted([f for f in os.listdir(directory) if f.endswith('.xlsx') or f.endswith('.xls')],
                     key=natural_sort_key)

dfs = []

for file in excel_files:
    file_path = os.path.join(directory, file)

    try:
        prob_table = load_protease(file_path)
        dfs.append(prob_table)
    except Exception as e:
        print(f"Error processing file {file}: {str(e)}")

df_3d = pd.concat(dfs, keys=excel_files, names=['file', 'row_index'])


def show_heatmap_with_slider():
    window = tk.Tk()
    window.title("Heatmap Viewer")

    fig, ax = plt.subplots(figsize=(10, 8))
    plt.subplots_adjust(bottom=0.2)

    def on_closing():
        window.destroy()
        window.quit()

    window.protocol("WM_DELETE_WINDOW", on_closing)

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

    initial_file = df_3d.index.levels[0][0]
    df_2d = df_3d.xs(initial_file, level='file')
    sns.heatmap(df_2d, annot=True, cmap="viridis", ax=ax, cbar=False)
    ax.xaxis.set_ticks_position('top')
    ax.xaxis.set_label_position('top')
    ax.set_xlabel("Amino Acids", labelpad=20)
    ax.set_ylabel("Amino Acids")
    ax.set_title(f"Heatmap of Layer ({initial_file})", pad=40)

    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    ax_slider = plt.axes([0.2, 0.05, 0.6, 0.03], facecolor='lightgoldenrodyellow')
    slider = Slider(ax_slider, 'Layer', 0, len(df_3d.index.levels[0]) - 1, valinit=0, valfmt='%0.0f')

    slider.on_changed(update)

    quit_button = ttk.Button(window, text="Quit", command=window.destroy)
    quit_button.pack(side=tk.BOTTOM)

    window.mainloop()


show_heatmap_with_slider()
