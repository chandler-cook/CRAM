import os
from transformers import pipeline
import torch
from datasets import Dataset

# Initialize the Zero-Shot Classification model
device = 0 if torch.cuda.is_available() else -1  # 0 for GPU, -1 for CPU
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli", device=device)

# Define the labels for classification
labels = ["Software", "Hardware", "Physical"]

# Read the .txt file content
def read_txt_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.readlines()

# Function to generate filtered filename based on the original filename
def get_filtered_filename(original_filename, label, output_dir):
    base_name, extension = os.path.splitext(original_filename)
    filtered_filename = f"{base_name}_{label}_filtered{extension}"
    return os.path.join(output_dir, filtered_filename)

# Modified function to classify and save text
def process_and_classify_text(file_path, output_dir="classified_output"):
    text_data = read_txt_file(file_path)
    
    # Filter out empty lines
    text_data = [paragraph.strip() for paragraph in text_data if paragraph.strip()]

    # Create a dataset object for more efficient processing
    dataset = Dataset.from_dict({"text": text_data})

    # Function to classify a single text
    def classify_text(batch):
        results = classifier(batch["text"], labels)
        batch["classification"] = [result["labels"][0] for result in results]
        return batch

    # Apply the classification function to the dataset
    classified_dataset = dataset.map(classify_text, batched=True, batch_size=8)

    # Create dictionaries to store classified text
    classified_text = {
        "Software": [],
        "Hardware": [],
        "Physical": []
    }

    # Distribute classified text into corresponding categories
    for item in classified_dataset:
        classified_text[item["classification"]].append(item["text"])

    # Write classified text to separate files
    for label, content in classified_text.items():
        output_file_path = get_filtered_filename(file_path, label, output_dir)
        os.makedirs(output_dir, exist_ok=True)  # Create directory if it doesn't exist
        with open(output_file_path, "w", encoding="utf-8") as output_file:
            output_file.writelines(content)

    print(f"Filtered text has been saved into separate files in the {output_dir} folder.")

# Specify the path to the text files from the classified_output directory
txt_file_paths = [
    "classified_output/Hardware.txt",
    "classified_output/Software.txt",
    "classified_output/Physical.txt"
]

# Process and classify each file
for txt_file_path in txt_file_paths:
    process_and_classify_text(txt_file_path)
