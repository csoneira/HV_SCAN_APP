#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 19:02:22 2024

@author: gfn
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import argparse
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Header ----------------------------------------------------------------------
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Parse command-line arguments ------------------------------------------------
# -----------------------------------------------------------------------------
parse_cond = False
reduced_field = True

if parse_cond:
    # Create argument parser
    parser = argparse.ArgumentParser(description="Process start and end dates.")

    # Define command-line arguments
    parser.add_argument("--start_date", type=str, default="2025-02-25 17:30:00", help="Start date in 'YYYY-MM-DD HH:MM:SS' format")
    parser.add_argument("--end_date", type=str, default="2025-02-26 01:00:00", help="End date in 'YYYY-MM-DD HH:MM:SS' format")

    # Parse arguments
    args = parser.parse_args()

    # Assign variables
    start_date_str = args.start_date
    end_date_str = args.end_date
else:
    # Use default values
    start_date_str = "2025-02-25 17:30:00"
    end_date_str = "2025-02-26 00:10:00"

start_date = pd.to_datetime(start_date_str, format='%Y-%m-%d %H:%M:%S')
end_date = pd.to_datetime(end_date_str, format='%Y-%m-%d %H:%M:%S')

# filename_suffix = "Madrid"
# filepath = f"accumulated_log_and_data_{filename_suffix}.txt"
filepath = "large_corrected_table.csv"

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Function definition ---------------------------------------------------------
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

