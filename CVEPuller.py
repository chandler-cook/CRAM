import re

# Function to extract every CVE instance in a line
def extract_cve_lines(input_file, output_file):
    try:
        with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
            line = infile.readline()
            
            # Use a regular expression to find all instances of 'CVE-' followed by any characters until ':'
            matches = re.findall(r'(CVE-[^:]+):', line)
            
            # Write each match to the output file
            for match in matches:
                outfile.write(match + '\n')
                print(match)  # Optional: Print to console
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")

# Example usage
input_file_path = 'input.txt'  # Replace with your input file path
output_file_path = 'output.txt'  # Replace with your output file path

# Example usage
input_file_path = 'home/Documents/Github/classified_output/Software.txt' # Replace with your input file path
output_file_path = 'home/Documents/Github/classified_output/CVEOnly.txt'  # Replace with your output file path

extract_cve_lines(input_file_path, output_file_path)
