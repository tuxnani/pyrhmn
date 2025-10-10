#!/usr/bin/env python

"""
Splits an input PDF file into several files based on a list of
splitting points (1-indexed page numbers where each part ends).

This script uses the cross-platform 'pypdf' library.
Install: pip install pypdf
"""

import sys
import os
import argparse
from pypdf import PdfReader, PdfWriter, errors


def split_pdf_file(input_fn, split_page_nums):
    """
    Splits the PDF file into multiple documents.

    Args:
        input_fn (str): The path to the input PDF file.
        split_page_nums (list[int]): A list of 1-based page numbers 
                                     defining the last page of each split part.

    For Linux, if you have a 200 page pdf, use as
      python split_pdf.py input_file.pdf $(seq 1 200)
    For Windows, in powershell, use the command for 200 page pdf into individual pages, use
      python split_pdf.py input_file.pdf (1..200)
    """
    try:
        reader = PdfReader(input_fn)
    except FileNotFoundError:
        print(f"Error: Input file not found at '{input_fn}'")
        sys.exit(1)
    except errors.PdfReadError:
        print(f"Error: Could not read PDF file '{input_fn}'. It may be corrupted or encrypted.")
        sys.exit(1)

    max_pages = len(reader.pages)
    print(f"'{input_fn}' has {max_pages} pages.")
    
    # --- Input Validation (Similar to the original script) ---
    
    # 1. Check bounds and increasing order
    for i, split_page_num in enumerate(split_page_nums):
        if not (1 <= split_page_num <= max_pages):
            print(f"Error: Split page number {split_page_num} is out of bounds (1 to {max_pages}).")
            sys.exit(3)
        if i > 0 and split_page_nums[i - 1] >= split_page_num:
            print("Error: Split page numbers must be strictly increasing.")
            sys.exit(4)

    # 2. Ensure the last page is included if not already specified
    if split_page_nums[-1] < max_pages:
        split_page_nums.append(max_pages)

    # --- Splitting Logic ---
    
    base_fn = os.path.splitext(os.path.basename(input_fn))[0]
    start_page_1_indexed = 1
    start_index_0_indexed = 0
    generated_files_count = 0

    for i, end_page_1_indexed in enumerate(split_page_nums):
        writer = PdfWriter()
        
        # The slice end index is the 1-indexed page number, 
        # because Python slices are exclusive at the end index,
        # and reader.pages is 0-indexed.
        end_index_0_indexed = end_page_1_indexed
        
        # Determine the pages to copy
        pages_to_copy = reader.pages[start_index_0_indexed : end_index_0_indexed]

        if not pages_to_copy:
            # This should only happen if splitPageNums had duplicates or was improperly validated,
            # but it's a good safety check.
            print(f"Skipping empty range: page {start_page_1_indexed}-{end_page_1_indexed}")
            start_page_1_indexed = end_page_1_indexed + 1
            start_index_0_indexed = end_index_0_indexed
            continue

        # Construct the output filename (e.g., input.part1.1_3.pdf)
        output_fn = f"{base_fn}.part{i + 1}.{start_page_1_indexed}_{end_page_1_indexed}.pdf"

        print(f"Writing page {start_page_1_indexed}-{end_page_1_indexed} to '{output_fn}'...")

        # Add pages to the writer object
        for page in pages_to_copy:
            writer.add_page(page)

        # Write the PDF to the output file
        with open(output_fn, "wb") as output_file:
            writer.write(output_file)
            
        generated_files_count += 1

        # Update start points for the next iteration
        start_page_1_indexed = end_page_1_indexed + 1
        start_index_0_indexed = end_index_0_indexed

    print(f"\nDone: {generated_files_count} file(s) generated.")


def main():
    parser = argparse.ArgumentParser(
        description="Splits an input PDF file into several given a list of splitting points (page numbers).",
        epilog="Example: python split_pdf.py input.pdf 3 5\n\nThis splits 'input.pdf' (e.g., 10 pages) into three files:\n- input.part1.1_3.pdf\n- input.part2.4_5.pdf\n- input.part3.6_10.pdf"
    )
    
    parser.add_argument(
        'inputFN',
        type=str,
        help='The path to the input PDF file.'
    )
    parser.add_argument(
        'splitPageNums',
        type=int,
        nargs='+',
        help='One or more positive integers (1-indexed page numbers) where each new part ends. Must be strictly increasing.'
    )

    if len(sys.argv) < 3:
        parser.print_help()
        sys.exit(1)
    
    args = parser.parse_args()
    
    # Validate the page numbers are positive integers before passing to the splitter
    if any(p <= 0 for p in args.splitPageNums):
        print("Error: All split page numbers must be positive integers (> 0).")
        sys.exit(5)
        
    split_pdf_file(args.inputFN, args.splitPageNums)

if __name__ == '__main__':
    main()