def plot_data(start_date, end_date, reduced_field, plot_vs_field):
    # Reading ---------------------------------------------------------------------
    data_df = pd.read_csv(filepath)
    print(data_df.columns.to_list())

    # Convert the 'Time' column to datetime
    data_df['Time'] = pd.to_datetime(data_df['Time'].str.strip('"'), format='%Y-%m-%d %H:%M:%S')

    data_df = data_df[(data_df['Time'] >= start_date) & (data_df['Time'] <= end_date)]

    # Define the numeric columns based on the new CSV structure
    numeric_cols = [
        'streamer_percent_1', 'streamer_percent_2', 'streamer_percent_3', 'streamer_percent_4', 
        'eff_global', 'unc_eff_global', 'count', 'pressure_lab', 'sensors_int_Temperature_int',
        'final_eff_1', 'final_eff_2', 'final_eff_3', 'final_eff_4', 'CRT_avg_mean'
    ]

    # -----------------------------------------------------------------------------------------------

    # Add the efficiencies for each plane if they exist in data
    # Apply the mean function to the grouped data by 'hv_mean'

    # !!! MAKE SURE TO PUT THE HV VALUE IN A CERTAIN DECIMAL APPROXIMATION !!!
    # Assuming 'hv_mean' is now represented by a similar column in the new CSV, e.g., 'hv_mean' or 'HV_mean'
    # If not, you need to identify the correct column name or create it.

    # rounded_decimals = 2
    # data_df['hv_mean'] = data_df['hv_mean'].round(rounded_decimals)

    data_df["t_in_K"] = data_df["sensors_int_Temperature_int"] + 273.15
    data_df["p_in_Pa"] = data_df["pressure_lab"] * 1000

    if reduced_field:
        # E/rho = V * T / P * cte
        data_df["hv_reduced"] = data_df["hv_mean"] * data_df["t_in_K"] / data_df["p_in_Pa"]
        step_size = 0.01 * data_df["t_in_K"].median() / data_df["p_in_Pa"].median()
        
        # V * P / T, which is actually nothing
        # data_df["hv_reduced"] = data_df["hv_mean"] * data_df["t_in_K"] / data_df["p_in_Pa"]
        # step_size = 0.01 * data_df["t_in_K"].median() / data_df["p_in_Pa"].median()
        
        data_grouped = data_df.groupby('hv_reduced')[numeric_cols].mean()
        label_hv = "$HV \\cdot T / P$"
        units_hv = "$(kV \\cdot K / Pa)$"
    else:
        data_grouped = data_df.groupby('hv_mean')[numeric_cols].mean()
        step_size = 0.01
        label_hv = "HV"
        units_hv = "(kV)"

    # Step size for smoothing (0.01 for HV)
    # step_size = 1 / 10**rounded_decimals

    # Check if CRT_avg exists in the data_grouped columns
    crt_avg = data_grouped.get('CRT_avg_mean', None)

    efficiency_M1 = data_grouped.get('final_eff_1', None)
    efficiency_M2 = data_grouped.get('final_eff_2', None)
    efficiency_M3 = data_grouped.get('final_eff_3', None)
    efficiency_M4 = data_grouped.get('final_eff_4', None)

    # Extract the relevant columns for plotting
    hv = data_grouped.index
    streamer_percentage_M1 = data_grouped['streamer_percent_1']
    streamer_percentage_M2 = data_grouped['streamer_percent_2']
    streamer_percentage_M3 = data_grouped['streamer_percent_3']
    streamer_percentage_M4 = data_grouped['streamer_percent_4']
    global_efficiency = data_grouped['eff_global']
    global_uncertainty = data_grouped['unc_eff_global']
    count = data_grouped['count']
    count_over_efficiency = count / global_efficiency

    count_over_efficiency = count_over_efficiency.replace([np.inf, -np.inf], 0)
    count_over_efficiency = count_over_efficiency.interpolate()
    count_over_efficiency = count_over_efficiency.fillna(0)

    pressure_lab = data_grouped['pressure_lab']
    temp_lab = data_grouped['sensors_int_Temperature_int']

    # Define the bin edges and center points for HV
    hv_min, hv_max = hv.min(), hv.max()
    hv_bins = np.arange(hv_min, hv_max + step_size, step_size)
    hv_bin_centers = (hv_bins[:-1] + hv_bins[1:]) / 2

    # Function to perform binning and averaging
    def bin_and_average(hv, values):
        binned_values = np.zeros(len(hv_bin_centers))
        for i in range(len(hv_bin_centers)):
            in_bin = (hv >= hv_bins[i]) & (hv < hv_bins[i + 1])
            binned_values[i] = np.nanmean(values[in_bin]) if np.any(in_bin) else np.nan
            # Use nanmean to handle NaNs
        return binned_values

    # Smooth data for each series by averaging over bins
    streamer_percentage_M1_smooth = bin_and_average(hv, streamer_percentage_M1)
    streamer_percentage_M2_smooth = bin_and_average(hv, streamer_percentage_M2)
    streamer_percentage_M3_smooth = bin_and_average(hv, streamer_percentage_M3)
    streamer_percentage_M4_smooth = bin_and_average(hv, streamer_percentage_M4)
    global_efficiency_smooth = bin_and_average(hv, global_efficiency)
    global_uncertainty_smooth = bin_and_average(hv, global_uncertainty)
    count_smooth = bin_and_average(hv, count)
    count_over_efficiency_smooth = bin_and_average(hv, count_over_efficiency)
    pressure_lab_smooth = bin_and_average(hv, pressure_lab)
    temp_lab_smooth = bin_and_average(hv, temp_lab)

    # Smooth normalized counts
    mean_count_smooth = np.nanmean(count_smooth)
    mean_count_over_eff_smooth = np.nanmean(count_over_efficiency_smooth)
    normalized_count_smooth = (count_smooth - mean_count_smooth) / mean_count_smooth
    normalized_count_over_eff_smooth = (count_over_efficiency_smooth - mean_count_over_eff_smooth) / mean_count_over_eff_smooth

    # Create subplots, adding one more if CRT_avg exists
    n_plots = 4
    fig, axs = plt.subplots(n_plots, 1, figsize=(8, 10), sharex=True)  # Adjusted figure size

    # Plot 1: Efficiency of each plane (if the efficiency columns exist)
    axs[0].set_ylabel('Efficiency')
    if efficiency_M1 is not None:
        axs[0].scatter(hv_bin_centers, bin_and_average(hv, efficiency_M1), label='Efficiency P1', color='blue')
    if efficiency_M2 is not None:
        axs[0].scatter(hv_bin_centers, bin_and_average(hv, efficiency_M2), label='Efficiency P2', color='orange')
    if efficiency_M3 is not None:
        axs[0].scatter(hv_bin_centers, bin_and_average(hv, efficiency_M3), label='Efficiency P3', color='green')
    if efficiency_M4 is not None:
        axs[0].scatter(hv_bin_centers, bin_and_average(hv, efficiency_M4), label='Efficiency P4', color='red')
    axs[0].legend()
    axs[0].set_ylim(0,1)
    axs[0].grid(True)
    axs[0].set_title(f'Efficiency of Each Plane vs {label_hv}')

    # Plot 3: Streamer Percentages vs HV
    axs[1].set_ylabel('Streamer %', color='tab:blue')
    axs[1].scatter(hv_bin_centers, streamer_percentage_M1_smooth, label='Streamer P1', color='blue')
    axs[1].scatter(hv_bin_centers, streamer_percentage_M2_smooth, label='Streamer P2', color='orange', linestyle='--')
    axs[1].scatter(hv_bin_centers, streamer_percentage_M3_smooth, label='Streamer P3', color='green', linestyle='-.')
    axs[1].scatter(hv_bin_centers, streamer_percentage_M4_smooth, label='Streamer P4', color='red', linestyle=':')
    axs[1].legend(loc='upper left')
    axs[1].grid(True)
    axs[1].set_title(f'Streamer % vs {label_hv}')

    # Plot 4: Pressure and Temperature vs HV
    axs[2].set_ylabel('Pressure (Lab)', color='tab:orange')
    axs[2].scatter(hv_bin_centers, pressure_lab_smooth, label='Pressure', color='orange')
    axs[2].tick_params(axis='y', labelcolor='tab:orange')
    # Add second y-axis for temperature
    ax_temp = axs[2].twinx()
    ax_temp.set_ylabel('Temperature (Lab)', color='tab:red')
    ax_temp.scatter(hv_bin_centers, temp_lab_smooth, label='Temperature', color='red')
    ax_temp.tick_params(axis='y', labelcolor='tab:red')
    axs[2].grid(True)
    axs[2].set_title(f'Pressure and Temperature vs {label_hv}')

    # axs[3].scatter(hv_bin_centers, hv_bin_centers, label='CRT Avg', color='purple')
    axs[3].scatter(hv_bin_centers, bin_and_average(hv, crt_avg) * 1000, label='CRT', color='purple')
    axs[3].set_ylabel('Timing uncertainty (ps)')
    axs[3].grid(True)
    axs[3].legend()
    axs[3].set_title(f'CRT (ps) vs {label_hv}')

    # Set common x-axis label
    axs[-1].set_xlabel(f'{label_hv} {units_hv}')
    axs[-1].set_xlim(hv_min, hv_max)

    # Adjust layout
    plt.tight_layout()
    return fig

