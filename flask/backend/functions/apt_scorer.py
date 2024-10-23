import re
import os

#the scores below need to be changed to take in the scores that are displayed after the model is initially run
scoreP = 0
scoreS = 0
scoreH = 0

hardwareTotal = 0
softwareTotal = 0
physicalTotal = 0
checkedAPTs = [] #this list needs to be filled with the checked APTs

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
    global hardwareTotal
    global softwareTotal
    global physicalTotal
    hardware, software, physical = parse_file(directory_path)
    hardwareTotal = hardwareTotal + hardware
    softwareTotal = softwareTotal + software
    physicalTotal = physicalTotal + physical
    return hardwareTotal, softwareTotal, physicalTotal

def makeNewScore(hardware, software, physical):
    global scoreH,scoreP,scoreS,checkedAPTs
    if(len(checkedAPTs) <= 5):
        scoreP = scoreP - (physical * (1/5))
        scoreH = scoreH - (hardware * (1/5))
        scoreS = scoreS - (software * (1/5))
    elif(len(checkedAPTs) <= 10):
        scoreP = scoreP - (physical * (1/10))
        scoreH = scoreH - (hardware * (1/10))
        scoreS = scoreS - (software * (1/10))
    elif(len(checkedAPTs) <= 20):
        scoreP = scoreP - (physical * (1/20))
        scoreH = scoreH - (hardware * (1/20))
        scoreS = scoreS - (software * (1/20))
    elif(len(checkedAPTs) <= 30):
        scoreP = scoreP - (physical * (1/30))
        scoreH = scoreH - (hardware * (1/30))
        scoreS = scoreS - (software * (1/30))
    elif(len(checkedAPTs) <= 40):
        scoreP = scoreP - (physical * (1/40))
        scoreH = scoreH - (hardware * (1/40))
        scoreS = scoreS - (software * (1/40))
    elif(len(checkedAPTs) <= 50):
        scoreP = scoreP - (physical * (1/50))
        scoreH = scoreH - (hardware * (1/50))
        scoreS = scoreS - (software * (1/50))
    elif(len(checkedAPTs) <= 75):
        scoreP = scoreP - (physical * (1/75))
        scoreH = scoreH - (hardware * (1/75))
        scoreS = scoreS - (software * (1/75))
    elif(len(checkedAPTs) <= 100):
        scoreP = scoreP - (physical * (1/100))
        scoreH = scoreH - (hardware * (1/100))
        scoreS = scoreS - (software * (1/100))
    elif(len(checkedAPTs) <= 150):
        scoreP = scoreP - (physical * (1/150))
        scoreH = scoreH - (hardware * (1/150))
        scoreS = scoreS - (software * (1/150))
    else:
        scoreP = scoreP - (physical * (1/200))
        scoreH = scoreH - (hardware * (1/200))
        scoreS = scoreS - (software * (1/200))
    scoreP = round(scoreP)
    scoreH = round(scoreH)
    scoreS = round(scoreS)
    for x in checkedAPTs:
        print(x)
    print("Physical: " + str(scoreP) + "   Hardware: " + str(scoreH) + "   Software: " + str(scoreS))
    return int(scoreS),int(scoreP),int(scoreH)


#hardware = 0
#hysical = 0
#software = 0

#irectory = "C:\\Users\\jippy\\OneDrive\\Desktop\\CSC Work\\Cyber\\CRAM Data\\Text Files\\" #this path needs to be changed to point to wherever the text files for the APTs are stored
#for x in checkedAPTs:
    #directory_tmp = directory + x + '-Profile.txt'
    #hardware,software,physical = process_directory(directory_tmp)
#scoreS,scoreP,scoreH = makeNewScore(hardware, software, physical) #these are the scores that have been updated to reflect the APT data