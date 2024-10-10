import os
import pandas as pd

# Function to process a single CSV file and extract hardware models
def extract_hardware_models_from_csv(csv_file):
    extracted_hardware = []

    # Read the CSV file using pandas
    try:
        df = pd.read_csv(csv_file)
    except Exception as e:
        print(f"Error reading {csv_file}: {e}")
        return extracted_hardware

    # Check if the necessary columns ('Make', 'Model No.') are present
    if 'Make' in df.columns and 'Model No.' in df.columns:
        # Iterate through each row to extract hardware makes and models
        for index, row in df.iterrows():
            make = row['Make']
            model = row['Model No.']

            if pd.notna(make) and pd.notna(model):  # Ensure both are not NaN
                extracted_hardware.append(f"{make} {model}")

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
output_file_path = 'extracted_hardware_models_filtered.txt'  # Output file for hardware models
process_csv_folder(folder_path, output_file_path)