# -----------------------------------------------------------------------------
# GUI Definition --------------------------------------------------------------
# -----------------------------------------------------------------------------

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Plotter")

        # Create and place the widgets
        self.start_date_label = ttk.Label(root, text="Start Date (YYYY-MM-DD HH:MM:SS):")
        self.start_date_label.grid(row=0, column=0, padx=10, pady=10)
        self.start_date_entry = ttk.Entry(root)
        self.start_date_entry.grid(row=0, column=1, padx=10, pady=10)
        self.start_date_entry.insert(0, "2025-02-25 17:30:00")

        self.end_date_label = ttk.Label(root, text="End Date (YYYY-MM-DD HH:MM:SS):")
        self.end_date_label.grid(row=1, column=0, padx=10, pady=10)
        self.end_date_entry = ttk.Entry(root)
        self.end_date_entry.grid(row=1, column=1, padx=10, pady=10)
        self.end_date_entry.insert(0, "2025-02-26 00:10:00")

        self.reduced_field_var = tk.BooleanVar()
        self.reduced_field_check = ttk.Checkbutton(root, text="Use Reduced Field", variable=self.reduced_field_var)
        self.reduced_field_check.grid(row=2, column=0, padx=10, pady=10)

        self.plot_vs_field_var = tk.BooleanVar()
        self.plot_vs_field_check = ttk.Checkbutton(root, text="Plot vs Field", variable=self.plot_vs_field_var)
        self.plot_vs_field_check.grid(row=2, column=1, padx=10, pady=10)

        self.plot_button = ttk.Button(root, text="Generate Plot", command=self.plot)
        self.plot_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

    def plot(self):
        start_date_str = self.start_date_entry.get()
        end_date_str = self.end_date_entry.get()
        reduced_field = self.reduced_field_var.get()
        plot_vs_field = self.plot_vs_field_var.get()

        start_date = pd.to_datetime(start_date_str, format='%Y-%m-%d %H:%M:%S')
        end_date = pd.to_datetime(end_date_str, format='%Y-%m-%d %H:%M:%S')

        fig = plot_data(start_date, end_date, reduced_field, plot_vs_field)

        # Open a new window to display the plot
        plot_window = tk.Toplevel(self.root)
        plot_window.title("Plot Results")
        plot_window.geometry("800x600")  # Set the size of the new window

        # Display the plot in the new window
        canvas = FigureCanvasTkAgg(fig, master=plot_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# -----------------------------------------------------------------------------
# Run the GUI -----------------------------------------------------------------
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()