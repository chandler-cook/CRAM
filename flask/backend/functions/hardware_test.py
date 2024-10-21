import pandas as pd
from datetime import datetime
from rapidfuzz import fuzz

def find_matches(text_file_path, csv_file_path, similarity_threshold=75):
    # Initialize an empty list to store the matches
    matching_values = []
    matching_string = []

    # Read the CSV file using pandas with error-tolerant encoding
    try:
        df = pd.read_csv(csv_file_path, encoding='utf-8')  # Try with UTF-8 encoding
    except UnicodeDecodeError:
        df = pd.read_csv(csv_file_path, encoding='ISO-8859-1')  # Fallback to ISO-8859-1 encoding

    # Ensure the CSV has at least two columns
    if df.shape[1] < 2:
        raise ValueError("The CSV file must have at least two columns.")

    # Read the text file
    with open(text_file_path, 'r', encoding='utf-8') as textfile:  # Reading the text file with UTF-8 encoding
        text_content = textfile.read().splitlines()  # Splitting by lines
    
    # Iterate over each line (or substring) in the text file
    for substring in text_content:
        # Iterate through each row of the DataFrame
        for index, row in df.iterrows():
            csv_value = row[0]  # First column value (to compare)
            corresponding_value = row[1]  # Second column value (to append)
            
            # Calculate the similarity ratio
            similarity = fuzz.ratio(substring, csv_value)
            
            # If similarity is above the threshold, append the corresponding value
            if similarity >= similarity_threshold and substring not in matching_string:
                matching_values.append(corresponding_value)
                matching_string.append(substring)
                print(substring)
    return matching_values