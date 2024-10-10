import os
import pandas as pd

# Folder where CSV files are located
csv_folder = 'CSVfromTables'

# Output file where the extracted hardware information will be saved
output_file = 'extracted_hardware_models.txt'

# List of keywords to identify relevant columns
hardware_keywords = ['Make', 'Model No.', 'Description']

def extract_hardware_from_csvs(csv_folder, output_file):
    with open(output_file, 'w') as outfile:
        # Loop through each file in the CSV folder
        for file in os.listdir(csv_folder):
            if file.endswith('.csv'):
                file_path = os.path.join(csv_folder, file)
                
                try:
                    # Read CSV into DataFrame
                    df = pd.read_csv(file_path)
                    
                    # Check if the relevant columns exist
                    if all(keyword in df.columns for keyword in hardware_keywords):
                        outfile.write(f"Extracting from {file}\n")
                        
                        # Loop through each row to extract Make, Model No., and Description
                        for index, row in df.iterrows():
                            make = row['Make']
                            model_no = row['Model No.']
                            description = row['Description']
                            
                            outfile.write(f"Make: {make}, Model No.: {model_no}, Description: {description}\n")
                    
                    else:
                        outfile.write(f"Relevant columns not found in {file}\n")
                
                except Exception as e:
                    outfile.write(f"Error processing {file}: {e}\n")

    print(f"Hardware extraction completed. Check '{output_file}' for results.")

# Run the function
extract_hardware_from_csvs(csv_folder, output_file)


