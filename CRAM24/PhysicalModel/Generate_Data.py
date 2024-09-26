import json
from itertools import combinations

def read_jsonl(file_path):
    """Read JSON Lines file and return a list of dictionaries."""
    with open(file_path, 'r') as file:
        return [json.loads(line) for line in file]

def create_new_responses(variations, responses):
    """Create new responses starting with the phrase 'Score this system:' with spaces between combined statements."""
    new_entries = []
    
    for i in range(len(variations)):
        for j in range(len(variations)):
            if i != j:
                # Combine prompts with a comma and space in between
                combined_prompt = f"{variations[i]}, {variations[j]}"
                new_prompt = f"Score this system: {combined_prompt}"
                
                # Assuming both responses are numeric, convert to int or float for addition
                new_response = responses[i] + responses[j]
                new_entries.append({
                    'prompt': new_prompt,
                    'response': new_response
                })
    
    return new_entries

def save_to_jsonl(data, file_path):
    """Save list of responses to a JSON Lines file."""
    with open(file_path, 'w') as file:
        for item in data:
            file.write(json.dumps(item) + '\n')

def main():
    input_file = 'my_dataset.jsonl'
    output_file = 'new_dataset.jsonl'

    # Step 1: Read the dataset
    dataset = read_jsonl(input_file)

    # Assume the dataset has a 'prompt' and 'response' field
    prompts = [item['prompt'] for item in dataset]
    responses = [int(item['response']) for item in dataset]  # Convert responses to integers

    # Step 2: Create new responses
    new_responses = create_new_responses(prompts, responses)

    # Step 3: Save new responses
    save_to_jsonl(new_responses, output_file)

if __name__ == "__main__":
    main()
