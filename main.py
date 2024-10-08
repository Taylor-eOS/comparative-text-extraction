import fitz  # PyMuPDF
from extractors import extract_text_from_pdf
from align import align_pages
from compare import determine_correct_word

# Main function to process PDF and produce aligned text output
def process_pdf(input_file, output_file):
    # Extract text from the PDF using both pdfminer.six and PyMuPDF
    print("Extracting text using pdfminer.six...")
    pdfminer_texts = extract_text_from_pdf(input_file, use_pdfminer=True)
    
    print("Extracting text using PyMuPDF...")
    pymupdf_texts = extract_text_from_pdf(input_file, use_pdfminer=False)

    # Check if both extractions have the same number of pages
    if len(pdfminer_texts) != len(pymupdf_texts):
        print("Error: The number of pages extracted by pdfminer.six and PyMuPDF does not match!")
        return

    # Open the output file for writing
    with open(output_file, 'w') as out:
        # Process each page
        for page_number in range(len(pdfminer_texts)):
            print(f"Processing page {page_number + 1}...")

            # Get the text for the current page from both extractors
            pdfminer_page_text = pdfminer_texts[page_number]
            pymupdf_page_text = pymupdf_texts[page_number]

            # Align words between the two extracted versions of the page
            aligned_words = align_pages(pdfminer_page_text, pymupdf_page_text)

            # For each aligned word pair, determine the correct word and write to output
            for i, (pdfminer_word, pymupdf_word, context_before, context_after) in enumerate(aligned_words):
                # Add future context (context_after) by looking ahead within the aligned_words
                context_after = [
                    aligned_words[j][0] or aligned_words[j][1]
                    for j in range(i + 1, min(i + 4, len(aligned_words)))
                    if aligned_words[j][0] or aligned_words[j][1]
                ]

                # Prepare context before (last three words)
                if i >= 3:
                    context_before = [
                        aligned_words[k][0] or aligned_words[k][1]
                        for k in range(i - 3, i)
                    ]

                # Call the comparison function with context
                if pdfminer_word and pymupdf_word:
                    correct_word = determine_correct_word(
                        pdfminer_word, pymupdf_word, context_before, context_after
                    )
                    out.write(correct_word + ' ')
                elif pdfminer_word:  # pdfminer.six has a word that PyMuPDF doesn't
                    out.write(pdfminer_word + ' ')
                elif pymupdf_word:  # PyMuPDF has a word that pdfminer.six doesn't
                    out.write(pymupdf_word + ' ')

            # Add a paragraph break after each page to format the output properly
            out.write('\n\n')

    print(f"Processing complete. Output written to {output_file}.")

if __name__ == "__main__":
    input_file = "input.pdf"  # Input PDF file located in the same folder
    output_file = "output.txt"  # Output text file, recreated each time

    process_pdf(input_file, output_file)
