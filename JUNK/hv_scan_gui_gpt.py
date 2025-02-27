import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# GUI Setup
class PlotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Plot Generator")

        # Date and time selection
        ttk.Label(root, text="Start Date & Time:").grid(row=0, column=0)
        self.start_cal = Calendar(root, selectmode='day', date_pattern='yyyy-mm-dd')
        self.start_cal.grid(row=0, column=1)
        self.start_time = ttk.Entry(root)
        self.start_time.grid(row=0, column=2)
        self.start_time.insert(0, "17:30:00")

        ttk.Label(root, text="End Date & Time:").grid(row=1, column=0)
        self.end_cal = Calendar(root, selectmode='day', date_pattern='yyyy-mm-dd')
        self.end_cal.grid(row=1, column=1)
        self.end_time = ttk.Entry(root)
        self.end_time.grid(row=1, column=2)
        self.end_time.insert(0, "00:10:00")

        # Options
        self.reduced_field_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(root, text="Use Reduced Field", variable=self.reduced_field_var).grid(row=2, column=1)

        self.plot_vs_time_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(root, text="Plot vs Time", variable=self.plot_vs_time_var).grid(row=3, column=1)

        # Generate Button
        self.generate_button = ttk.Button(root, text="Generate Plot", command=self.generate_plot)
        self.generate_button.grid(row=4, column=1)

    def generate_plot(self):
        start_date_str = self.start_cal.get_date() + " " + self.start_time.get()
        end_date_str = self.end_cal.get_date() + " " + self.end_time.get()

        start_date = pd.to_datetime(start_date_str, format='%Y-%m-%d %H:%M:%S')
        end_date = pd.to_datetime(end_date_str, format='%Y-%m-%d %H:%M:%S')

        reduced_field = self.reduced_field_var.get()
        plot_vs_time = self.plot_vs_time_var.get()

        # Read CSV file
        filepath = "large_corrected_table.csv"
        data_df = pd.read_csv(filepath)
        data_df['Time'] = pd.to_datetime(data_df['Time'].str.strip('"'), format='%Y-%m-%d %H:%M:%S')
        data_df = data_df[(data_df['Time'] >= start_date) & (data_df['Time'] <= end_date)]

        numeric_cols = [
            'streamer_percent_1', 'streamer_percent_2', 'streamer_percent_3', 'streamer_percent_4', 
            'eff_global', 'unc_eff_global', 'count', 'pressure_lab', 'sensors_int_Temperature_int',
            'final_eff_1', 'final_eff_2', 'final_eff_3', 'final_eff_4', 'CRT_avg_mean'
        ]

        data_df["t_in_K"] = data_df["sensors_int_Temperature_int"] + 273.15
        data_df["p_in_Pa"] = data_df["pressure_lab"] * 1000

        if reduced_field:
            data_df["hv_reduced"] = data_df["hv_mean"] * data_df["t_in_K"] / data_df["p_in_Pa"]
            data_grouped = data_df.groupby('hv_reduced')[numeric_cols].mean()
            label_hv = "$HV \cdot T / P$"
            units_hv = "$(kV \cdot K / Pa)$"
        else:
            data_grouped = data_df.groupby('hv_mean')[numeric_cols].mean()
            label_hv = "HV"
            units_hv = "(kV)"

        hv = data_grouped.index
        efficiency_M1 = data_grouped.get('final_eff_1', None)
        efficiency_M2 = data_grouped.get('final_eff_2', None)
        efficiency_M3 = data_grouped.get('final_eff_3', None)
        efficiency_M4 = data_grouped.get('final_eff_4', None)

        # Create plots
        fig, axs = plt.subplots(4, 1, figsize=(10, 12), sharex=True)

        # Plot Efficiency
        axs[0].set_ylabel('Efficiency')
        if efficiency_M1 is not None:
            axs[0].plot(hv, efficiency_M1, label='Efficiency P1', color='blue')
        if efficiency_M2 is not None:
            axs[0].plot(hv, efficiency_M2, label='Efficiency P2', color='orange')
        if efficiency_M3 is not None:
            axs[0].plot(hv, efficiency_M3, label='Efficiency P3', color='green')
        if efficiency_M4 is not None:
            axs[0].plot(hv, efficiency_M4, label='Efficiency P4', color='red')
        axs[0].legend()
        axs[0].set_ylim(0,1)
        axs[0].grid(True)
        axs[0].set_title(f'Efficiency of Each Plane vs {label_hv}')

        # Plot Pressure and Temperature
        axs[1].set_ylabel('Pressure (Lab)', color='tab:orange')
        axs[1].plot(hv, data_grouped['pressure_lab'], label='Pressure', color='orange')
        axs[1].tick_params(axis='y', labelcolor='tab:orange')
        ax_temp = axs[1].twinx()
        ax_temp.set_ylabel('Temperature (Lab)', color='tab:red')
        ax_temp.plot(hv, data_grouped['sensors_int_Temperature_int'], label='Temperature', color='red')
        ax_temp.tick_params(axis='y', labelcolor='tab:red')
        axs[1].grid(True)
        axs[1].set_title(f'Pressure and Temperature vs {label_hv}')

        # Plot CRT
        axs[2].plot(hv, data_grouped['CRT_avg_mean'] * 1000, label='CRT', color='purple')
        axs[2].set_ylabel('CRT (ps)')
        axs[2].grid(True)
        axs[2].legend()
        axs[2].set_title(f'CRT (ps) vs {label_hv}')

        axs[-1].set_xlabel(f'{label_hv} {units_hv}')
        axs[-1].set_xlim(hv.min(), hv.max())

        plt.tight_layout()
        plt.show()

# Run the GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = PlotGUI(root)
    root.mainloop()
