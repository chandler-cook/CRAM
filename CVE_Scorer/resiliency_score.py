import json
import subprocess
from cpeparser import CpeParser
import argparse
import os


### Make script to see if api is set, if not set it



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
    
    # Initialize a list to hold the descriptions
    description_list = []
    
    # Iterate over each part and construct the descriptions
    for part in parts:
        if ':' not in part:  # Ensure the part contains a colon
            continue  # Skip this part if it's not valid
        
        code, value = part.split(':', 1)  # Split by the colon
        
        if code in descriptions and value in descriptions[code]:
            full_name = full_names.get(code, code)  # Get the full name
            description = descriptions[code][value]
            description_list.append(f"\t{full_name}:\n\t\t{description}")
    
    # Join all descriptions into a single string
    return '\n'.join(description_list)


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

def all_json_to_sw_hw_json(json_file):
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
            print(cpe_parsed)
            type = type_of_vuln_cpe(cpe_parsed)
            if type == 'Operating System' or type == 'Application':
                resiliency_score = 100 - cve['cvss_base_score'] * 10
                cve['resiliency_score'] = resiliency_score
                sw_data['cves'].append(cve)
                sw_overall_resiliency_score += resiliency_score
                sw_i += 1
            elif type == 'Hardware':
                resiliency_score = 100 - cve['cvss_base_score'] * 10
                cve['resiliency_score'] = resiliency_score
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


#def main_res_score_program(cve_file, json_file):
#if __name__ == '__main__':
    # Run cve_prioritizer.py to generate .json file
    #parser = argparse.ArgumentParser(description="Program to calculate resiliency score.")
    #parser.add_argument("-j", "--json_file", type=str, required = True, help="The json file name containing the list of CVEs to process.")
    #parser.add_argument("-f ", "--cve_file", type=str, required = True, help="The file containing the list of CVEs to process.")
    #args = parser.parse_args()
    #check_and_remove_previous_files('sw_cves.json', 'hw_cves.json')
    #run_cve_scan(cve_file, json_file)    
    #all_json_to_sw_hw_json(json_file)
    #if os.path.exists(json_file):
    #    os.remove(json_file)

            
#main_res_score_program("testCVE", "all_cves.json")
            


   
    
