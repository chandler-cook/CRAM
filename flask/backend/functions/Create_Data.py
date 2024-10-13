import random

def load_lines(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
    return lines

def parse_lines(lines):
    parsed_lines = []
    current_text = ""
    for line in lines:
        line = line.strip()
        if line.startswith("Score:"):
            score = int(line.split("Score:")[1].strip())
            parsed_lines.append((current_text, score))
            current_text = ""
        elif line:
            # Collecting the description
            if current_text:
                current_text += " " + line
            else:
                current_text = line
    return parsed_lines

def create_combined_lines(parsed_lines, num_lines_to_combine, num_new_lines):
    combined_lines = []
    
    for _ in range(num_new_lines):
        selected_lines = random.sample(parsed_lines, num_lines_to_combine)
        
        # Combine the text content with a comma and space for each item
        combined_text = ', '.join(line[0] for line in selected_lines)
        # Calculate the average score, rounded to the nearest integer
        average_score = round(sum(line[1] for line in selected_lines) / num_lines_to_combine)
        combined_lines.append((combined_text, average_score))
    
    return combined_lines

def write_combined_lines(filename, combined_lines):
    with open(filename, 'w') as file:
        for text, score in combined_lines:
            file.write(f"{text}\nScore: {score}\n\n")  # Score on a new line

def main():
    input_filename = 'formatted_vault.txt'  # Replace with your input filename
    output_filename = 'combined_output.txt'  # Replace with your desired output filename
    num_lines_to_combine = 10  # Adjust as needed for the number of descriptions per line
    num_new_lines = 500  # Adjust as needed for the number of new combined lines
    
    lines = load_lines(input_filename)
    parsed_lines = parse_lines(lines)

    # Check if there are enough lines to combine
    if num_lines_to_combine > len(parsed_lines):
        print(f"Error: You requested to combine {num_lines_to_combine} lines, but only {len(parsed_lines)} lines are available.")
        return

    combined_lines = create_combined_lines(parsed_lines, num_lines_to_combine, num_new_lines)
    write_combined_lines(output_filename, combined_lines)
    print(f"{num_new_lines} new combined lines created and saved to {output_filename}")

if __name__ == "__main__":
    main()
