from flask import Flask, request, jsonify
from functions.pdf_processor import extract_text, extract_images, cogvlm2_description

app = Flask(__name__)

@app.route('/analyze', methods=['POST'])
def analyze():

    # Check if a file is uploaded
    if 'pdf' not in request.files:
        return jsonify({"error": "No PDF file provided"}), 400

    pdf_file = request.files['pdf']
    project_name = request.form.get('projectName')

    # Ensure a project name was provided
    if not project_name:
        return jsonify({"error": "Project name is required"}), 400

    # Ensure a file was selected
    if pdf_filefile.filename == '':
        return jsonify({"error": "No file selected"}), 400

    # Ensure file is a PDF
    if not pdf_file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Invalid file type. Please upload a PDF'}), 400

    # Extract text from PDF
    extracted_text = extract_text(pdf_file)

    # Extract images from PDF
    extracted_images = extract_images(pdf_file)

    # Generate descriptions of images
    image_descriptions = [cogvlm2_description(img.getvalue()) for img in extracted_images]

    return jsonify({
        "project_name": project_name,
        "extracted_text": extracted_text,
        "image_descriptions": image_descriptions
    }), 200


if __name__ == '__main__':
    app.run(debug=True)
