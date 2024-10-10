import os
import pandas as pd

# Define the whitelist of popular brands and your specific brands
whitelisted_brands = [
    "Cisco", "Dell", "Tripp Lite", "APC", "Miscellaneous", "HP", "Lenovo", "IBM", "ASUS",
    "Apple", "Acer", "Intel", "Netgear", "Ubiquiti", "Juniper", "Samsung", "Gator"
]

def extract_hardware_models_from_csv(folder_path, output_file):
    with open(output_file, 'w') as outfile:
        for file_name in os.listdir(folder_path):
            if file_name.endswith(".csv"):
                print(f"Extracting from {file_name}")
                file_path = os.path.join(folder_path, file_name)
                df = pd.read_csv(file_path)

                # Ensure necessary columns are present
                if 'Make' in df.columns and 'Model No.' in df.columns:
                    # Filter for rows where 'Make' is in the whitelist
                    filtered_df = df[df['Make'].isin(whitelisted_brands)]
                    
                    # Write the filtered makes and models to the output file
                    for _, row in filtered_df.iterrows():
                        make = row['Make']
                        model = row['Model No.']
                        outfile.write(f"Make: {make}, Model No.: {model}\n")
                else:
                    print(f"Relevant columns not found in {file_name}")

    print(f"Extraction completed. Results saved to {output_file}")

# Define the folder containing the CSV files and the output file
csv_folder_path = "CSVfromTables"  # Update this path if needed
output_txt_file = "extracted_hardware_models.txt"

# Run the extraction process
extract_hardware_models_from_csv(csv_folder_path, output_txt_file)
