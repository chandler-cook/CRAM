import random

# Function to read prompts and scores from a file
def read_prompts_from_file(input_file):
    prompts = []
    with open(input_file, 'r') as file:
        lines = [line.strip() for line in file.readlines() if line.strip()]  # Remove empty lines
        for i in range(0, len(lines), 2):
            prompt = lines[i].strip()  # Prompt line
            # Ensure there is a score line after the prompt
            if i + 1 < len(lines):
                score_line = lines[i + 1].strip()
                # Check if the score line starts with 'Score:'
                if score_line.startswith("Score:"):
                    try:
                        score = int(score_line.split(': ')[1].strip())  # Extract score
                        prompts.append((prompt, score))
                    except ValueError:
                        print(f"Invalid score format in line: {score_line}")
                else:
                    print(f"Missing 'Score:' in line: {score_line}")
            else:
                print(f"Missing score for prompt: {prompt}")
    return prompts

# Function to create a combined prompt
def create_combined_prompt(prompts, num_prompts):
    # Randomly choose 'num_prompts' prompts from the list
    selected_prompts = random.sample(prompts, num_prompts)
    
    # Combine the selected prompts into one string separated by commas
    combined_prompt = ', '.join([prompt for prompt, score in selected_prompts])
    
    # Calculate the average score of the selected prompts
    avg_score = sum([score for prompt, score in selected_prompts]) / num_prompts
    
    # Round the average score
    rounded_score = round(avg_score)
    
    return combined_prompt, rounded_score

# Function to append multiple combined prompts and scores to a new file
def append_combined_prompts_to_new_file(output_file, prompts, num_prompts, num_lines):
    with open(output_file, 'w') as file:  # Open in write mode for the new file
        for _ in range(num_lines):
            combined_prompt, rounded_score = create_combined_prompt(prompts, num_prompts)
            file.write(f"{combined_prompt}\n")
            file.write(f"Score: {rounded_score}\n\n")  # Write the rounded score

# Main function
if __name__ == "__main__":
    # Input file with prompts and scores
    input_file = 'DataTraining.txt'
    
    # Output file where the combined prompts and scores will be written
    output_file = 'CombinedPrompts.txt'
    
    # Number of prompts to combine per line
    num_prompts = 200
    
    # Number of combined prompts to generate
    num_lines = 5000  # Change this to however many combined lines you want
    
    # Read prompts and scores from the input file
    prompts = read_prompts_from_file(input_file)
    
    # Append multiple combined prompts and scores to the new output file
    append_combined_prompts_to_new_file(output_file, prompts, num_prompts, num_lines)
    
    print(f"{num_lines} combined prompts written to {output_file}")
