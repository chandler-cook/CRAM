import os
import re
import pandas as pd

# A refined regex pattern for matching hardware models, excluding CVEs and dates
hardware_pattern = r'\b(?:[A-Za-z]+)\s*[A-Z0-9]+(?:-[A-Z0-9]+)*\b'

# Exclusion patterns (for dates, CVEs, etc.)
exclude_patterns = [
    r'\bCVE-\d{4}-\d+\b',            # Matches CVE numbers like CVE-2023-0015
    r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b',  # Matches dates like 18/09/2023, 09-18-23
    r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\b',  # Matches month names
    r'\b\d{1,2}(st|nd|rd|th)?\b'  # Matches ordinal dates like 18th
]

# Function to check if an item matches any exclusion patterns
def is_excluded(item):
    for pattern in exclude_patterns:
        if re.search(pattern, item):
            return True
    return False

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
        
        # Filter out any matches that fall under the exclusion patterns (e.g., CVEs, dates)
        filtered_matches = [match for match in matches if not is_excluded(match)]
        extracted_hardware.extend(filtered_matches)
    
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
