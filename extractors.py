import fitz  # PyMuPDF
from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams
import io
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter

# Function to extract text from a single page using pdfminer.six
def extract_text_pdfminer(page_number, input_file):
    # Set up pdfminer resource manager and converter
    output_string = io.StringIO()
    laparams = LAParams()  # Configure layout analysis parameters as needed

    with open(input_file, 'rb') as file:
        # Use the page number to get the specific page
        for page in PDFPage.get_pages(file, pagenos=[page_number], caching=True, check_extractable=True):
            resource_manager = PDFResourceManager()
            device = TextConverter(resource_manager, output_string, laparams=laparams)
            interpreter = PDFPageInterpreter(resource_manager, device)
            interpreter.process_page(page)
            device.close()

    text = output_string.getvalue()
    output_string.close()
    
    # Return the extracted text from the page
    return text

# Function to extract text from a single page using PyMuPDF
def extract_text_pymupdf(page):
    # Use PyMuPDF's built-in text extraction (ignores layout, focuses on continuous text)
    return page.get_text("text")

# Main function to extract text page by page using both pdfminer.six and PyMuPDF
def extract_text_from_pdf(input_file, use_pdfminer=True):
    # Open the PDF with PyMuPDF
    pdf_document = fitz.open(input_file)
    
    page_texts = []

    # Iterate through all pages in the PDF
    for page_number in range(pdf_document.page_count):
        if use_pdfminer:
            # Extract text using pdfminer for the current page
            text_pdfminer = extract_text_pdfminer(page_number, input_file)
            page_texts.append(text_pdfminer)
        else:
            # Extract text using PyMuPDF for the current page
            page = pdf_document.load_page(page_number)
            text_pymupdf = extract_text_pymupdf(page)
            page_texts.append(text_pymupdf)
    
    # Close the document
    pdf_document.close()

    return page_texts
