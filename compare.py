import re
from nltk.corpus import words as nltk_words

# Preload a list of English words using nltk
nltk_words_list = set(nltk_words.words())

# Dictionary of common OCR/extraction errors that need context to resolve
common_errors_patterns = [
    (r'rn', 'm'),  # "rn" mistaken for "m" (e.g., "farn" vs "farm")
    (r'nn', 'm'),  # "nn" mistaken for "m" (e.g., "fann" vs "farm")
    (r'i(\d)', r'1\1'),  # "i9" mistaken for "19"
    (r'0', 'o'),  # Zero mistaken for "o"
    (r'1', 'l'),  # One mistaken for "l" in certain cases
    (r'\bl\b', 'I'),  # Lowercase "l" mistaken for uppercase "I"
]

# Helper function to preprocess the text (e.g., normalize cases, strip non-alphabetic characters)
def preprocess_text(word):
    return re.sub(r'[^a-zA-Z0-9]', '', word.lower())

# Function to correct known common errors by leveraging context from word lists
def correct_common_errors(word1, word2):
    word1_clean = preprocess_text(word1)
    word2_clean = preprocess_text(word2)

    for error_pattern, correction in common_errors_patterns:
        # Try applying the error pattern to word1 and word2
        corrected_word1 = re.sub(error_pattern, correction, word1_clean)
        corrected_word2 = re.sub(error_pattern, correction, word2_clean)

        # Check if the corrected version is a valid known word
        if corrected_word1 in nltk_words_list and corrected_word2 not in nltk_words_list:
            return corrected_word1
        elif corrected_word2 in nltk_words_list and corrected_word1 not in nltk_words_list:
            return corrected_word2

    return None

# Function to check if the word is in the known word list
def is_known_word(word):
    return word.lower() in nltk_words_list

# Context-based word comparison function
def compare_words_with_context(pdfminer_word, pymupdf_word, context_before, context_after):
    # Step 1: If words are the same, return the word directly
    if pdfminer_word == pymupdf_word:
        return pdfminer_word

    # Step 2: Correct common errors based on known word list
    corrected = correct_common_errors(pdfminer_word, pymupdf_word)
    if corrected:
        return corrected

    # Step 3: Check if one of the words is known and the other is not
    pdfminer_known = is_known_word(pdfminer_word)
    pymupdf_known = is_known_word(pymupdf_word)

    if pdfminer_known and not pymupdf_known:
        return pdfminer_word
    elif pymupdf_known and not pdfminer_known:
        return pymupdf_word

    # Step 4: If neither word is recognized, prompt the user for input
    return ask_user_to_choose(pdfminer_word, pymupdf_word, context_before, context_after)

# Function to prompt the user to choose the correct word with context
def ask_user_to_choose(word1, word2, context_before, context_after):
    context_before_str = ' '.join(context_before[-3:]) if context_before else ""
    context_after_str = ' '.join(context_after[:3]) if context_after else ""
    
    # Display context and the two word options
    print(f"\nContext: {context_before_str} [ {word1} / {word2} ] {context_after_str}")
    
    while True:
        choice = input(f"Which word is correct? (1 for '{word1}', 2 for '{word2}'): ")
        if choice == '1':
            return word1
        elif choice == '2':
            return word2
        else:
            print("Invalid input, please press '1' or '2'.")

# Main comparison function to be used in the script
def determine_correct_word(pdfminer_word, pymupdf_word, context_before, context_after):
    return compare_words_with_context(pdfminer_word, pymupdf_word, context_before, context_after)

