# import module
from PIL import Image
from pdf2image import convert_from_path
import os
from pytesseract import pytesseract 

path_to_tesseract = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
directory_path = "C:\\Users\\jippy\\OneDrive\\Desktop\\CSC Work\\Cyber\\CRAM Data\\pdf2image\\"
# Store Pdf with convert_from_path function
images = convert_from_path("C:\\Users\\jippy\\Downloads\\Challenge_Smaller_System_Under_Evaluation_Rev_0.1.pdf", poppler_path = "C:\\Users\\jippy\\OneDrive\\Desktop\\CSC Work\\Cyber\\CRAM Data\\poppler-24.08.0\\Library\\bin")
textFile = 'insertFilePathHere'
for i in range(len(images)):
      # Save pages as images in the pdf
    images[i].save("C:\\Users\\jippy\\OneDrive\\Desktop\\CSC Work\\Cyber\\CRAM Data\\pdf2image\\page" + str(i) +'.jpg', 'JPEG')

for filename in os.listdir(directory_path):
        # Check if the file is a CSV file
        if filename.endswith('.jpg'):
            file_path = os.path.join(directory_path, filename)
            image = Image.open(file_path)
            pytesseract.tesseract_cmd = path_to_tesseract 
            text = pytesseract.image_to_string(image)
            with open(textFile, 'a') as file:
              file.write(text)