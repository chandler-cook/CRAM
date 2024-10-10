import os
import csv

# Folder where CSV files are located
csv_folder = '/home/user/Documents/Github/CSVfromTables'

# Output file where the extracted hardware information will be saved
output_file = 'extracted_hardware_models.txt'

# List of whitelisted brands
whitelisted_brands = [
    "Cisco", "Dell", "Tripp Lite", "APC", "Miscellaneous", 
    "HP", "Lenovo", "IBM", "ASUS", "Apple", "Acer", 
    "Intel", "Netgear", "Ubiquiti", "Juniper", "Samsung", "Gator"
]

# Function to check if a row contains valid hardware data
def is_valid_hardware_row(row):
    # Check if the row has at least two columns (Make and Model)
    if len(row) < 2:
        return False
    # Ensure that neither Make nor Model are empty or just miscellaneous
    make = row[0].strip()
    model = row[1].strip()
    
    # Check if the make is in the whitelisted brands
    if make and model and any(brand.lower() in make.lower() for brand in whitelisted_brands):
        return True
    return False

def extract_hardware_from_csvs(csv_folder, output_file):
    with open(output_file, 'w') as outfile:
        # Loop through each file in the CSV folder
        for file in os.listdir(csv_folder):
            if file.endswith('.csv'):
                file_path = os.path.join(csv_folder, file)
                
                try:
                    with open(file_path, 'r') as csvfile:
                        reader = csv.reader(csvfile)
                        
                        # Loop through each row in the CSV file
                        for row in reader:
                            # Extract Make and Model from the relevant columns
                            if is_valid_hardware_row(row):
                                make = row[0].strip()
                                model = row[1].strip()
                                outfile.write(f"Make: {make}\n")
                                outfile.write(f"Model No.: {model}\n\n")
                
                except Exception as e:
                    outfile.write(f"Error processing file {file}: {str(e)}\n")

    print(f"Hardware models have been extracted to {output_file}")

# Call the function to start processing
extract_hardware_from_csvs(csv_folder, output_file)
