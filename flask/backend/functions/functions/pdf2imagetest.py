# import module
from PIL import Image
from pdf2image import convert_from_path
import os
from pytesseract import pytesseract 

#path_to_tesseract = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
#directory_path = "C:\\Users\\jippy\\OneDrive\\Desktop\\CSC Work\\Cyber\\CRAM Data\\pdf2image\\"
# Store Pdf with convert_from_path function
def pdf_to_image(directory, pdf_path):
  images = convert_from_path(pdf_path)
  text_file = os.path.join(directory, 'run.txt')
  for i in range(len(images)):
    # Save pages as images in the pdf
    images[i].save(os.path.join(directory, f'image{i}.png'), 'PNG')

  for filename in os.listdir(directory):
    # Check if the file is a CSV file
    if filename.endswith('.png'):
        file_path = os.path.join(directory, filename)
        image = Image.open(file_path)
        #pytesseract.tesseract_cmd = path_to_tesseract 
        text = pytesseract.image_to_string(image)
        with open(text_file, 'a') as file:
          file.write(text)