from flask import Flask, request, jsonify, render_template
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import time
from functions.pdf2imagetest import *
from functions.rotate import *
#from functions.pdf_processor import *
from functions.csv_formatter import *
from functions.resiliency_score import *
from functions.hardware_test import *
from functions.physical_line_indicator import *
from functions.physical_model import *
from functions.physical_suggestions import *
from functions.apt_scorer import *

import torch

app = Flask(__name__)

# Setup device and torch type based on CUDA availability
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
TORCH_TYPE = torch.bfloat16 if torch.cuda.is_available() and torch.cuda.get_device_capability()[0] >= 8 else torch.float16

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
        #print("No PDF file provided")
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
    
    # Creates /static/data
    output_path = os.path.join(app.root_path, 'static/data')
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # Deletes previous runs
    delete_data_directory(output_path)
    
    # Saves PDF to app files
    filename = f"{project_name}_{pdf_file.filename}"
    pdf_path = os.path.join(output_path, filename)
    try:
        pdf_file.save(pdf_path)
    except Exception as e:
        print(f"Error saving PDF: {e}")

    # Rotates PDF pages if necessary
    rotated_pdf = os.path.join(output_path, 'rotated.pdf')
    rotate_pdf_pages(pdf_path, rotated_pdf)

    # Creates run.txt and tables from PDF
    process_pdf_to_tables(output_path, rotated_pdf)

    run_path = os.path.join(output_path, 'run.txt')
    cves_path = os.path.join(output_path, 'extracted_cves.txt')
    extract_cves(run_path, cves_path)

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

    # Deletes previous runs
    #sw_json = os.path.join(output_path, 'sw_cves.json')
    #hw_json = os.path.join(output_path, 'hw_cves.json')


    cve_prioritizer = os.path.join(app.root_path, 'functions/CVE_Prioritizer/cve_prioritizer.py')
    cve_json = os.path.join(output_path, 'all_cves.json')
    cve_scan(cve_prioritizer, cves_path, cve_json)
    sw_score, hw_score = convert_to_json(output_path, cve_json, final_csv)

    hw_db = os.path.join(app.root_path, 'static/hw_db.csv')
    year_list = find_matches(run_path, hw_db)
    count_5_10 = 0
    count_10_20 = 0
    count_over_20 = 0
    hardwareScore = 0
    # Get the current year
    current_year = datetime.now().year
    for x in year_list:
        if (current_year - 10) < int(x) & (int(x) <= 5):
            count_5_10 += 1
        elif (current_year - 20 < int(x)) & (int(x) <= current_year - 10):
            count_10_20 += 1
        elif int(x) <= (current_year - 20):
            count_over_20 += 1

    hardwareScore += (count_5_10 * 2)
    hardwareScore += (count_10_20 * 5)
    hardwareScore += (count_over_20 * 20)

    final_hw_score = 100 - (hw_score + hardwareScore)

    torch.cuda.empty_cache() # Clearing cache
    model_name = "llama3" # Defining the name of the model being used
    #Defining the path to the file that contains all of the text extracted from the pdf
    phy_txt_path = os.path.join(output_path, 'physical_output.txt') # Defining the path of the text file that contains the physical policy to be scored

    physical_suggestions_rag = os.path.join(output_path, 'suggestions_vault.txt') # Path for the two code files: finding the physcial policy and the giving improvements
    physical_vault_path = os.path.join(output_path, 'physical_vault.txt')

    torch.cuda.empty_cache() # Clearing cache to avoid GPU issues

    process_input_file(run_path, phy_txt_path, model_name) # This is the function that finds each line of text that is a physcial policy\
    time.sleep(5)

    #remove_unwanted_lines(phy_txt_path) # Cleaning up the text to be scored next

    # This is the call that gets the physical score
    time.sleep(2)  # Giving two seconds for the model to wait before reinitiating a connection
    physical_vault_path = os.path.join(output_path, 'physical_vault.txt')
    physical_score = localrag(phy_txt_path, physical_vault_path)

    print(physical_score)
    

    process_file(phy_txt_path, physical_suggestions_rag, model_name, physical_vault_path)


    resiliency_score = (sw_score + hw_score + physical_score) / 3
    #time.sleep(2) # Giving two seconds for the model to wait before reinitiating a connection
    #torch.cuda.empty_cache() # Clearing cache to avoid GPU issues

    #physical_suggestions = os.path.join(output_path, "suggestions.txt")
    # This is the function that calls the model and finds suggestions to physical policy
    #process_file(phy_txt_path, physical_suggestions, model_name, physical_suggestions_rag)

    # Functions to clean up the suggestions text.
    #remove_lines(physical_suggestions)
    #remove_double_asterisks(physical_suggestions)

    return jsonify({
        "project_name": project_name,
        "resiliency_score": int(resiliency_score),
        "sw_score": sw_score,
        "hw_score": final_hw_score,
        "physical_score": physical_score
    }), 200
    
@app.route('/software')
def software():

    sw_path = os.path.join(app.root_path, 'static/data/sw_cves.json')
    with open(sw_path, 'r') as file:
        cve_data = json.load(file)
    return jsonify(cve_data)

@app.route('/apts', methods=['POST'])
def apts():

    data = request.get_json()
    checked_apts = data.get("checked_apts", [])

    hardware = 0
    physical = 0
    software = 0
    checked_apts = []

    apts_path = os.path.join(app.root_path, 'static/apts')
    for x in checked_apts:
        tmp_directory = f"{apts_path}{x}-Profile.txt"
        hardware, software, physical = process_directory(tmp_directory)

    score_s, score_p, score_h = makeNewScore(hardware, software, physical)

    return jsonify({
        "sw_score": score_s,
        "hw_score": score_h,
        "phy_score": score_p
    }), 200

if __name__ == '__main__':
    app.run(debug=True)
    torch.cuda.empty_cache()
    torch.cuda.ipc_collect()
