# Install required packages
# pip install transformers torch

from transformers import pipeline

# Initialize the Zero-Shot Classification model
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Define the labels for classification
labels = ["Software", "Hardware", "Physical"]

# Read the .txt file content
def read_txt_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.readlines()

# Classify text into categories and save into separate files
def classify_and_save_text(file_path, output_dir="classified_output"):
    text_data = read_txt_file(file_path)

    # Create dictionaries to store classified text
    classified_text = {
        "Software": [],
        "Hardware": [],
        "Physical": []
    }

    # Process each line or paragraph in the text
    for paragraph in text_data:
        if len(paragraph.strip()) == 0:
            continue

        # Get classification result for the paragraph
        classification = classifier(paragraph, labels)

        # Identify the highest scoring label
        best_label = classification["labels"][0]
        classified_text[best_label].append(paragraph)

    # Write classified text to separate files
    for label, content in classified_text.items():
        output_file_path = f"{output_dir}/{label}.txt"
        os.makedirs(output_dir, exist_ok=True)  # Create directory if it doesn't exist
        with open(output_file_path, "w", encoding="utf-8") as output_file:
            output_file.writelines(content)

    print(f"Text has been classified and saved into separate files in the {output_dir} folder.")

# Call the function with the updated .txt file path
txt_file_path = "final_output_with_text_images_tables_cogvlm2.txt"
classify_and_save_text(txt_file_path)
