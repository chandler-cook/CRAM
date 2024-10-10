import os
import re

# Folder where CSV files are located
csv_folder = 'CSVfromTables'

# Output file where the extracted hardware information will be saved
output_file = 'extracted_hardware_models.txt'

# Hardware manufacturers/brands you expect to see
valid_brands = ["Cisco", "Dell", "Tripp Lite", "APC", "Miscellaneous"]

# Refined patterns for specific formats of hardware information
make_pattern = re.compile(r"^(Cisco|Dell|Tripp Lite|APC|Miscellaneous)", re.IGNORECASE)
model_pattern = re.compile(r"\b([\w\-]+)\b")  # Match alphanumeric model numbers

def extract_hardware_from_csvs(csv_folder, output_file):
    with open(output_file, 'w') as outfile:
        # Loop through each file in the CSV folder
        for file in os.listdir(csv_folder):
            if file.endswith('.csv'):
                file_path = os.path.join(csv_folder, file)
                
                try:
                    outfile.write(f"Extracting from {file}\n")
                    with open(file_path, 'r') as csvfile:
                        # Initialize placeholders for extracting hardware data
                        current_make = None
                        current_model = None
                        
                        # Loop through each line in the CSV file
                        for line in csvfile:
                            line = line.strip()
                            
                            # Check for a valid hardware manufacturer/brand (Make)
                            if make_pattern.search(line):
                                current_make = line
                            
                            # Check for a valid hardware model number
                            elif model_pattern.search(line):
                                current_model = line
                            
                            # If both Make and Model have been found, save them
                            if current_make and current_model:
                                outfile.write(f"Make: {current_make}\n")
                                outfile.write(f"Model No.: {current_model}\n\n")
                                
                                # Reset for the next hardware entry
                                current_make = None
                                current_model = None
                
                except Exception as e:
                    outfile.write(f"Error processing file {file}: {str(e)}\n")

    print(f"Hardware models have been extracted to {output_file}")

# Call the function to start processing
extract_hardware_from_csvs(csv_folder, output_file)
