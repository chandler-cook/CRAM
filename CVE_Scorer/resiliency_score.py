import json
import subprocess
from cpeparser import CpeParser
import os
import pandas as pd

### Make script to see if api is set, if not set it

def crit_score(json_file, cve):
    crit_score = 1  # Default score if not found
    endpoint_name = ''
    with open(json_file) as f:
        data = json.load(f)
        for crit in data['cves']:
            # Check if 'CVEs' key exists and if the CVE is in the list
            if 'CVEs' in crit and cve in crit['CVEs']:
                if crit.get('Criticality') == 'Critical':
                    return 3, crit.get('Endpoint Name')
                elif crit.get('Criticality') == 'Medium':
                    return 2, crit.get('Endpoint Name')
                elif crit.get('Criticality') == 'Low':
                    return 1, crit.get('Endpoint Name')
                else:
                    return 1, crit.get('Endpoint Name')
    return crit_score, ""
    


def csv_to_json(csv_file, json_file):
    df = pd.read_csv(csv_file)
    
    # Function to parse CVEs
    def parse_cves(row):
        cves = []
        for col in row.index:
            if col.startswith('Unnamed:') and isinstance(row[col], str):
                for cve_entry in row[col].split(','):
                    cve_entry = cve_entry.strip()
                    if cve_entry.startswith(('CVE-', 'CVD-')):
                        cve_id = cve_entry.split(';')[0].strip()
                        # Change 'CVD' to 'CVE' if present
                        if cve_id.startswith('CVD-'):
                            cve_id = 'CVE-' + cve_id[4:]
                        cves.append(cve_id)
        return cves if cves else None

    # Apply the parsing function and create a new 'CVEs' column
    df['CVEs'] = df.apply(parse_cves, axis=1)
    
    # Drop all unnamed columns
    df = df.drop(columns=[col for col in df.columns if col.startswith('Unnamed:')])
    
    # Remove rows where all values are null
    df = df.dropna(how='all')
    
    # Remove rows where the 'CVEs' column is null
    df = df[df['CVEs'].notna()]
    
    # Convert to a list of dictionaries
    cves_list = df.to_dict(orient='records')
    
    # Create a dictionary with 'cves' as the key
    cves_dict = {'cves': cves_list}
    
    # Save to JSON
    with open(json_file, 'w') as f:
        json.dump(cves_dict, f, indent=4)

    

def run_cve_scan(cve_file, json_file_name):
    #json_file_name = args.json_file
    # Run cve_prioritizer.py to generate .json file
    subprocess.run(["python3", "CVE_Prioritizer/cve_prioritizer.py", "-j", json_file_name, "-vc", "-vck", "-v", "-t 100" , "-f", cve_file])
    


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
    

def all_json_to_sw_hw_json(json_file, crit_csv_file):
    csv_to_json(crit_csv_file, 'crit.json')
    cpe = CpeParser()
    with open(json_file) as f:
        data = json.load(f)

        # Load existing data from sw_cves.json if it exists
        try:
            with open('sw_cves.json') as sw_f:
                sw_data = json.load(sw_f)
        except FileNotFoundError:
            sw_data = {'cves': []}
        try:
            with open('hw_cves.json') as hw_f:
                hw_data = json.load(hw_f)
        except FileNotFoundError:
            hw_data = {'cves': []}
            
        hw_overall_resiliency_score = float(0)
        sw_overall_resiliency_score = float(0)
        sw_i = 0
        hw_i = 0
        for cve in data['cves']:
            cpe_string = cve['cpe']
            cpe_parsed = cpe.parser(cpe_string)
            cpe_to_json = all_cpe(cpe_parsed)
            cvss_vector_description = parse_cvss_vector(cve['vector'])
            type = type_of_vuln_cpe(cpe_parsed)
            if type == 'Operating System' or type == 'Application':
                cve['criticality'], cve['endpoint_name'] = crit_score('crit.json', cve['cve_id'])
                resiliency_score = (100 - cve['cvss_base_score'] * 10)/cve['criticality']
                
                cve['resiliency_score'] = resiliency_score
                cve['cpe_full'] = cpe_to_json
                cve['cvss_vector_description'] = cvss_vector_description
                sw_data['cves'].append(cve)
                sw_overall_resiliency_score += resiliency_score
                sw_i += 1
            elif type == 'Hardware':
                cve['criticality'], cve['endpoint_name'] = crit_score('crit.json', cve['cve_id'])
                resiliency_score = (100 - cve['cvss_base_score'] * 10)/cve['criticality']
                cve['resiliency_score'] = resiliency_score
                cve['cpe_full'] = cpe_to_json
                hw_data['cves'].append(cve)
                hw_overall_resiliency_score += resiliency_score
                hw_i += 1
        if sw_i > 0:
            sw_overall_resiliency_score = sw_overall_resiliency_score / sw_i
            sw_data['overall_resiliency_score'] = sw_overall_resiliency_score
            # Write the updated data back to sw_cves.json
            with open('sw_cves.json', 'w') as sw_f:
                json.dump(sw_data, sw_f, indent=4)
        if hw_i > 0:
            hw_overall_resiliency_score = hw_overall_resiliency_score / hw_i
            hw_data['overall_resiliency_score'] = hw_overall_resiliency_score
            # Write the updated data back to sw_cves.json
            with open('hw_cves.json', 'w') as hw_f:
                json.dump(hw_data, hw_f, indent=4)


def check_and_remove_previous_files(sw_file, hw_file):
    if os.path.exists(sw_file):
        os.remove(sw_file)
    if os.path.exists(hw_file):
        os.remove(hw_file)
