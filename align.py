from difflib import SequenceMatcher
from thefuzz import fuzz

# Helper function to preprocess the text (e.g., remove unnecessary whitespace, normalize cases)
def preprocess_text(text):
    # Remove extra spaces, normalize text (convert to lowercase, etc.)
    return " ".join(text.lower().split())

# Function to fuzzy match two words
def fuzzy_match(word1, word2, threshold=85):
    # Return True if words match based on a fuzzy similarity score above the threshold
    return fuzz.ratio(word1, word2) >= threshold

# Function to align pages from pdfminer and PyMuPDF text
def align_pages(pdfminer_page, pymupdf_page):
    # Preprocess text from both pages to remove layout noise and prepare for word alignment
    pdfminer_page_clean = preprocess_text(pdfminer_page)
    pymupdf_page_clean = preprocess_text(pymupdf_page)

    # Split the cleaned text into word lists for comparison
    pdfminer_words = pdfminer_page_clean.split()
    pymupdf_words = pymupdf_page_clean.split()

    # Initialize the result list for aligned word pairs and context
    aligned_pairs = []
    context_before = []  # Keeps track of words before the current word
    context_after = []   # Placeholder for after context (may need filling in the main loop)

    # Use a sequence matcher to align the two word lists, handling small differences
    matcher = SequenceMatcher(None, pdfminer_words, pymupdf_words)

    # Get matching blocks and process them
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            # If words are considered equal, align them directly
            for pdfminer_word, pymupdf_word in zip(pdfminer_words[i1:i2], pymupdf_words[j1:j2]):
                aligned_pairs.append((pdfminer_word, pymupdf_word, context_before.copy(), context_after.copy()))
                # Update context
                context_before.append(pdfminer_word)
        elif tag == 'replace':
            # If there are replacements (differences), attempt fuzzy matching
            for pdfminer_word, pymupdf_word in zip(pdfminer_words[i1:i2], pymupdf_words[j1:j2]):
                if fuzzy_match(pdfminer_word, pymupdf_word):
                    aligned_pairs.append((pdfminer_word, pymupdf_word, context_before.copy(), context_after.copy()))
                else:
                    aligned_pairs.append((pdfminer_word, pymupdf_word, context_before.copy(), context_after.copy()))
                # Update context
                context_before.append(pdfminer_word)
        elif tag == 'delete':
            # Words only in pdfminer (possibly dropped in PyMuPDF extraction)
            for pdfminer_word in pdfminer_words[i1:i2]:
                aligned_pairs.append((pdfminer_word, None, context_before.copy(), context_after.copy()))
                context_before.append(pdfminer_word)
        elif tag == 'insert':
            # Words only in pymupdf (possibly dropped in pdfminer extraction)
            for pymupdf_word in pymupdf_words[j1:j2]:
                aligned_pairs.append((None, pymupdf_word, context_before.copy(), context_after.copy()))

    return aligned_pairs

