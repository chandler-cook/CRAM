import pandas as pd
from datetime import datetime
from difflib import SequenceMatcher
def is_similar(str1, str2, threshold=0.75):
    """Returns True if the similarity ratio between str1 and str2 is above the threshold."""
    return SequenceMatcher(None, str1, str2).ratio() >= threshold

def find_similar_entries(csv_file1, csv_file2):
    similar_values = []

    # Read the first and second CSV files into pandas DataFrames
    df1 = pd.read_csv(csv_file1)
    df2 = pd.read_csv(csv_file2)

    # Iterate over each value in the first column of the first DataFrame
    for value1 in df1.iloc[:, 0]:  # First column of CSV1
        # Compare with each value in the first column of the second DataFrame
        for value2 in df2.iloc[:, 0]:  # First column of CSV2
            # If similarity is above 85%, store the second column value of the first DataFrame
            if is_similar(str(value1), str(value2)):
                similar_values.append(df1.iloc[df1[df1.iloc[:, 0] == value1].index[0], 1])  # Store the second column value from CSV1

    return similar_values

def print_first_column(csv_file):
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(csv_file)
    
    # Print all the values in the first column
    for value in df.iloc[:, 0]:
        print(value)

yearList = find_similar_entries("C:\\Users\\johno\\Downloads\\cleaned_combined_hardware_dates(1).csv", "C:\\Users\\johno\\Downloads\\image21_table_0.csv")
count_5_10 = 0
count_10_20 = 0
count_over_20 = 0
# Get the current year
current_year = datetime.now().year
for x in yearList:
    if (current_year - 10) < int(x) & (int(x) <= 5):
        count_5_10 += 1
    elif (current_year - 20 < int(x)) & (int(x) <= current_year - 10):
        count_10_20 += 1
    elif int(x) <= (current_year - 20):
        count_over_20 += 1
# Output the counts
print(f"The count of years between 5 and 10 years older than the current year: {count_5_10}")
print(f"The count of years between 10 and 20 years older than the current year: {count_10_20}")
print(f"The count of years more than 20 years older than the current year: {count_over_20}")