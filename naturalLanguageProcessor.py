import os

# Function to append "_filtered" to the original filename
def get_filtered_filename(original_filename, label, output_dir):
    base_name, extension = os.path.splitext(original_filename)
    filtered_filename = f"{base_name}_{label}_filtered{extension}"
    return os.path.join(output_dir, filtered_filename)

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
