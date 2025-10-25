import pytesseract
import pandas as pd
from pdf2image import convert_from_path
import os
import sys
from typing import Optional

def check_dependencies():
    """Checks for necessary installations (Tesseract) and language data."""
    try:
        # Check if pytesseract is configured correctly
        pytesseract.get_tesseract_version()
    except pytesseract.TesseractNotFoundError:
        print("CRITICAL ERROR: Tesseract is not installed or not in your PATH.", file=sys.stderr)
        print("Please install Tesseract OCR (tesseract-ocr) on your system.", file=sys.stderr)
        return False
        
    try:
        # Check for language data availability
        # We assume 'eng' is standard. We explicitly check for 'tel'.
        languages = pytesseract.get_languages()
        if 'tel' not in languages:
            print("WARNING: Telugu ('tel') language data not found for Tesseract.", file=sys.stderr)
            print("Layout preservation will still work, but Telugu text will not be recognized.", file=sys.stderr)
            # We allow it to continue, but warn the user
    except Exception as e:
        print(f"Error checking Tesseract language data: {e}", file=sys.stderr)
        
    return True

def pdf_to_layout_data(pdf_path: str, lang: str = 'eng+tel') -> Optional[pd.DataFrame]:
    """
    Converts a multi-page PDF into a single DataFrame containing every 
    recognized word and its bounding box for layout preservation.

    Args:
        pdf_path: The file path to the input PDF.
        lang: Tesseract language string (e.g., 'eng+tel').

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
        # Convert PDF pages to a list of PIL Image objects
        print("Converting PDF pages to images (Requires Poppler)...")
        pages = convert_from_path(pdf_path)
    except Exception as e:
        print(f"CRITICAL ERROR: Error converting PDF to image.", file=sys.stderr)
        print(f"Ensure Poppler (pdf-to-ppm/pdftoppm) is installed and in your system PATH.", file=sys.stderr)
        print(f"Original error: {e}", file=sys.stderr)
        return None

    all_data_frames = []
    print(f"Starting OCR with Tesseract (Languages: {lang})...")

    for i, page in enumerate(pages):
        # Use Tesseract's image_to_data to get TSV output. 
        # output_type.DATAFRAME automatically parses the TSV into a DataFrame.
        # --psm 3 (Page Segmentation Mode) is generally good for a single column page
        data = pytesseract.image_to_data(page, lang=lang, config='--psm 3', output_type=pytesseract.Output.DATAFRAME)
        
        # Clean up the DataFrame: remove rows where text is NaN or just whitespace
        data = data.dropna(subset=['text'])
        data = data[data.text.apply(lambda x: str(x).strip() != '')]
        
        if not data.empty:
            # Add page number for reference
            data['page_num_actual'] = i + 1
            all_data_frames.append(data)

    if not all_data_frames:
        print("No readable text or data found after OCR.", file=sys.stderr)
        return None

    # Concatenate all page data into a single DataFrame
    final_df = pd.concat(all_data_frames, ignore_index=True)
    
    # Select and rename columns for clarity
    columns_to_keep = ['page_num_actual', 'level', 'block_num', 'par_num', 'line_num', 'word_num', 'left', 'top', 'width', 'height', 'text']
    final_df = final_df[columns_to_keep]
    
    return final_df


if __name__ == "__main__":
    # --- DEMONSTRATION & EXAMPLE USAGE ---
    
    # 1. Define a dummy PDF file path (REPLACE THIS WITH YOUR ACTUAL PDF FILE)
    dummy_pdf_path = "sample_document_eng_tel.pdf" 
    
    print(f"--- Running PDF Extractor on: {dummy_pdf_path} ---")
    
    # 2. Run the extraction function
    layout_df = pdf_to_layout_data(dummy_pdf_path, lang='eng+tel')
    
    if layout_df is not None:
        print("\n--- Extraction Successful ---")
        print(f"Total words found: {len(layout_df)}")
        print("\nFirst 5 rows of layout data (Word, Bounding Box, and Position):")
        
        # 3. Display the key layout columns
        print(layout_df[['page_num_actual', 'text', 'left', 'top', 'width', 'height', 'line_num']].head())
        
        # 4. Example of Layout Analysis (Grouping by page and line)
        print("\n--- Layout Analysis Example (First Page) ---")
        
        # Filter for the first page
        first_page_df = layout_df[layout_df['page_num_actual'] == 1]
        
        # Group by line number to reconstruct sentences
        line_groups = first_page_df.groupby('line_num').agg(
            full_line=('text', ' '.join),
            top_y=('top', 'min') # Use the top-most position of the line for sorting
        ).sort_values(by='top_y')
        
        print("Reconstructed Text by Line (Ordered by Vertical Position):")
        for line in line_groups['full_line']:
            print(f"> {line}")
        
    else:
        print("\n--- Extraction Failed. Check console for error messages. ---")
