import json
import subprocess
from cpeparser import CpeParser
import os
import pandas as pd

OVERALL_LOW_CRIT_SCORE_WEIGHT = 0.75

### Make script to see if api is set, if not set it

def crit_score(json_file, sw_hw_cve):
    endpoint_name = ''
    with open(json_file) as f:
        data = json.load(f)
        for crit in data['cves']:
            # Check if 'CVEs' key exists and if the CVE is in the list
            if 'CVEs' in crit and sw_hw_cve['cve_id'] in crit['CVEs']:
                criticality = crit.get('Criticality', '').strip().capitalize()
                endpoint_name = crit.get('Endpoint Name', '').strip()
                if criticality == 'Critical':
                    return 1.75, endpoint_name
                elif criticality == 'Medium':
                    return 1.5, endpoint_name
                elif criticality == 'Low':
                    return 1, endpoint_name
                else:
                    return 1, endpoint_name
    return 1, ""
    


def csv_to_json(csv_file, json_file):
    df = pd.read_csv(csv_file)

    # Function to parse CVEs from the 'CVEs' column
    def parse_cves(row):
        cves = []
        cve_entries = row.get('CVEs', '')
        if isinstance(cve_entries, str):
            for cve_entry in cve_entries.split(','):
                cve_entry = cve_entry.strip()
                if cve_entry.startswith(('CVE-', 'CVD-')):
                    # Convert 'CVD-' to 'CVE-' if applicable
                    if cve_entry.startswith('CVD-'):
                        cve_id = 'CVE-' + cve_entry[4:]
                    else:
                        cve_id = cve_entry
                    cves.append(cve_id)
        return cves if cves else []

    # Apply the parsing function and create a new 'CVEs' column with lists
    df['CVEs'] = df.apply(parse_cves, axis=1)

    # Rename 'Endpoint' to 'Endpoint Name' to match expected key in crit_score
    df = df.rename(columns={'Endpoint': 'Endpoint Name'})

    # Ensure 'Criticality' is standardized (e.g., stripping whitespace)
    df['Criticality'] = df['Criticality'].str.strip().str.capitalize()

    # Drop any other unnecessary columns (if any)
    df = df[['Endpoint Name', 'Criticality', 'CVEs']]

    # Convert to a list of dictionaries
    cves_list = df.to_dict(orient='records')

    # Create a dictionary with 'cves' as the key
    cves_dict = {'cves': cves_list}

    # Save to JSON with indentation for readability
    with open(json_file, 'w') as f:
        json.dump(cves_dict, f, indent=4)

def cve_scan(cve_prioritizer, cve_file, json_file_name):
    #json_file_name = args.json_file
    # Run cve_prioritizer.py to generate .json file
    subprocess.run(["python3", cve_prioritizer, "-j", json_file_name, "-vc", "-vck", "-v", "-t 100" , "-f", cve_file])
    
def parse_cvss_vector(cvss_vector):
    # Remove everything up to and including the first '/'
    cvss_vector = cvss_vector.split('/', 1)[-1]

    # Define possible values and their descriptions
    descriptions = {
        'AV': {
            'N': 'Network: Exploitable remotely over a network',
            'A': 'Adjacent: Exploitable from an adjacent network',
            'L': 'Local: Exploitable with local access',
            'P': 'Physical: Requires physical access',
        },
        'AC': {
            'L': 'Low: Exploitation is straightforward',
            'H': 'High: Exploitation requires specialized conditions',
        },
        'PR': {
            'N': 'None: No privileges needed',
            'L': 'Low: Requires basic user privileges',
            'H': 'High: Requires administrative privileges',
        },
        'UI': {
            'N': 'None: No user interaction required',
            'R': 'Required: User interaction is required',
        },
        'S': {
            'U': 'Unchanged: Exploitation does not affect other components',
            'C': 'Changed: Exploitation affects other components',
        },
        'C': {
            'N': 'None: No impact on confidentiality',
            'L': 'Low: Partial loss of confidentiality',
            'H': 'High: Complete loss of confidentiality',
        },
        'I': {
            'N': 'None: No impact on integrity',
            'L': 'Low: Partial loss of integrity',
            'H': 'High: Complete loss of integrity',
        },
        'A': {
            'N': 'None: No impact on availability',
            'L': 'Low: Partial loss of availability',
            'H': 'High: Complete loss of availability',
        },
    }
    
    # Define full names for the acronyms
    full_names = {
        'AV': 'Attack Vector',
        'AC': 'Attack Complexity',
        'PR': 'Privileges Required',
        'UI': 'User Interaction',
        'S': 'Scope',
        'C': 'Confidentiality Impact',
        'I': 'Integrity Impact',
        'A': 'Availability Impact',
    }
    
    # Split the vector into parts
    parts = cvss_vector.split('/')
    whole_description = {}
    tmp_description = {}
    # Initialize a list to hold the descriptions
    description_list = []
    
    # Iterate over each part and construct the descriptions
    for part in parts:
        if ':' not in part:  # Ensure the part contains a colon
            continue  # Skip this part if it's not valid
        
        code, value = part.split(':', 1)  # Split by the colon
        if code in full_names and code in descriptions and value in descriptions[code]:
            full_name = full_names[code]
            whole_description[full_name] = descriptions[code][value]
    
    return whole_description




def type_of_vuln_cpe(cpe_parsed):
    for key, value in cpe_parsed.items():
                if value not in ['-', '*']:
                    if key == 'part':
                        if value == 'a':
                            value = 'Application'
                        if value == 'o':
                            value = 'Operating System'
                        if value == 'h':
                            value = 'Hardware'
                    return value

