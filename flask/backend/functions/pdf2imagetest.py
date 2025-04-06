import os
from PIL import Image as PILImage
import pandas as pd
from pdf2image import convert_from_path
from pytesseract import image_to_string
from img2table.document.image import Image
from img2table.ocr import TesseractOCR
import cv2
import re

# Function to convert PDF pages to images
def pdf_to_image(directory, pdf_path):
    images = convert_from_path(pdf_path)
    for i, image in enumerate(images):
        # Save each page as an image
        image.save(os.path.join(directory, f'image_{i}.png'), 'PNG')

# Function to extract text from images using OCR
def extract_text_from_images(directory):
  text_file = os.path.join(directory, 'run.txt')
  for filename in os.listdir(directory):
    if filename.endswith('.png'):
      file_path = os.path.join(directory, filename)
      image = PILImage.open(file_path)
      text = image_to_string(image)
      with open(text_file, 'a') as file:
        file.write(text)

# Function to extract tables using Camelot for PDF and Img2table for PNG
def extract_tables_from_images(directory):
    for filename in os.listdir(directory):
        if filename.endswith('.png'):
            file_path = os.path.join(directory, filename)

            try:
                # Load the image with OpenCV and verify it
                img = cv2.imread(file_path)
                if img is None:
                    print(f"Error: Failed to load image {file_path}")
                    continue
                
                # Initialize the document and OCR engine
                doc = Image(file_path)
                ocr_engine = TesseractOCR()
                
                # Extract the tables from the image
                extracted_tables = doc.extract_tables(ocr=ocr_engine)

                # Loop through each extracted table
                for i, table in enumerate(extracted_tables):
                    #print(f"Bounding box coordinates: {table.bbox.x1}, {table.bbox.y1}, {table.bbox.x2}, {table.bbox.y2}")

                    # Check if the extracted table has a DataFrame representation
                    if hasattr(table, 'df'):
                        df = table.df  # Assuming df is a pandas DataFrame

                        # Create a unique filename based on the image filename and table index
                        output_filename = f"{os.path.splitext(filename)[0]}_table_{i}.csv"
                        output_path = os.path.join(directory, output_filename)

                        # Save the DataFrame to a CSV file with a unique name
                        df.to_csv(output_path, index=False)
                        #print(f"Table saved to {output_path}")
                    else:
                        print(f"Error: No DataFrame found for table {i} in {file_path}")

            except Exception as e:
                print(f"Error extracting tables with img2table: {e}")

def extract_cves(input_file, output_file):
    cve_pattern = re.compile(r'(CVE-\d{4}-\d+|CVD-\d{4}-\d+)')
    unique_cves = set()
    
    with open(input_file, 'r', encoding='utf-8') as infile:
        for line in infile:
            matches = cve_pattern.findall(line)
            for match in matches:
                # Convert CVD to CVE if necessary
                if match.startswith('CVD-'):
                    match = 'CVE-' + match[4:]
                unique_cves.add(match)
    
    # Write unique CVEs to output file
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for cve in sorted(unique_cves):
            outfile.write(cve + '\n')

# Main function to run all processes
def process_pdf_to_tables(directory, pdf_path):
    # Step 1: Convert PDF pages to images
    pdf_to_image(directory, pdf_path)

    # Step 2: Extract text from the images using Tesseract
    extract_text_from_images(directory)

    # Step 3: Extract tables using Img2Table
    extract_tables_from_images(directory)

def delete_data_directory(directory_path):
    # Check if the provided path is a directory
    if os.path.isdir(directory_path):
        # Loop through all items in the directory
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            # Check if it's a file and then delete it
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted: {file_path}")
            else:
                print(f"Skipped (not a file): {file_path}")
    else:
        print(f"The provided path '{directory_path}' is not a valid directory.")
    
