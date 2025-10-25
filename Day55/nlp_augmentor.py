import nltk
import pandas as pd
import random
import re
from nltk.corpus import wordnet as wn
from typing import List, Union

# Ensure necessary NLTK data is downloaded (only needs to be run once)
try:
    # Attempt to load wordnet, if it fails, download it
    _ = wn.synsets('test')
except nltk.downloader.DownloadError:
    print("Downloading 'wordnet' corpus from NLTK. This may take a moment...")
    nltk.download('wordnet')
except LookupError:
    print("Downloading 'wordnet' corpus from NLTK. This may take a moment...")
    nltk.download('wordnet')

class NLPDataAugmenter:
    """
    Automated data augmentation for NLP using simple but effective techniques 
    like synonym replacement and random deletion.
    
    NOTE: Synonym replacement works best for English, but the structure can be 
    used for custom dictionary-based replacement in other languages.
    """
    
    def __init__(self, synonym_prob: float = 0.2, delete_prob: float = 0.1):
        """
        Initializes the augmenter with probabilities for each operation.
        
        Args:
            synonym_prob: Probability of replacing a word with a synonym.
            delete_prob: Probability of randomly deleting a word.
        """
        self.synonym_prob = synonym_prob
        self.delete_prob = delete_prob
        print(f"NLP Augmenter initialized: Synonym Prob={synonym_prob}, Delete Prob={delete_prob}")

    def _get_synonyms(self, word: str) -> List[str]:
        """Fetches a list of unique synonyms for a given word using WordNet."""
        synonyms = set()
        for syn in wn.synsets(word):
            for lemma in syn.lemmas():
                # Avoid the word itself and ensure it's a valid string
                if lemma.name().lower() != word.lower() and re.match(r'^\w+$', lemma.name()):
                    synonyms.add(lemma.name().replace('_', ' '))
        return list(synonyms)

    def synonym_replacement(self, text: str) -> str:
        """
        Replaces random words in the text with one of their synonyms.
        """
        words = text.split()
        new_words = words.copy()
        
        # Keep track of words already replaced to avoid double processing
        replaced_indices = set()
        
        for i, word in enumerate(words):
            if i in replaced_indices:
                continue
                
            if random.random() < self.synonym_prob:
                synonyms = self._get_synonyms(word)
                if synonyms:
                    # Choose a random synonym and replace the word
                    new_words[i] = random.choice(synonyms)
                    replaced_indices.add(i)
                    
        return ' '.join(new_words)

    def random_deletion(self, text: str) -> str:
        """
        Randomly deletes words from the text based on the deletion probability.
        """
        words = text.split()
        if len(words) == 0:
            return text
            
        # Create a new list containing only the words that pass the random check
        remaining_words = [
            word for word in words if random.random() > self.delete_prob
        ]
        
        # Ensure the resulting sentence is not empty
        if len(remaining_words) == 0:
            # Fallback: keep one random word if everything was deleted
            return random.choice(words)
            
        return ' '.join(remaining_words)

    def augment(self, text: Union[str, pd.Series]) -> Union[str, pd.Series]:
        """
        Applies both synonym replacement and random deletion sequentially.
        Can process a single string or a pandas Series/column.
        """
        if isinstance(text, pd.Series):
            print("Applying augmentation to pandas Series...")
            # Use apply to process each string in the series
            return text.apply(self._augment_single_text)
        else:
            return self._augment_single_text(text)

    def _augment_single_text(self, text: str) -> str:
        """Helper function for the sequential augmentation steps."""
        if not isinstance(text, str):
            return text
            
        # Apply synonym replacement first
        augmented_text = self.synonym_replacement(text)
        
        # Then apply random deletion to the result
        augmented_text = self.random_deletion(augmented_text)
        
        return augmented_text


if __name__ == "__main__":
    # --- Example Usage ---
    
    # 1. Create the Augmenter instance
    augmenter = NLPDataAugmenter(
        synonym_prob=0.3, # 30% chance to replace a word with a synonym
        delete_prob=0.1   # 10% chance to delete a word
    )

    # 2. Sample Data
    input_text = "The quick brown fox jumps over the lazy dog."
    
    print("\n--- Single Text Augmentation ---")
    print(f"Original: {input_text}")
    
    # Generate 5 augmented versions of the single text
    for i in range(5):
        augmented = augmenter.augment(input_text)
        print(f"Augmented {i+1}: {augmented}")

    # 3. DataFrame Augmentation Example
    data = {
        'text': ["The client requires a complex and detailed report.", 
                 "We need to urgently purchase supplies for the next phase.",
                 "The current process is inefficient and costly."]
    }
    df = pd.DataFrame(data)
    
    print("\n--- DataFrame Augmentation ---")
    print("Original DataFrame:")
    print(df)

    # Augment the 'text' column and add it as a new column
    df['augmented_text'] = augmenter.augment(df['text'])
    
    print("\nDataFrame after Augmentation:")
    # Display original alongside augmented text
    for index, row in df.iterrows():
        print(f"Original: {row['text']}")
        print(f"Augmented: {row['augmented_text']}")
        print("-" * 20)
