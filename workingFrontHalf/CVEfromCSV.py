import os
import re
import pandas as pd

# Function to extract CVEs from a CSV file
def extract_cve_from_csv(file_path, output_file):
    try:
        df = pd.read_csv(file_path)
        
        # Convert the DataFrame to a single string for searching
        csv_content = df.to_string(index=False, header=False)
        
        # Regular expression to match 'CVE-' followed by numbers and hyphens
        cve_matches = re.findall(r'(CVE-\d{4}-\d+)', csv_content)
        
        # Write each match to the output file
        with open(output_file, 'a') as outfile:  # Append mode to consolidate results across files
            for match in cve_matches:
                outfile.write(match + '\n')
                print(f"Extracted {match} from {file_path}")  # Optional: Print to console
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")

# Function to process all CSV files in a directory
def process_all_csv_files(directory, output_file):
    try:
        csv_files = [f for f in os.listdir(directory) if f.endswith('.csv')]
        
        # Clear the output file before appending results
        with open(output_file, 'w') as f:
            f.write('')
        
        for csv_file in csv_files:
            file_path = os.path.join(directory, csv_file)
            extract_cve_from_csv(file_path, output_file)
    except Exception as e:
        print(f"Error processing directory {directory}: {e}")

# Example usage
csv_directory = 'home/user/documents/Github/CSVfromTables'  # Directory containing the CSV files
output_file_path = 'CVEfromCSVOutput.txt'  # Output file to store extracted CVEs

process_all_csv_files(csv_directory, output_file_path)
