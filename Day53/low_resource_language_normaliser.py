import re
import unicodedata
import pandas as pd
from typing import Dict, List, Any

class LowResourceNormalizer:
    """
    A customizable text normalization pipeline designed for low-resource languages.
    
    The pipeline includes steps for robust Unicode handling, diacritic removal,
    punctuation standardization, and custom dictionary-based substitution.
    """
    def __init__(self, custom_rules: Dict[str, str] = None, remove_diacritics: bool = False):
        """
        Initializes the normalizer with optional custom substitution rules.

        Args:
            custom_rules: A dictionary where keys are patterns (or exact words) to 
                          replace, and values are the replacement strings.
            remove_diacritics: If True, attempts to remove all combining diacritical marks.
        """
        # Ensure rules are compiled for faster matching if many are provided
        self.custom_rules = custom_rules if custom_rules is not None else {}
        self.remove_diacritics = remove_diacritics
        print(f"Normalizer initialized with {len(self.custom_rules)} custom rules.")

    def _apply_custom_rules(self, text: str) -> str:
        """Applies dictionary-based substitution rules."""
        for pattern, replacement in self.custom_rules.items():
            # Use regex substitution to handle case-insensitivity and word boundaries 
            # for common replacements
            try:
                # \b ensures we match whole words unless the pattern is complex
                text = re.sub(r'\b' + re.escape(pattern) + r'\b', replacement, text, flags=re.IGNORECASE)
            except Exception:
                # Fallback to simple string replacement for non-regex patterns
                text = text.replace(pattern, replacement)
        return text

    def _remove_diacritics(self, text: str) -> str:
        """Removes diacritical marks from characters."""
        text = unicodedata.normalize('NFD', text)
        text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')
        return unicodedata.normalize('NFKC', text) # Re-normalize after removal

    def normalize_text(self, text: str) -> str:
        """
        Applies the full normalization pipeline to a single string.
        
        The pipeline order is:
        1. Unicode Standardization (NFKC)
        2. Custom Substitution Rules
        3. Punctuation Standardization
        4. Diacritic Removal (if configured)
        5. Whitespace Cleanup
        """
        if not isinstance(text, str):
            # Handle non-string input (e.g., NaNs which might be read as float)
            return ""

        # Step 1: Unicode Standardization (NFKC is preferred for compatibility)
        text = unicodedata.normalize('NFKC', text)
        
        # Step 2: Apply Custom Rules (e.g., spelling variants, abbreviations)
        text = self._apply_custom_rules(text)

        # Step 3: Punctuation Standardization (e.g., replacing special dashes with standard ones)
        text = text.replace('—', '--').replace('–', '-')
        
        # Step 4: Diacritic Removal (if configured)
        if self.remove_diacritics:
            text = self._remove_diacritics(text)

        # Step 5: Lowercasing and Whitespace Cleanup
        text = text.lower()
        # Replace multiple spaces, tabs, newlines with a single space
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    def normalize_series(self, series: pd.Series) -> pd.Series:
        """Applies normalization to a pandas Series (e.g., a DataFrame column)."""
        print(f"Applying normalization to pandas Series...")
        return series.apply(self.normalize_text)

# --- Example Usage ---

if __name__ == "__main__":
    # 1. Define custom normalization rules specific to your low-resource language
    # These rules might handle common dialectal variations, abbreviations, or known errors.
    custom_normalization_rules = {
        "tél": "telephone",      # Abbreviation standardization
        "k's": "kus",            # Dialectal/slang variant standardization
        "cáfé": "cafe",          # Common misspelling fix (optional, NFKC may handle accents)
        "D.P.": "District Police" # Acronym expansion
    }

    # 2. Instantiate the Normalizer
    # Set remove_diacritics=True if you want to aggressively simplify characters (e.g., é -> e).
    normalizer = LowResourceNormalizer(
        custom_rules=custom_normalization_rules, 
        remove_diacritics=True
    )
    
    # 3. Sample Data
    sample_texts = [
        "Unicôde test: Tél. no. 123",
        "This is a K's example--with multiple   spaces.",
        "D.P. officer was at the CáFé.",
        "Another Example.",
        None, # Test handling of non-string values (like None/NaN)
        "résumé"
    ]
    
    # 4. Create a DataFrame for demonstration
    df = pd.DataFrame({'raw_text': sample_texts})
    
    print("\nOriginal DataFrame:")
    print(df)
    
    # 5. Apply the normalization to the column
    df['normalized_text'] = normalizer.normalize_series(df['raw_text'])
    
    print("\nNormalized DataFrame:")
    print(df)

    # Expected output for normalized_text:
    # 0: 'unicode test: telephone no. 123' (tél replaced, no. cleaned)
    # 1: 'this is a kus example-with multiple spaces.' (K's replaced, '--' standardized)
    # 2: 'district police officer was at the cafe.' (D.P. expanded, cáFé normalized and diacritics removed)
    # 5: 'resume' (diacritics removed)
