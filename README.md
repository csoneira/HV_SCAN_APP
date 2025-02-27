# HV Scan Analysis Script

This repository contains a Python script for analyzing High Voltage (HV) scan data. The script reads data from CSV files, filters it based on user input, and performs various calculations and visualizations. It is designed to work with data from multiple stations and supports features like reduced field calculations, efficiency analysis, and streamer percentage tracking.

## Table of Contents
- [Features](#features)
- [Repository Structure](#repository-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [License](#license)

---

## Features

- **Data Loading and Filtering**: Loads HV scan data from CSV files and filters it based on user-specified date ranges.
- **Reduced Field Calculations**: Supports reduced field calculations for normalized HV values.
- **Efficiency and Streamer Analysis**: Calculates and visualizes efficiency and streamer percentages for each plane.
- **Pressure and Temperature Tracking**: Plots pressure and temperature data over time.
- **Interactive CLI**: Provides an interactive command-line interface for user input.
- **Visualizations**: Generates plots for HV vs. efficiency, streamer percentages, pressure, temperature, and more.
- **Google Drive Integration**: Downloads data files from Google Drive if they are missing or outdated.

---

## Repository Structure

```
HV_SCAN_APP/
├── DATA/                          # Directory for storing station-specific data
│   ├── MINGO01/                   # Data for station 1
│   │   └── data_1.csv             # CSV file for station 1
│   ├── MINGO02/                   # Data for station 2
│   │   └── data_2.csv             # CSV file for station 2
│   └── ...                        # Additional stations
├── CONFIG/                        # Configuration files
│   └── drive_links.txt            # File containing Google Drive links for data
├── hv_scan_analysis.py            # Main analysis script
├── requirements.list              # Package requirements
├── README.md                      # This file
└── LICENSE                        # GNU General Public License v3.0
```

---

## Installation

### Prerequisites
- Python 3.x
- Required Python packages: `numpy`, `pandas`, `matplotlib`, `gdown`

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/csoneira/HV_SCAN_APP.git
   cd HV_SCAN_APP
   ```

2. Install dependencies using:
   ```bash
   pip install -r requirements.list
   ```

3. Ensure the `DATA` and `CONFIG` directories are set up correctly:
   - Place station-specific CSV files in the `DATA/MINGO0X/` directories.
   - Add Google Drive links for each station in `CONFIG/drive_links.txt` (one link per line, formatted as `station_number URL`).

---

## Usage

Run the script from the command line:
```bash
python hv_scan_analysis.py
```

### User Inputs
- **Station Number**: Enter the station number (1-4).
- **Start and End Dates**: Specify the date range for analysis (format: `YYYY-MM-DD HH:MM:SS`).
- **Reduced Field**: Enable or disable reduced field calculations.
- **Plot Options**: Choose which plots to generate (e.g., HV vs. efficiency, streamer percentages, pressure, temperature).

### Example Workflow
1. The script will prompt for user inputs.
2. It will load the data for the specified station and date range.
3. If the data file is missing or outdated, it will download it from Google Drive.
4. The script will perform calculations and generate the requested plots.
5. Press any key in the terminal to exit after viewing the plots.

---

## Configuration

### `drive_links.txt`
This file contains Google Drive links for downloading station-specific data.

---

### Data Files
- Data files should be placed in the `DATA/MINGO0X/` directories, where `X` is the station number.
- Each file should be named `data_X.csv`, where `X` is the station number.

---

## License

This project is licensed under the **GNU General Public License v3.0**. See the [LICENSE](LICENSE) file for details.

---

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

---

## Contact

For questions or feedback, please contact:
- **C. Soneira-Landín**: csoneira@ucm.es
- **GitHub**: [csoneira](https://github.com/csoneira)
```

---

### Key Sections:
1. **Features**: Highlights the main functionalities of the script.
2. **Repository Structure**: Explains the directory layout and file organization.
3. **Installation**: Provides step-by-step instructions for setting up the environment.
4. **Usage**: Describes how to run the script and interact with it.
5. **Configuration**: Explains how to set up the `drive_links.txt` file and data directories.
6. **License**: Specifies the GNU GPL v3.0 license.
7. **Contributing**: Encourages contributions from the community.
8. **Acknowledgments**: Credits the libraries and tools used.
9. **Contact**: Provides contact information for questions or feedback.

This README is designed to be clear and comprehensive, making it easy for users and contributors to understand and use your repository. Let me know if you need further adjustments!