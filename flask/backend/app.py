from flask import Flask, request, jsonify, render_template
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import time
from functions.pdf2imagetest import *
from functions.pdf_processor import *
from functions.csv_formatter import *
from functions.resiliency_score import *
from functions.physical_line_indicator import *
from functions.physical_model import *
from functions.physical_suggestions import *

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
    
    output_path = os.path.join(app.root_path, 'static/data')
    filename = f"{project_name}_{pdf_file.filename}"

    pdf_path = os.path.join(output_path, filename)
    pdf_file.save(os.path.join(output_path, filename))

    pdf_bytes = pdf_file.read()

    # Deletes previous runs
    sw_json = os.path.join(output_path, 'sw_cves.json')
    hw_json = os.path.join(output_path, 'hw_cves.json')
    delete_txt_files(output_path)
    delete_csv_files(output_path)
    delete_json_files(output_path)

    pdf_to_image(output_path, pdf_path)
    '''
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

    initial_csv = os.path.join(output_path, 'initial_cve.csv')
    generate_csv(initial_csv)

    matched_files = check_criticality(output_path, matched_files)

    processed_list = process_csvs(matched_files, processed_list)

    cve_files = search_csvs(output_path)

    for x in processed_list:
        assign_criticality(x, initial_csv)

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
        append_matching(initial_csv, x)

    final_csv = os.path.join(output_path, 'final_cve.csv')
    process_csv2(initial_csv, final_csv)

    #
    # SCORING SECTION
    #

    cve_prioritizer = os.path.join(app.root_path, 'functions/CVE_Prioritizer/cve_prioritizer.py')
    cve_json = os.path.join(output_path, 'all_cves.json')
    cve_scan(cve_prioritizer, cve_file, cve_json)
    sw_score, hw_score = convert_to_json(output_path, cve_json, final_csv)

    static_path = os.path.join(app.root_path, 'static/')
    physical_path = os.path.join(output_path, 'Physical.txt')
    physical_score = physical_main(static_path, physical_path)
    if physical_score is not None:
        print(physical_score)
    else:
        print('No score could be calculated')

    resiliency_score = (sw_score + hw_score + physical_score) / 3
    #rounded_score = round(resiliency_score)
    '''


    torch.cuda.empty_cache() # Clearing cache

    model_name = "llama3" # Defining the name of the model being used
    run_path = os.path.join(output_path, 'run.txt') #Defining the path to the file that contains all of the text extracted from the pdf
    phy_txt_path = os.path.join(output_path, 'physical_output.txt') # Defining the path of the text file that contains the physical policy to be scored

    physical_suggestions_rag = os.path.join(output_path, 'suggestions_vault.txt') # Path for the two code files: finding the physcial policy and the giving improvements
    physical_vault_path = os.path.join(output_path, 'physical_vault.txt')

    torch.cuda.empty_cache() # Clearing cache to avoid GPU issues

    process_input_file(run_path, phy_txt_path, model_name) # This is the function that finds each line of text that is a physcial policy
    remove_unwanted_lines(phy_txt_path) # Cleaning up the text to be scored next

    # This is the call that gets the physical score
    time.sleep(2)  # Giving two seconds for the model to wait before reinitiating a connection
    physical_vault_path = os.path.join(output_path, 'physical_vault.txt')
    physical_score = localrag(phy_txt_path, physical_vault_path)
    
    print (physical_score)


    time.sleep(2) # Giving two seconds for the model to wait before reinitiating a connection
    #torch.cuda.empty_cache() # Clearing cache to avoid GPU issues

    physical_suggestions = os.path.join(output_path, "suggestions.txt")
    # This is the function that calls the model and finds suggestions to physical policy
    process_file(phy_txt_path, physical_suggestions, model_name, physical_suggestions_rag)

    # Functions to clean up the suggestions text.
    remove_lines(physical_suggestions)
    remove_double_asterisks(physical_suggestions)


    return jsonify({
        "project_name": project_name,
        "resiliency_score": int(resiliency_score),
        "sw_score": sw_score,
        "hw_score": hw_score,
        "physical_score": physical_score
    }), 200
    

@app.route('/software')
def software():

    sw_path = os.path.join(app.root_path, 'static/data/sw_cves.json')
    with open(sw_path, 'r') as file:
        cve_data = json.load(file)
    return jsonify(cve_data)

if __name__ == '__main__':
    app.run(debug=True)
    torch.cuda.empty_cache()
    torch.cuda.ipc_collect()
