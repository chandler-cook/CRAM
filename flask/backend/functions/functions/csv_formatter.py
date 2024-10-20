import os
import pandas as pd
import numpy
import csv
import re
from collections import Counter

def generate_csv(output_file):
    # Define the column labels
    columns = ['Endpoint Name', 'Criticality', 'CVEs']
    
    # Create an empty DataFrame with the specified columns
    df = pd.DataFrame(columns=columns)
    
    # Save the DataFrame to a new CSV file
    df.to_csv(output_file, index=False)
    
    print(f"CSV file '{output_file}' created with 3 columns.")

def check_criticality(directory_path, matched_files, search_value='F6'):
    # Loop through all files in the directory
    for filename in os.listdir(directory_path):
        # Check if the file is a CSV file
        if filename.endswith('.csv'):
            file_path = os.path.join(directory_path, filename)
            
            try:
                # Load the CSV file
                df = pd.read_csv(file_path, low_memory=False)
                
                # Check if any cell contains the search value
                match = (df == search_value).any().any()  # Checks if any cell has the value 'F6'
                
                # If a match is found, print the file name
                if match:
                    matched_files.append(file_path)
                    print(f'Match found in file: {filename}')
            except Exception as e:
                print(f'Error processing file {filename}: {e}')

    return matched_files

def process_csvs(csv_list, processed_list):
    for file in csv_list:
        try:
            # Load the CSV file
            df = pd.read_csv(file, low_memory=False)
            
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
            processed_list.append(output_file)
            df.to_csv(output_file, index=False)
            print(f"Processed file: {output_file}")

        except Exception as e:
            print(f"Error processing file {file}: {e}")

    return processed_list

def search_csvs(directory, substring = 'CVE'):
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

def assign_criticality(modified_csv, new_csv):
    try:
        # Load the modified CSV file
        df_modified = pd.read_csv(modified_csv, low_memory=False)
        df_newCSV = pd.read_csv(new_csv, low_memory=False)
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
            
            if (row[:len(row)//3] == 'X').any():
                criticality = 'Critical'

            # Check the second portion (e.g., the second third of the data)
            elif (row[len(row)//3:2*len(row)//3] == 'X').any():
                criticality = 'Medium'

            # Check the third portion (the last third of the data)
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

def last_empty(input_file, output_file):
    # Read the CSV file
    with open(input_file, 'r', newline='') as infile:
        reader = list(csv.reader(infile))
        
        # Traverse rows from the second row to the last
        i = 1
        while i < len(reader):
            if reader[i][-1] == '':  # Check if the last column is empty
                # Append the current row's first column value to the previous row's first column
                reader[i-1][0] = reader[i-1][0] + ' ' + reader[i][0] if reader[i-1][0] else reader[i][0]
                
                # Remove the current row after appending
                reader.pop(i)
            else:
                i += 1  # Move to the next row only if no deletion

        # Write the updated data to a new CSV file
        with open(output_file, 'w', newline='') as outfile:
            writer = csv.writer(outfile)
            writer.writerows(reader)

def first_empty(input_file, output_file):
    # Read the CSV file
    with open(input_file, 'r', newline='') as infile:
        reader = list(csv.reader(infile))
        
        # Traverse rows from the second row to the last
        i = 1
        while i < len(reader):
            if reader[i][0] == '':  # Check if the first column is empty
                # Append the current row's last column value to the previous row's last column
                reader[i-1][-1] = reader[i-1][-1] + ', ' + reader[i][-1] if reader[i-1][-1] else reader[i][-1]
                
                # Remove the current row after appending
                reader.pop(i)
            else:
                i += 1  # Move to the next row only if no deletion

        # Write the updated data to a new CSV file
        with open(output_file, 'w', newline='') as outfile:
            writer = csv.writer(outfile)
            writer.writerows(reader)

def append_matching(primary_csv, secondary_csv):
    # Read Primary.csv
    with open(primary_csv, 'r') as p_file:
        primary_data = list(csv.reader(p_file))
    
    # Read Secondary.csv
    with open(secondary_csv, 'r') as s_file:
        secondary_data = list(csv.reader(s_file))
    
    # Create new Primary.csv content with appended column
    updated_primary_data = []
    
    # Loop through each row in Primary.csv
    for p_row in primary_data:
        primary_value = p_row[0]
        primary_tokens = tokenize(primary_value)
        
        # Track if we find a match
        matching_value = ""
        
        # Nested loop: compare with each row in Secondary.csv
        for s_row in secondary_data:
            secondary_value = s_row[0]
            secondary_tokens = tokenize(secondary_value)
            
            # Check word similarity (50% threshold)
            if word_similarity(primary_tokens, secondary_tokens) >= 0.75:
                matching_value = s_row[-1]  # Get the final column of the secondary row
                break  # Stop searching once a match is found
        
        # Append the matching value to the current row of Primary.csv
        updated_primary_data.append(p_row + [matching_value])
    
    # Write the updated Primary.csv back to disk
    with open(primary_csv, 'w', newline='') as p_file:
        writer = csv.writer(p_file)
        writer.writerows(updated_primary_data)

def process_csv2(input_file, output_file):
    # Read the CSV file
    with open(input_file, mode='r', newline='', encoding='utf-8') as infile:
        reader = list(csv.reader(infile))

    # Process the CSV content
    new_rows = []
    for i in range(len(reader)):
        if i > 0 and (reader[i][0].startswith('CVE-') or reader[i][0].startswith('CVD-')):
            # Append the current row to the row above
            reader[i - 1] = reader[i - 1] + reader[i]
        else:
            # Add the row if it's not part of a CVE/CVD adjustment
            new_rows.append(reader[i])

    # Write the modified rows to the output CSV
    with open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        writer.writerows(new_rows)

def tokenize(text):
    """Tokenizes and removes stopwords and punctuation from a given text."""

    # List of common stopwords to ignore during comparison
    stopwords = {"and", "the", "is", "in", "at", "of", "on", "a", "to"}

    # Convert to lowercase, remove punctuation, and split into words
    words = re.findall(r'\w+', text.lower())
    # Remove stopwords
    filtered_words = [word for word in words if word not in stopwords]
    return filtered_words

def word_similarity(tokens1, tokens2):
    """Calculates the percentage of common words between two token lists."""
    common_words = Counter(tokens1) & Counter(tokens2)
    total_words = max(len(tokens1), len(tokens2))
    
    # If no words in either string, return 0 similarity
    if total_words == 0:
        return 0
    
    # Percentage of common words
    similarity = sum(common_words.values()) / total_words
    return similarity

def delete_csv_files(directory):
    try:
        # List all files in the provided directory
        files_in_directory = os.listdir(directory)
        
        # Filter out only .csv files
        csv_files = [file for file in files_in_directory if file.endswith(".csv")]
        
        if csv_files:
            for file in csv_files:
                file_path = os.path.join(directory, file)
                try:
                    os.remove(file_path)  # Delete the file
                    print(f"{file_path} has been deleted.")
                except Exception as e:
                    print(f"Error occurred while deleting {file_path}: {e}")
        else:
            print("No .csv files found in the directory.")
    
    except Exception as e:
        print(f"Error occurred while accessing the directory: {e}")