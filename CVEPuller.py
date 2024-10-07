# Function to extract lines containing 'CVE'
def extract_cve_lines(input_file, output_file):
    try:
        with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
            for line in infile:
                if 'CVE' in line:
                    # Find the position of 'C' in 'CVE' and the first occurrence of ':'
                    start_index = line.find('CVE')
                    end_index = line.find(';', start_index)
                    
                    # If both 'CVE' and ':' are found, extract and write the substring
                    if start_index != -1 and end_index != -1:
                        cve_content = line[start_index:end_index]
                        outfile.write(cve_content + '\n')
                        print(cve_content)  # Optional: Print to console
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")

# Example usage
input_file_path = 'home/Documents/Github/classified_output/Software.txt' # Replace with your input file path
output_file_path = 'home/Documents/Github/classified_output/CVEOnly.txt'  # Replace with your output file path

extract_cve_lines(input_file_path, output_file_path)
