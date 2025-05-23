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
from functions.new_apt import *

import torch

app = Flask(__name__)

filename = None

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
    global filename
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

    static_path = os.path.join(app.root_path, 'static/')
    csv_path = checkName(static_path, filename)
    new_csv = os.path.join(output_path, 'updated_table.csv')
    csv(csv_path, new_csv)

    #
    # SCORING SECTION
    #

    cve_prioritizer = os.path.join(app.root_path, 'functions/CVE_Prioritizer/cve_prioritizer.py')
    cve_json = os.path.join(output_path, 'all_cves.json')
    cve_scan(cve_prioritizer, cves_path, cve_json)
    sw_score, hw_score = convert_to_json(output_path, cve_json, new_csv)

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
    phy_txt_path = os.path.join(output_path, 'physical_output.txt')
    physical_vault_path = os.path.join(app.root_path, 'static/physical_vault.txt')

    process_input_file(run_path, phy_txt_path, model_name) # This is the function that finds each line of text that is a physical policy
    time.sleep(5)

    # This is the call that gets the physical score
    physical_score = localrag(phy_txt_path, physical_vault_path)
    
    resiliency_score = (sw_score + final_hw_score + physical_score) / 3

    return jsonify({
        "project_name": project_name,
        "resiliency_score": int(resiliency_score),
        "sw_score": sw_score,
        "hw_score": final_hw_score,
        "physical_score": physical_score
    }), 200
    
@app.route('/software', methods=['GET', 'POST'])
def software():

    output_path = os.path.join(app.root_path, 'static/data')
    cves_path = os.path.join(output_path, 'extracted_cves.txt')
    cve_prioritizer = os.path.join(app.root_path, 'functions/CVE_Prioritizer/cve_prioritizer.py')
    cve_json = os.path.join(output_path, 'all_cves.json')
    sw_json = os.path.join(output_path, 'sw_cves.json')
    final_csv = os.path.join(output_path, 'final_cve.csv')

    if request.method == 'POST':
        data = request.get_json()  # Parse JSON from the request
        cve_ids = data.get('cve_ids')  # Extract the array of CVE IDs
        
        if not cve_ids or not isinstance(cve_ids, list):
            return jsonify({'error': 'CVE IDs not provided or incorrect format'}), 400

        try:
            # Read the contents of extracted_cves.txt
            with open(cves_path, 'r') as file:
                lines = file.readlines()

            # Filter out the resolved CVE(s) from the file
            with open(cves_path, 'w') as file:
                for line in lines:
                    # Keep the line only if none of the cve_ids are in the line
                    if not any(cve_id in line for cve_id in cve_ids):
                        file.write(line)

            if os.path.exists(sw_json):
                os.remove(sw_json)
            
            cve_scan(cve_prioritizer, cves_path, cve_json)
            sw_score, hw_score = convert_to_json(output_path, cve_json, final_csv)

            # Step 3: Return a success response after the CVEs have been removed
            return jsonify({
                'message': f'CVEs {cve_ids} removed successfully',
                'software_score': sw_score
            }), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    elif request.method == 'GET':
        sw_path = os.path.join(output_path, 'sw_cves.json')
        with open(sw_path, 'r') as file:
            cve_data = json.load(file)
        return jsonify(cve_data)

@app.route('/physical', methods=['POST'])
def physical():

    data = request.get_json()

    # Extract the policy text from the request
    policy_text = data.get('policy', '')

    if not policy_text:
        return jsonify({"error": "No policy text provided"}), 400

    # Here you can handle the policy text, e.g., save it to a file or database
    # For example, saving it to a file called policies.txt:
    try:
        policy_file_path = os.path.join(app.root_path, 'static/data', 'policies.txt')
        with open(policy_file_path, 'a') as f:
            f.write(policy_text + '\n')  # Append the policy to the file
        
        # Respond with success
        return jsonify({"message": "Policy added successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/apts', methods=['POST'])
def apts():

    data = request.get_json()
    checked_apts = data.get("checked_apts", [])

    # Get the current scores sent from the frontend
    current_overall = int(data.get("current_overall", 0))
    current_sw_score = int(data.get("current_sw_score", 0))
    current_hw_score = int(data.get("current_hw_score", 0))
    current_phy_score = int(data.get("current_phy_score", 0))
    print(current_overall, current_sw_score, current_hw_score, current_phy_score)

    hardware = 0
    physical = 0
    software = 0

    apts_path = os.path.join(app.root_path, 'static/apts')
    for x in checked_apts:
        tmp_directory = f"{apts_path}/{x}-Profile.txt"
        hardware, software, physical = process_directory(tmp_directory)

    score_s, score_p, score_h = makeNewScore(hardware, software, physical)
    
    # Add the new scores to the current scores
    final_sw_score = current_sw_score + score_s
    final_hw_score = current_hw_score + score_h
    final_phy_score = current_phy_score + score_p
    final_resiliency_score = (final_sw_score + final_hw_score + final_phy_score) / 3

    return jsonify({
        "overall_score": int(final_resiliency_score),
        "sw_score": final_sw_score,
        "hw_score": final_hw_score,
        "phy_score": final_phy_score
    }), 200

@app.route('/new_apt', methods=['POST'])
def new_apt():
    
    data = request.json
    apt_name = data.get('apt_name')
    apt_behavior = data.get('apt_behavior')
    apt_db = os.path.join(app.root_path, 'static/apts')
    apt_list = os.path.join(apt_db, 'APT-List.txt')
    phys_vault = os.path.join(app.root_path, 'static/physical_vault.txt')

    if not apt_name or not apt_behavior:
        return jsonify({"error": "APT name and behavior are required"}), 400
    
    try:
        # Call New_APT to save the APT behavior
        New_APT(apt_db, apt_name, apt_behavior, phys_vault)

        # Append the APT name to the APT-List.txt file
        with open(apt_list, 'a') as file:
            file.write(f"{apt_name}\n")
        
        # If everything was successful, return a success message
        return jsonify({"message": "APT added successfully"}), 200

    except Exception as e:
        # If there's an error, return an error message and log the exception
        print(f"Error processing APT: {e}")
        return jsonify({"error": "Failed to process new APT"}), 500
    
@app.route('/change_criticality', methods=['POST'])
def change_criticality():
    
    static_path = os.path.join(app.root_path, 'static')
    csv_path = checkName(static_path, filename)
    output_path = os.path.join(app.root_path, 'static/data')
    copy_path = os.path.join(output_path, 'copied.csv')
    changeCrit(csv_path, copy_path)

    csv_output = os.path.join(output_path, 'copied2.csv')
    csv(copy_path, csv_output)

    sw_json = os.path.join(output_path, 'sw_cves.json')
    if os.path.exists(sw_json):
        os.remove(sw_json)
    
    cves_path = os.path.join(output_path, 'extracted_cves.txt')
    cve_prioritizer = os.path.join(app.root_path, 'functions/CVE_Prioritizer/cve_prioritizer.py')
    cve_json = os.path.join(output_path, 'all_cves.json')
    sw_json = os.path.join(output_path, 'sw_cves.json')

    cve_scan(cve_prioritizer, cves_path, cve_json)
    sw_score, hw_score = convert_to_json(output_path, cve_json, csv_output)

    # Return a success response
    return jsonify({sw_score})


if __name__ == '__main__':
    app.run(debug=True)
    torch.cuda.empty_cache()
    torch.cuda.ipc_collect()
