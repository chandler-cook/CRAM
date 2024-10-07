import os
from datetime import datetime

# Function to ensure unique filenames by appending timestamp
def get_unique_filename(filename, output_dir):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Adds timestamp to filename
    base_name, extension = os.path.splitext(filename)
    unique_filename = f"{base_name}_{timestamp}{extension}"
    return os.path.join(output_dir, unique_filename)

# Modified function to classify and save text
def process_and_classify_text(file_path, output_dir="classified_output"):
    text_data = read_txt_file(file_path)
    
    # Filter out empty lines
    text_data = [paragraph.strip() for paragraph in text_data if paragraph.strip()]

    # Initialize storage for classified text
    classified_text = {
        "Software": [],
        "Hardware": [],
        "Physical": []
    }

    # Process each text (summarize and classify)
    for paragraph in text_data:
        summary = summarize_text(paragraph)
        category = classify_text(summary)
        classified_text[category].append(summary)

    # Save classified text into separate files with unique names
    for label, content in classified_text.items():
        filename = f"{label}.txt"  # Base filename (e.g., Software.txt, Hardware.txt)
        unique_filename = get_unique_filename(filename, output_dir)
        os.makedirs(output_dir, exist_ok=True)  # Create directory if not exists
        with open(unique_filename, "w", encoding="utf-8") as output_file:
            output_file.writelines("\n".join(content) + "\n")

    print(f"Summarized and classified text saved into separate files in '{output_dir}'.")

txt_file_path = "final_output_with_text_images_tables_cogvlm2.txt"  # Replace with your file path
process_and_classify_text(txt_file_path)
txt_file_path = "final_output_with_text_images_tables_cogvlm2.txt"  # Replace with your file path
process_and_classify_text(txt_file_path)
