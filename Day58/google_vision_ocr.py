import pandas as pd
import os
import sys
from typing import Optional, List, Dict, Any
from google.cloud import vision

def check_dependencies():
    """Checks for necessary Google Cloud authentication."""
    if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
        print("CRITICAL ERROR: 'GOOGLE_APPLICATION_CREDENTIALS' environment variable not set.", file=sys.stderr)
        print("Please set this variable to point to your Google Cloud JSON key file.", file=sys.stderr)
        return False
    
    if not os.path.exists(os.environ["GOOGLE_APPLICATION_CREDENTIALS"]):
        print(f"CRITICAL ERROR: Google credentials file not found at:", file=sys.stderr)
        print(f"{os.environ['GOOGLE_APPLICATION_CREDENTIALS']}", file=sys.stderr)
        return False
        
    print("Google Cloud credentials found.")
    return True

def get_word_layout(word: vision.Word) -> Dict[str, Any]:
    """Extracts text and bounding box info from a Google Vision Word object."""
    text = "".join([symbol.text for symbol in word.symbols])
    
    # Get bounding box vertices
    vertices = word.bounding_box.vertices
    
    # Calculate simple bounding box (min/max)
    left = min([v.x for v in vertices if v.x is not None], default=0)
    top = min([v.y for v in vertices if v.y is not None], default=0)
    right = max([v.x for v in vertices if v.x is not None], default=0)
    bottom = max([v.y for v in vertices if v.y is not None], default=0)
    
    return {
        'text': text,
        'left': left,
        'top': top,
        'width': right - left,
        'height': bottom - top,
        'confidence': word.confidence
    }

def pdf_to_layout_data(pdf_path: str) -> Optional[pd.DataFrame]:
    """
    Converts a multi-page PDF into a single DataFrame containing every 
    recognized word and its bounding box using Google Cloud Vision.

    Args:
        pdf_path: The file path to the input PDF.

    Returns:
        A Pandas DataFrame with columns like 'text', 'left', 'top', 
        'width', 'height', or None if an error occurs.
    """
    if not check_dependencies():
        return None

    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found at {pdf_path}", file=sys.stderr)
        return None

    try:
        client = vision.ImageAnnotatorClient()

        with open(pdf_path, 'rb') as f:
            content = f.read()

        mime_type = "application/pdf"
        input_config = vision.InputConfig(content=content, mime_type=mime_type)

        # Feature for text detection
        feature = vision.Feature(type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION)
        
        # Language hints can be provided, but auto-detection is powerful.
        # Adding 'te' (Telugu) and 'en' (English)
        image_context = vision.ImageContext(language_hints=["en", "te"])

        print(f"Submitting PDF to Google Vision API (this may take a moment)...")
        request = vision.AnnotateFileRequest(
            input_config=input_config,
            features=[feature],
            image_context=image_context
        )

        # Use batch_annotate_files for PDFs
        response = client.batch_annotate_files(requests=[request])

    except Exception as e:
        print(f"CRITICAL ERROR: Error calling Google Cloud Vision API.", file=sys.stderr)
        print(f"Original error: {e}", file=sys.stderr)
        return None

    all_words_data = []
    
    # Process the response
    try:
        for i, page_response in enumerate(response.responses[0].responses):
            page_num = i + 1
            annotation = page_response.full_text_annotation
            
            for page in annotation.pages:
                for block_num, block in enumerate(page.blocks):
                    for par_num, paragraph in enumerate(block.paragraphs):
                        for word_num, word in enumerate(paragraph.words):
                            word_data = get_word_layout(word)
                            word_data['page_num'] = page_num
                            word_data['block_num'] = block_num
                            word_data['par_num'] = par_num
                            word_data['word_num'] = word_num
                            all_words_data.append(word_data)

    except Exception as e:
        print(f"Error parsing Google Vision response: {e}", file=sys.stderr)
        if hasattr(response, 'error') and response.error:
             print(f"API Error Message: {response.error.message}", file=sys.stderr)
        return None

    if not all_words_data:
        print("No readable text or data found after OCR.", file=sys.stderr)
        return None

    # Concatenate all page data into a single DataFrame
    final_df = pd.DataFrame(all_words_data)
    
    # Reorder columns for clarity
    columns_order = [
        'page_num', 'block_num', 'par_num', 'word_num', 
        'text', 'left', 'top', 'width', 'height', 'confidence'
    ]
    final_df = final_df[columns_order]
    
    return final_df

if __name__ == "__main__":
    # --- DEMONSTRATION & EXAMPLE USAGE ---
    
    # 1. Define a dummy PDF file path (REPLACE THIS WITH YOUR ACTUAL PDF FILE)
    dummy_pdf_path = "sample_document_eng_tel.pdf" 
    
    print(f"--- Running Google Vision Extractor on: {dummy_pdf_path} ---")
    
    # 2. Run the extraction function
    layout_df = pdf_to_layout_data(dummy_pdf_path)
    
    if layout_df is not None:
        print("\n--- Extraction Successful ---")
        print(f"Total words found: {len(layout_df)}")
        print("\nFirst 5 rows of layout data (Word, Bounding Box, and Position):")
        
        # 3. Display the key layout columns
        print(layout_df[['page_num', 'text', 'left', 'top', 'width', 'height']].head())
        
        # 4. Example of Layout Analysis (Grouping by paragraph)
        print("\n--- Layout Analysis Example (First Page) ---")
        
        # Filter for the first page
        first_page_df = layout_df[layout_df['page_num'] == 1]
        
        # Group by block and paragraph to reconstruct text flow
        # We sort by the 'top' coordinate of the first word in each paragraph
        par_groups = first_page_df.groupby(['block_num', 'par_num']).agg(
            full_paragraph=('text', ' '.join),
            top_y=('top', 'min') # Use the top-most position for sorting
        ).sort_values(by='top_y')
        
        print("Reconstructed Text by Paragraph (Ordered by Vertical Position):")
        for par in par_groups['full_paragraph']:
            print(f"> {par}")
        
    else:
        print("\n--- Extraction Failed. Check console for error messages. ---")
        print("Please ensure 'GOOGLE_APPLICATION_CREDENTIALS' is set correctly.")
