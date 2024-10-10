import os
import re
import pandas as pd

# A more general regex pattern for hardware models
hardware_pattern = r'\b(?:[A-Za-z]+)\s*[A-Z0-9]+(?:-[A-Z0-9]+)*\b'

# Function to process a single CSV file and extract hardware models
def extract_hardware_models_from_csv(csv_file):
    extracted_hardware = []
    
    # Read the CSV file using pandas
    try:
        df = pd.read_csv(csv_file)
    except Exception as e:
        print(f"Error reading {csv_file}: {e}")
        return extracted_hardware
    
    # Iterate through each row and search for hardware models in all columns
    for index, row in df.iterrows():
        row_content = " ".join(row.astype(str))  # Convert all columns to strings and join
        matches = re.findall(hardware_pattern, row_content)
        extracted_hardware.extend(matches)
    
    return extracted_hardware

# Function to recursively process all CSV files in a folder
def process_csv_folder(folder_path, output_file):
    all_extracted_hardware = []

    # Recursively search for CSV files
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".csv"):
                csv_file_path = os.path.join(root, file)
                print(f"Processing file: {csv_file_path}")
                
                # Extract hardware models from this CSV
                extracted_hardware = extract_hardware_models_from_csv(csv_file_path)
                all_extracted_hardware.extend(extracted_hardware)
    
    # Remove duplicates
    unique_hardware = set(all_extracted_hardware)
    
    # Write results to a text file
    with open(output_file, 'w') as outfile:
        for model in unique_hardware:
            outfile.write(model + '\n')

    print(f"Extracted hardware models saved to {output_file}")

# Example usage
folder_path = 'CSVfromTables'  # Path to the folder containing your CSV files
output_file_path = 'extracted_hardware_models.txt'  # Output file for hardware models
process_csv_folder(folder_path, output_file_path)
