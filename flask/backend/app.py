from flask import Flask, request, jsonify, render_template
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from functions.pdf_processor import *
from functions.csv_formatter import *
import torch

app = Flask(__name__)


# Setup device and torch type based on CUDA availability
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
TORCH_TYPE = torch.bfloat16 if torch.cuda.is_available() and torch.cuda.get_device_capability()[0] >= 8 else torch.float16

# Initialize the CogVLM2 Model for Image Descriptions
cogvlm2_model_path = "THUDM/cogvlm2-llama3-chat-19B"
cogvlm2_tokenizer = AutoTokenizer.from_pretrained(cogvlm2_model_path, trust_remote_code=True)
cogvlm2_model = AutoModelForCausalLM.from_pretrained(cogvlm2_model_path, torch_dtype=TORCH_TYPE, trust_remote_code=True).to(DEVICE).eval()

# Initialize the Zero-Shot Classification model
classifier_device = 0 if torch.cuda.is_available() else -1  # Specific device configuration for pipeline
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli", device=classifier_device)

# Define the labels for classification
labels = ["Software", "Hardware", "Physical"]

# Initialize the Summarization Model
summarizer_model_path = "facebook/bart-large-cnn"
summarizer_tokenizer = AutoTokenizer.from_pretrained(summarizer_model_path)
summarizer_model = AutoModelForSeq2SeqLM.from_pretrained(summarizer_model_path, torch_dtype=TORCH_TYPE).to(DEVICE).eval()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():

    #
    #  PDF Processing Section
    #

    # Check if a file is uploaded
    if 'pdf' not in request.files:
        return jsonify({"error": "No PDF file provided"}), 400

    pdf_file = request.files['pdf']
    project_name = request.form.get('projectName')

    # Ensure a project name was provided
    if not project_name:
        return jsonify({"error": "Project name is required"}), 400

    # Ensure a file was selected
    if pdf_file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    # Ensure file is a PDF
    if not pdf_file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Invalid file type. Please upload a PDF'}), 400

    pdf_bytes = pdf_file.read()

    output_path = os.path.join(app.root_path, 'static/data')

    # Extract text from PDF
    extracted_text = extract_text(pdf_bytes)

    # Extract images from PDF
    extracted_images = extract_images(pdf_bytes)

    extract_tables(output_path, pdf_bytes)

    # Generate descriptions of images
    image_descriptions = [cogvlm2_description(img.getvalue(), DEVICE, TORCH_TYPE, cogvlm2_tokenizer, cogvlm2_model) for img in extracted_images]

    #Join image descriptions into a single string, separated by newlines or any desired separator
    descriptions_text = "\n".join(image_descriptions)

    # Combine extracted text with image descriptions
    final_text = f"{extracted_text}\n{descriptions_text}"

    # Classify the combined text
    classify_text(output_path, final_text, classifier, labels)

    clean_text(output_path, DEVICE, summarizer_tokenizer, summarizer_model)

    cve_file = os.path.join(output_path, 'extracted_cves.txt')
    extract_cves(output_path, cve_file)

    #
    # CSV Section
    #

    matched_files = []
    processed_list = []
    cve_files = []

    final_csv = os.path.join(output_path, 'final_cve.csv')
    generate_csv(final_csv)

    matched_files = check_criticality(output_path, matched_files)

    processed_list = process_csvs(matched_files, processed_list)

    cve_files = search_csvs(output_path)

    for x in processed_list:
        assign_criticality(x, final_csv)

    count = 0
    final_cve_files = []
    for x in cve_files:
        modified_file = os.path.join(output_path, f"CVEModified{count}.csv")
        final_file = os.path.join(output_path, f"CVEFinal{count}.csv")
    
        last_empty(x, modified_file)
        first_empty(modified_file, final_file)
    
        # Append the final file path to cveFinalFiles
        final_cve_files.append(final_file)
    
        count += 1

    for x in final_cve_files:
        append_matching(final_csv, x)


    return jsonify({
        "project_name": project_name,
        "extracted_text": extracted_text,
        "image_descriptions": image_descriptions
    }), 200


if __name__ == '__main__':
    app.run(debug=True)
