import re
import csv
from collections import defaultdict
import os

def clean_telugu_word(word):
    """
    Cleans a Telugu word by removing common suffixes, punctuation, 
    and non-Telugu/non-space characters for basic normalization.
    This helps in matching different forms of the same word root.
    
    A more advanced solution would require a full morphological analyzer.
    """
    # 1. Remove common punctuation and stanza markers (like 1, 2, 3...)
    # We keep only Telugu script characters and the zero-width non-joiner (ZWNJ, \u200c) 
    # which is important for some conjuncts, but remove all other non-Telugu/non-space.
    word = re.sub(r'[.,;!?"\-()\[\]{}—:‘“’”\d\s]+', '', word)
    
    # 2. Normalize common Telugu word endings (optional, but improves simple concordance)
    # This is a basic, incomplete attempt at declension normalization:
    # word = re.sub(r'(ము|బు|లు|కు|న|వు|య|వు|రు|డు|కి|కిని|యున్)$', '', word)
    # For initial concordance, we'll rely on strict matching, as aggressive 
    # stemmers can lead to false positives.

    # 3. Convert to lowercase (not strictly needed for Telugu but good practice)
    # Telugu characters don't have case difference like English.
    
    return word.strip()

def tokenize_telugu_text(text):
    """
    Tokenizes the text into a list of words.
    """
    # Split by whitespace and remove empty strings
    words = re.split(r'\s+', text)
    return [word for word in words if word]

def generate_concordance(filepath, target_words=None, output_csv='concordance_output.csv'):
    """
    Generates a concordance list (Keyword-in-Context) for a Telugu text file.

    :param filepath: Path to the input Telugu text file.
    :param target_words: A list of specific words to search for. If None, all words are indexed.
    :param output_csv: Name of the output CSV file.
    """
    print(f"Processing text file: {filepath}...")
    
    try:
        # Use 'utf-8' encoding for Telugu text
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return

    concordance_entries = []
    
    # Normalize the target words for matching
    if target_words:
        target_words_set = {clean_telugu_word(word) for word in target_words}
    else:
        target_words_set = None

    for line_num, line in enumerate(lines, 1):
        # Strip leading/trailing whitespace and metadata markers
        cleaned_line = line.strip()
        
        # Skip empty lines, comment/metadata lines, and chapter headers for context accuracy
        if not cleaned_line or \
           cleaned_line.startswith(('అర్థం:', 'తాత్పర్యం:', 'వ్యాఖ్య:', 'విశేషం:', '::')):
            continue

        tokens = tokenize_telugu_text(cleaned_line)

        for token in tokens:
            normalized_token = clean_telugu_word(token)
            
            # Check if this word is a target word or if we are indexing all words
            if normalized_token and (target_words_set is None or normalized_token in target_words_set):
                
                # The full line is the context (Keyword in Context - KIC)
                # FIX APPLIED HERE: Used .append() instead of .=
                concordance_entries.append({
                    'Word': normalized_token,
                    'Original Form': token,
                    'Context': cleaned_line,
                    'Line Number': line_num
                })

    # Write the results to a CSV file
    fieldnames = ['Word', 'Original Form', 'Context', 'Line Number']
    
    try:
        with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(concordance_entries)
        
        print(f"Successfully generated concordance. Output saved to {output_csv}")
        print(f"Total entries found: {len(concordance_entries)}")

    except Exception as e:
        print(f"An error occurred while writing the CSV file: {e}")

# --- Example Usage ---
if __name__ == '__main__':
    # 1. Define the input file path (using the file you uploaded as example)
    input_file = 'kreedabhiraamamu.txt'
    
    # 2. Define a list of words you want to create the concordance for.
    # For example, searching for mentions of 'వల్లభరాయ', 'కామమంజరి', and 'ఓరుఁగంటి'
    # The script will normalize the words (e.g., remove trailing punctuation/suffixes) 
    # to perform the match, but will list the full word as it appears in the text.
    target_list = ['వల్లభరాయ', 'కామమంజరి', 'ఓరుఁగంటి', 'వీరపురుషులు']

    # 3. Run the generator
    generate_concordance(
        filepath=input_file, 
        target_words=target_list, 
        output_csv='kreedabhiraamamu_concordance.csv'
    )
    
    # Optional: Generate concordance for ALL words (Warning: this will be a huge file!)
    print("\nGenerating full concordance (all words)...")
    generate_concordance(
         filepath=input_file, 
         target_words=None, 
         output_csv='kreedabhiraamamu_full_concordance.csv'
    )
