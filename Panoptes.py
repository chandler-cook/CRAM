
import COGwithCSVtables
import sorter
import CVEfromCSV
import naturalLanguageProcessor

def main():
    # Step 1: Run the natural language processor to clean the Physical.txt
    print("Running naturalLanguageProcessor.py...")
    physical_file_path = 'classified_output/Physical.txt'  # Update with correct path if necessary
    naturalLanguageProcessor.process_and_clean_physical_file(physical_file_path)

    # Step 2: Run the CogVLM2 for image descriptions and extract tables and text
    print("Running COGwithCSVtables.py...")
    COGwithCSVtables.process_pdf_with_cogvlm2('/home/user/Documents/Github/')  # Replace with your PDF path

    # Step 3: Sort the Software, Hardware, and Physical files
    print("Running sorter.py...")
    txt_file_path = 'final_output_with_text_images_tables_cogvlm2.txt'  # Ensure the path is correct
    sorter.classify_and_save_text(txt_file_path)

    # Step 4: Pull CVEs from the CSV tables using the CVEfromCSV.py script
    print("Running CVEfromCSV.py...")
    csv_directory = 'CSVfromTables'  # Directory containing the CSV files
    output_file_path = 'CVEfromCSVOutput.txt'  # Output file for extracted CVEs
    CVEfromCSV.process_all_csv_files(csv_directory, output_file_path)

if __name__ == "__main__":
    main()

