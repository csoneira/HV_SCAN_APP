import gdown
import os
import gdown

# Read the file and store links in a dictionary
file_links = {}
with open("drive_links.txt", "r") as f:
    for line in f:
        parts = line.strip().split()  # Split by spaces
        if len(parts) > 1:  # Ensure the line is valid
            station = parts[0]  # First column is the station number
            url = parts[1]  # Second column is the Google Drive link
            file_links[station] = url

# Get user input for station number
station_number = input("Enter the station number: ").strip()

# Check if the station number exists
if station_number in file_links:
    drive_url = file_links[station_number]
    
    # Define the destination directory and filename
    destination_folder = f"./DATA/MINGO0{station_number}"
    destination_file = os.path.join(destination_folder, f"data_{station_number}.csv")

    # Create the directory if it doesn't exist
    os.makedirs(destination_folder, exist_ok=True)

    print(f"Downloading file for station {station_number}...")
    
    # Use gdown to download and rename the file
    gdown.download(drive_url, destination_file, quiet=False, fuzzy=True)

    print(f"Download complete! File saved to {destination_file}")
else:
    print(f"Station number {station_number} not found.")