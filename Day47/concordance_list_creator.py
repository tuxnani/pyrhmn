import re
from collections import defaultdict

# --- CONFIGURATION ---
TARGET_WORD = "రాముడు"  # Example: "Rama" (Rāmudu)
CONTEXT_SIZE = 4       # Number of words to show on each side
FILE_PATH = "telugu_text.txt"

# --- 1. BASIC TOKENIZATION AND PREPARATION ---

def simple_telugu_tokenizer(text):
    """
    Splits text into a list of "words" (tokens) for simple concordance.
    Uses a regex pattern to capture Telugu characters, numbers, and basic English.
    Note: This is a basic approach and doesn't handle complex inflections.
    """
    # Regex for Telugu characters (\u0c00-\u0c7f), numbers (0-9), and basic word characters (a-zA-Z)
    tokens = re.findall(r'[\u0c00-\u0c7f\w]+', text, re.UNICODE)
    return tokens

# --- 2. CONCORDANCE GENERATOR FUNCTION ---

def generate_concordance(tokens, target_word, context_size):
    """
    Generates a list of concordance lines (KWiC).
    """
    concordance_list = []
    
    for i, word in enumerate(tokens):
        # Case-insensitive check (though in Telugu text, it's often consistent)
        if word == target_word:
            # Calculate start and end indices for the context
            start_index = max(0, i - context_size)
            end_index = min(len(tokens), i + context_size + 1)
            
            # Extract left context, target, and right context
            left_context = " ".join(tokens[start_index:i])
            right_context = " ".join(tokens[i+1:end_index])
            
            concordance_list.append({
                'left': left_context,
                'target': word,
                'right': right_context,
                'index': i # Simple token index for reference
            })
            
    return concordance_list

# --- 3. MAIN EXECUTION ---

if __name__ == "__main__":
    try:
        # Load the Telugu text (ensure the file is UTF-8 encoded)
        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            raw_text = f.read()
    except FileNotFoundError:
        print(f"Error: The file '{FILE_PATH}' was not found.")
        # Create a dummy file with an example if not found
        sample_text = "రాముడు గొప్ప వీరుడు. సీత రాముడు తో కలిసి వచ్చింది. రాముడు రాజ్యం పాలించాడు."
        print(f"Using sample text: {sample_text}")
        raw_text = sample_text
    
    # --- PROCESSING STEPS ---
    
    # 1. Tokenization
    all_tokens = simple_telugu_tokenizer(raw_text)
    
    # 2. Generate Concordance
    concordance_data = generate_concordance(all_tokens, TARGET_WORD, CONTEXT_SIZE)

    # --- OUTPUT ---
    
    if not concordance_data:
        print(f"\nNo occurrences of '{TARGET_WORD}' found in the text.")
    else:
        print(f"\n--- Padaprayoga Soochi (Concordance) for '{TARGET_WORD}' ---")
        print(f"Total Occurrences: {len(concordance_data)}\n")
        
        # Determine max context lengths for alignment
        max_left = max(len(item['left']) for item in concordance_data)
        
        # Print the results in a classic KWiC format
        for item in concordance_data:
            print(
                f"{item['left'].rjust(max_left)} "
                f"**{item['target']}** "
                f"{item['right']}"
            )
            
    # Optional: Basic word frequency list (for unique words)
    # This list will include all inflected forms
    word_freq = defaultdict(int)
    for token in all_tokens:
        word_freq[token] += 1
        
    unique_word_count = len(word_freq)
    print(f"\nTotal Unique Word Forms (Approximate): {unique_word_count}")
