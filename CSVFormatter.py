import os
import pandas as pd

matchedFiles = []
processedList = []
cveFiles = []

def check_csv_for_criticality(directory_path, search_value='F6'):
    # Loop through all files in the directory
    for filename in os.listdir(directory_path):
        # Check if the file is a CSV file
        if filename.endswith('.csv'):
            file_path = os.path.join(directory_path, filename)
            
            try:
                # Load the CSV file
                df = pd.read_csv(file_path)
                
                # Check if any cell contains the search value
                match = (df == search_value).any().any()  # Checks if any cell has the value 'F6'
                
                # If a match is found, print the file name
                if match:
                    filename1 = "C:\\Users\\JP\\Desktop\\Personal Projects\\CRAM Work\\" + filename
                    matchedFiles.append(filename1)
                    print(f'Match found in file: {filename}')
            except Exception as e:
                print(f'Error processing file {filename}: {e}')

def check_csv_for_cve(directory_path, search_value='CVE-'):
    # Loop through all files in the directory
    for filename in os.listdir(directory_path):
        # Check if the file is a CSV file
        if filename.endswith('.csv'):
            file_path = os.path.join(directory_path, filename)
            
            try:
                # Load the CSV file
                df = pd.read_csv(file_path)
                
                # Check if any cell contains the search value
                match = (df == search_value).any().any()  # Checks if any cell has the value 'F6'
                
                # If a match is found, print the file name
                if match:
                    filename1 = "C:\\Users\\JP\\Desktop\\Personal Projects\\CRAM Work\\" + filename
                    cveFiles.append(filename1)
                    print(f'Match found in file: {filename}')
            except Exception as e:
                print(f'Error processing file {filename}: {e}')

def process_csvs(csv_list):
    for file in csv_list:
        try:
            # Load the CSV file
            df = pd.read_csv(file)
            
            # Create a list to track indices of rows to be deleted
            rows_to_delete = []

            # Iterate over the rows starting from the second row
            for i in range(1, len(df)):
                first_value = df.iloc[i, 0]  # First value of the current row
                other_values = df.iloc[i, 1:]  # Other values in the row
                
                # Check if all other columns in the row are empty (NaN or empty string)
                if other_values.isna().all() or (other_values == '').all():
                    # Check if the previous row's first value contains 'X'
                    prev_row_value = df.iloc[i-1, 0]
                    
                    if 'X' in prev_row_value:
                        # Insert the new text before 'X'
                        updated_value = prev_row_value.replace('X', f'{first_value} X')
                    else:
                        # Otherwise, append the new text to the first value of the previous row
                        updated_value = str(prev_row_value) + ' ' + str(first_value)
                    
                    # Update the previous row's first value
                    df.iloc[i-1, 0] = updated_value
                    
                    # Add the index of the current row to the list of rows to delete
                    rows_to_delete.append(i)

            # Drop the rows that were marked for deletion
            df = df.drop(rows_to_delete).reset_index(drop=True)

            # Save the modified DataFrame back to the CSV file or a new one
            output_file = file.replace('.csv', '_modified.csv')  # Create a modified version
            processedList.append(output_file)
            df.to_csv(output_file, index=False)
            print(f"Processed file: {output_file}")

        except Exception as e:
            print(f"Error processing file {file}: {e}")


def generate_csv_with_3_columns(output_file):
    # Define the column labels
    columns = ['Endpoint Name', 'Criticality', 'CVEs']
    
    # Create an empty DataFrame with the specified columns
    df = pd.DataFrame(columns=columns)
    
    # Save the DataFrame to a new CSV file
    df.to_csv(output_file, index=False)
    
    print(f"CSV file '{output_file}' created with 3 columns.")


def add_first_column_and_assign_criticality(modified_csv, new_csv):
    try:
        # Load the modified CSV file
        df_modified = pd.read_csv(modified_csv)
        df_newCSV = pd.read_csv(new_csv)
        # Check if the necessary columns already exist
        if 'Endpoint Name' not in df_newCSV or 'Criticality' not in df_newCSV:
            print(f"Error: CSV file '{new_csv}' must contain 'Endpoint Name' and 'Criticality' columns.")
            return
        
        # Create a temporary DataFrame to hold new rows
        new_rows = []

        # Iterate over the rows to determine the criticality and add the first column value
        for i in range(len(df_modified)):
            row = df_modified.iloc[i, :]
            
            # Get the value of the first column
            endpoint_name = row.iloc[0]  # First column of the current row
            
            # Check the first 5 columns for 'X'
            if (row[:6] == 'X').any():
                criticality = 'Critical'
            # If no 'X' in the first 5 columns, check columns 6, 7, and 8
            elif (row[6:9] == 'X').any():
                criticality = 'Medium'
            # If no 'X' in the first 8 columns
            else:
                criticality = 'Low'
            
            # Append new row data to the temporary list
            new_rows.append({'Endpoint Name': endpoint_name, 'Criticality': criticality})
        
        # Convert the new rows into a DataFrame
        df_new = pd.DataFrame(new_rows)
        
        # Append the new DataFrame to the new CSV without overwriting
        df_new.to_csv(new_csv, mode='a', header=not pd.io.common.file_exists(new_csv), index=False)
        print(f"Data appended to CSV '{new_csv}' successfully.")
        
    except Exception as e:
        print(f"Error processing files {modified_csv} or {new_csv}: {e}")


def search_csvs_in_directory(directory, substring = 'CVE'):
    """
    Searches all CSV files in a directory for any cell containing a specific substring.

    Parameters:
    directory (str): The directory path to search for CSV files.
    substring (str): The substring to search for in the CSV files.

    Returns:
    List of file paths of CSVs that contain the substring.
    """
    matching_files = []
    
    # Traverse through the directory and find CSV files
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.csv'):
                file_path = os.path.join(root, file)
                
                try:
                    # Read the CSV file
                    df = pd.read_csv(file_path, dtype=str)  # Read as string to avoid type issues
                    
                    # Check if the substring exists in any cell
                    if df.apply(lambda x: x.str.contains(substring, na=False)).any().any():
                        matching_files.append(file_path)
                
                except Exception as e:
                    print(f"Error reading file {file_path}: {e}")
    
    return matching_files


# Specify the directory path
directory_path = "C:\\Users\\JP\\Desktop\\Personal Projects\\CRAM Work"

# Run the function to check the headers in all CSV files

output_file = "C:\\Users\\JP\\Desktop\\Personal Projects\\CRAM Work\\test.csv"
#generate_csv_with_3_columns(output_file)
check_csv_for_criticality(directory_path)
check_csv_for_cve(directory_path)
#process_csvs(matchedFiles)
#for x in processedList:
    #add_first_column_and_assign_criticality(x, output_file)

cveFiles = search_csvs_in_directory(directory_path)
if cveFiles:
    print(f"CSV files containing the substring CVE:")
    for csv in cveFiles:
        print(csv)
else:
    print(f"No CSV files found with the substring CVE.")