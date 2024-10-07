# Import necessary modules from each file
import COGwithCSVtables
import sorter
import CVEPuller
import naturalLanguageProcessor

# Main function to run all processes sequentially
def main():
    # Step 1: Process the PDF and extract CSV tables
    print("Running COGwithCSVtables.py...")
    COGwithCSVtables.process_pdf_with_cogvlm2('/path/to/your/pdf/file')

    # Step 2: Sort and classify the information in text files
    print("Running sorter.py...")
    sorter.classify_and_save_text("final_output_with_text_images_tables_cogvlm2.txt")

    # Step 3: Pull CVE data from the CSV files
    print("Running CVEPuller.py...")
    CVEPuller.process_cves("/path/to/csv/folder")  # Adjust the folder path to your actual CSV location

    # Step 4: Clean the text files using the natural language processor
    print("Running naturalLanguageProcessor.py...")
    naturalLanguageProcessor.process_and_clean_physical_file("classified_output/Physical.txt")

    print("All processes completed.")

if __name__ == "__main__":
    main()