def all_cpe(cpe_parsed):
    key_val_dict = {}
    for key, value in cpe_parsed.items():
        key_val_dict[key] = value
    return key_val_dict
    

def convert_to_json(output_path, json_file, crit_csv_file):
    #if os.path.exists(crit_csv_file):
        #crit_path = os.path.join(output_path, 'crit.json')
    csv_to_json(crit_csv_file, 'crit.json')
    cpe = CpeParser()
    with open(json_file) as f:
        data = json.load(f)

    sw_path = os.path.join(output_path, 'sw_cves.json')
    hw_path = os.path.join(output_path, 'hw_cves.json')

        # Load existing data from sw_cves.json if it exists
    try:
        with open(sw_path) as sw_f:
            sw_data = json.load(sw_f)
    except FileNotFoundError:
        sw_data = {'cves': []}
    try:
        with open(hw_path) as hw_f:
            hw_data = json.load(hw_f)
    except FileNotFoundError:
        hw_data = {'cves': []}
            
    sw_overall_resiliency_score = 0
    hw_overall_resiliency_score = 0
    sw_total_weight = 0
    hw_total_weight = 0
    max_sw_criticality = 1
    max_hw_criticality = 1
    max_sw_cvss = 0
    max_hw_cvss = 0

    for cve in data['cves']:
        cpe_string = cve['cpe']
        cpe_parsed = cpe.parser(cpe_string)
        cpe_to_json = all_cpe(cpe_parsed)
        cvss_vector_description = parse_cvss_vector(cve['vector'])
        type = type_of_vuln_cpe(cpe_parsed)
        
        cve['criticality'], cve['endpoint_name'] = crit_score('crit.json', cve)
        
        # Calculate resiliency score based on criticality and CVSS score
        # Increase the impact of high CVSS scores and criticality
        resiliency_score = (100 - (cve['cvss_base_score']) * 10) / (cve['criticality'])
        cve['resiliency_score'] = resiliency_score
        
        # Calculate weight based on CVSS score and criticality
        # Give more weight to high CVSS scores and high criticality
        criticality_factor = cve['criticality']
        weight = (cve['cvss_base_score']) * criticality_factor
        
        cve['cpe_full'] = cpe_to_json
        cve['cvss_vector_description'] = cvss_vector_description

        if type == 'Operating System' or type == 'Application':
            sw_data['cves'].append(cve)
            sw_overall_resiliency_score += resiliency_score * weight
            sw_total_weight += weight
            max_sw_criticality = max(max_sw_criticality, cve['criticality'])
            max_sw_cvss = max(max_sw_cvss, cve['cvss_base_score'])
        elif type == 'Hardware':
            hw_data['cves'].append(cve)
            hw_overall_resiliency_score += resiliency_score * weight
            hw_total_weight += weight
            max_hw_criticality = max(max_hw_criticality, cve['criticality'])
            max_hw_cvss = max(max_hw_cvss, cve['cvss_base_score'])

    # Reduce the adjustment factor for low criticality systems
    adjustment_factor = 1.2  # Changed from 1.5 to 1.2

    if sw_total_weight > 0:
        sw_overall_resiliency_score = sw_overall_resiliency_score / (sw_total_weight * 0.45)
        if max_sw_criticality == 1:  # If all systems are low criticality
            sw_overall_resiliency_score *= adjustment_factor
        # Add an additional penalty for high CVSS scores
        if max_sw_cvss >= 9.0:
            sw_overall_resiliency_score *= 0.75  # Reduce score by 1/4 for critical vulnerabilities
        sw_overall_resiliency_score = min(sw_overall_resiliency_score, 95)
        sw_data['overall_resiliency_score'] = sw_overall_resiliency_score
        with open(sw_path, 'w') as sw_f:
            json.dump(sw_data, sw_f, indent=4)
    else:
        sw_data['overall_resiliency_score'] = 100
        with open(sw_path, 'w') as sw_f:
                json.dump(sw_data, sw_f, indent=4)
    if hw_total_weight > 0:
        hw_overall_resiliency_score = hw_overall_resiliency_score / (hw_total_weight * 0.45)
        if max_hw_criticality == 1:  # If all systems are low criticality
            hw_overall_resiliency_score *= adjustment_factor
        # Add an additional penalty for high CVSS scores
        if max_hw_cvss >= 9.0:
            hw_overall_resiliency_score *= 0.75  # Reduce score by 1/4 for critical vulnerabilities
        hw_overall_resiliency_score = min(hw_overall_resiliency_score, 95)
        hw_data['overall_resiliency_score'] = hw_overall_resiliency_score
        # Write the updated data back to sw_cves.json
        with open(hw_path, 'w') as hw_f:
                json.dump(hw_data, hw_f, indent=4)
    else:
        hw_data['overall_resiliency_score'] = 100
        with open(hw_path, 'w') as hw_f:
            json.dump(hw_data, hw_f, indent=4)
    return round(sw_overall_resiliency_score), round(hw_overall_resiliency_score)

def delete_json_files(directory):
    try:
        # List all files in the provided directory
        files_in_directory = os.listdir(directory)
        
        # Filter out only .csv files
        json_files = [file for file in files_in_directory if file.endswith(".json")]
        
        if json_files:
            for file in json_files:
                file_path = os.path.join(directory, file)
                try:
                    os.remove(file_path)  # Delete the file
                    print(f"{file_path} has been deleted.")
                except Exception as e:
                    print(f"Error occurred while deleting {file_path}: {e}")
        else:
            print("No .json files found in the directory.")
    
    except Exception as e:
        print(f"Error occurred while accessing the directory: {e}")
