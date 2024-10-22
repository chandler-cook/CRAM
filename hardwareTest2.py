import pandas as pd
from rapidfuzz import fuzz
from difflib import SequenceMatcher
from datetime import datetime
def check_substring(substring1, list):
    for x in list:
        if x in substring1:
            return False
    return True

def find_matches(text_file_path, csv_file_path):
    # Initialize an empty list to store the matches
    matching_values = []
    matching_string = []

    # Read the CSV file using pandas with error-tolerant encoding
    try:
        df = pd.read_csv(csv_file_path, encoding='utf-8')  # Try with UTF-8 encoding
    except UnicodeDecodeError:
        df = pd.read_csv(csv_file_path, encoding='ISO-8859-1')  # Fallback to ISO-8859-1 encoding
    modelList = df['Hardware Name'].tolist()
    yearList = df['Year'].tolist()
    # Ensure the CSV has at least two columns
    if df.shape[1] < 2:
        raise ValueError("The CSV file must have at least two columns.")

    # Read the text file
    with open(text_file_path, 'r', encoding='utf-8') as textfile:  # Reading the text file with UTF-8 encoding
        text_content = textfile.read().splitlines()  # Splitting by lines
    
    # Iterate over each line (or substring) in the text file
    for substring in text_content:
        for i, value in enumerate(modelList):
            if modelList[i] in substring and modelList[i] not in matching_string:
                matching_string.append(modelList[i])
                matching_values.append(yearList[i])
                print(modelList[i])
    return matching_values
yearList = find_matches("C:\\Users\\johno\\Downloads\\run.txt","C:\\Users\\johno\\Desktop\\CRAM\\Data\\Hardware Database.csv")
count_5_10 = 0
count_10_20 = 0
count_over_20 = 0
hardwareScore = 0
# Get the current year
current_year = datetime.now().year
for x in yearList:
    if (current_year - 10) < int(x) & (int(x) <= 5):
        count_5_10 += 1
    elif (current_year - 20 < int(x)) & (int(x) <= current_year - 10):
        count_10_20 += 1
    elif int(x) <= (current_year - 20):
        count_over_20 += 1

hardwareScore += (count_5_10 * 2)
hardwareScore += (count_10_20 * 5)
hardwareScore += (count_over_20 * 20)
print(str(hardwareScore))