import re
import os

# Function to parse the file and extract numbers next to specified keywords
def parse_file(file_path):
    # Initialize variables to store the values
    hardware_value = 0
    software_value = 0
    physical_value = 0
    # Define the patterns to search for (keywords followed by a number)
    patterns = {
        'Hardware': r'Hardware:\s*(\d+)',
        'Software': r'Software:\s*(\d+)',
        'Physical': r'Physical:\s*(\d+)'
    }

    # Open and read the file
    with open(file_path, 'r') as file:
        content = file.read()

        # Search for each pattern and store the results in the respective variable
        hardware_match = re.search(patterns['Hardware'], content)
        software_match = re.search(patterns['Software'], content)
        physical_match = re.search(patterns['Physical'], content)
        
        if hardware_match:
            hardware_value = int(hardware_match.group(1))
        
        if software_match:
            software_value = int(software_match.group(1))
        
        if physical_match:
            physical_value = int(physical_match.group(1))
    return hardware_value, software_value, physical_value
def process_directory(directory_path):
    hardwareTotal = 0
    softwareTotal = 0
    physicalTotal = 0
    for filename in os.listdir(directory_path):
        # Check if the file name contains '-Profile'
        if '-Profile' in filename:
            file_path = os.path.join(directory_path, filename)
            # Call parse_file function and retrieve values
            hardware, software, physical = parse_file(file_path)
        hardwareTotal = hardwareTotal + hardware
        softwareTotal = softwareTotal + software
        physicalTotal = physicalTotal + physical
    return hardwareTotal, softwareTotal, physicalTotal

def makeNewScore(hardware, software, physical):
    scoreP = physical - (2 * (scoreP/10))
    scoreH = hardware - (2 * (scoreH/10))
    scoreS = software - (2 * (scoreS/10))
# Example usage

scoreP = 0
scoreS = 0
scoreH = 0
checkedAPTs = []

directory = "C:\\Users\\jippy\\OneDrive\\Desktop\\CSC Work\\Cyber\\CRAM Data\\Text Files\\"
for x in checkedAPTs:
    for filename in os.listdir(directory):
        if x in filename and '-Profile' in filename:
            hardware,software,physical = process_directory(os.path.join(directory, x))
hardware = hardware/2
software = software/2
physical = physical/2
makeNewScore(hardware, software, physical)