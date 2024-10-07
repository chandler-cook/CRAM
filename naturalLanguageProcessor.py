import os
from transformers import pipeline

# Define the paths to the classified text files
txt_file_paths = {
    "Software": "classified_output/Software.txt",
    "Hardware": "classified_output/Hardware.txt",
    "Physical": "classified_output/Physical.txt"
}

# Define a function to process the classified text files
def process_and_filter_text(file_path, output_dir="filtered_output"):
    # Read the text content from the file
    with open(file_path, "r", encoding="utf-8") as file:
        text_data = file.readlines()

    # Initialize the summarization model
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn", device=0)

    # Filter out empty lines and summarize each piece of text
    filtered_text = []
    for paragraph in text_data:
        if paragraph.strip():  # Skip empty lines
            summary = summarizer(paragraph.strip(), max_length=100, min_length=30, do_sample=False)
            filtered_text.append(summary[0]["summary_text"] + "\n")

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Save the filtered text to a new file
    base_name = os.path.basename(file_path)
    output_file_path = os.path.join(output_dir, f"filtered_{base_name}")
    with open(output_file_path, "w", encoding="utf-8") as output_file:
        output_file.writelines(filtered_text)

    print(f"Filtered text saved to {output_file_path}")

# Process each of the classified text files
for label, file_path in txt_file_paths.items():
    process_and_filter_text(file_path)

        category = classify_text(summary)
        classified_text[category].append(summary)

    # Save classified text into separate files
    for label, content in classified_text.items():
        filtered_filename = get_filtered_filename(file_path, label, output_dir)
        os.makedirs(output_dir, exist_ok=True)  # Create directory if it doesn't exist
        with open(filtered_filename, "w", encoding="utf-8") as output_file:
            output_file.writelines("\n".join(content) + "\n")

    print(f"Summarized and classified text saved into separate files in '{output_dir}'.")


txt_file_path = "final_output_with_text_images_tables_cogvlm2.txt"  # Replace with your file path
process_and_classify_text(txt_file_path)
txt_file_path = "final_output_with_text_images_tables_cogvlm2.txt"  # Replace with your file path
process_and_classify_text(txt_file_path)
