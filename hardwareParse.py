import os
import re

# Folder where CSV files are located
csv_folder = 'CSVfromTables'

# Output file where the extracted hardware information will be saved
output_file = 'extracted_hardware_models.txt'

# Patterns to identify Make, Model No., and Description lines
make_pattern = re.compile(r"^(Make|Cisco|Dell|Tripp Lite|APC|Miscellaneous)", re.IGNORECASE)
model_pattern = re.compile(r"(Model No\.|[\w\-]+)")  # Catch Model No. or alphanumeric model numbers
description_pattern = re.compile(r"Description|[a-zA-Z ]+")

def extract_hardware_from_csvs(csv_folder, output_file):
    with open(output_file, 'w') as outfile:
        # Loop through each file in the CSV folder
        for file in os.listdir(csv_folder):
            if file.endswith('.csv'):
                file_path = os.path.join(csv_folder, file)
                
                try:
                    outfile.write(f"Extracting from {file}\n")
                    with open(file_path, 'r') as csvfile:
                        # Loop through each line in the CSV file
                        for line in csvfile:
                            # Search for Make, Model No., and Description in each line
                            if make_pattern.search(line):
                                outfile.write(f"Make: {line.strip()}\n")
                            elif model_pattern.search(line):
                                outfile.write(f"Model No.: {line.strip()}\n")
                            elif description_pattern.search(line):
                                outfile.write(f"Description: {line.strip()}\n")
                
                except Exception as e:
                    outfile.write(f"Error processing file {file}: {str(e)}\n")

    print(f"Hardware models have been extracted to {output_file}")

# Call the function to start processing
extract_hardware_from_csvs(csv_folder, output_file)
