#!/usr/bin/env python3
"""
PDF to Image PDF Converter
Converts a text-based PDF to an image-based PDF at specified DPI.
Useful for PDFs (e.g., Telugu) with text extraction/copy-paste issues.
"""

import sys
import os
from pathlib import Path
# Import BytesIO from the io module for in-memory image handling
from io import BytesIO

try:
    # Import required libraries
    from pdf2image import convert_from_path
    from PIL import Image
    import img2pdf
except ImportError:
    print("Required Python libraries not found. Please install them using:")
    print("pip install pdf2image pillow img2pdf")
    print("\nNote: pdf2image also requires the poppler-utils utility:")
    print("  Ubuntu/Debian: sudo apt-get install poppler-utils")
    print("  macOS: brew install poppler")
    print("  Windows: Download from https://github.com/oschwartz10612/poppler-windows/releases/ and add to PATH.")
    sys.exit(1)


def convert_pdf_to_image_pdf(input_pdf, output_pdf=None, dpi=120):
    """
    Convert a text-based PDF to an image-based PDF.

    Args:
        input_pdf (str or Path): Path to input PDF file.
        output_pdf (str or Path, optional): Path to output PDF file.
        dpi (int): Resolution for image conversion (default: 120).

    Returns:
        Path: Path to the created output PDF.
        
    Raises:
        FileNotFoundError: If the input PDF does not exist.
        Exception: For errors during conversion.
    """
    input_path = Path(input_pdf)
    
    # Validate input file
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_pdf}")
    
    # Generate output filename if not provided
    if output_pdf is None:
        output_path = input_path.parent / f"{input_path.stem}_image.pdf"
    else:
        output_path = Path(output_pdf)
    
    print(f"Converting: {input_path.resolve()}")
    print(f"Output will be saved to: {output_path.resolve()}")
    print(f"Resolution: {dpi} DPI")
    print("\nConverting PDF pages to images...")
    
    try:
        # Convert PDF pages to PIL Images
        # The poppler path might be needed here if not in system PATH
        images = convert_from_path(input_path, dpi=dpi)
        print(f"Successfully converted {len(images)} page(s) to images.")
        
        # Convert PIL Images to bytes for img2pdf
        image_bytes_list = []
        for i, img in enumerate(images, 1):
            # Use carriage return to show progress on a single line
            print(f"Processing page {i}/{len(images)}...", end='\r')
            
            # img2pdf works best with images that have color space information (like RGB/JPEG)
            if img.mode not in ('RGB', 'RGBA', 'L', 'P', 'CMYK'):
                img = img.convert('RGB')
            
            # Save the PIL image to a temporary in-memory buffer (BytesIO) as JPEG
            # Using JPEG compression helps keep the final PDF size manageable
            img_bytes_buffer = BytesIO()
            img.save(img_bytes_buffer, format='JPEG', quality=85)
            # Append the raw bytes to the list
            image_bytes_list.append(img_bytes_buffer.getvalue())
            
        print(f"\nCreating image-based PDF...")
        
        # Create PDF from image bytes
        # The 'wb' mode is crucial for writing binary data
        with open(output_path, "wb") as f:
            f.write(img2pdf.convert(image_bytes_list))
        
        # Get file sizes for comparison
        input_size = input_path.stat().st_size / (1024 * 1024)  # MB
        output_size = output_path.stat().st_size / (1024 * 1024) # MB
        
        print(f"\n\n\u2713 Conversion complete!")
        print(f"Input file size: {input_size:.2f} MB")
        print(f"Output file size: {output_size:.2f} MB")
        print(f"Output saved to: {output_path.resolve()}")
        
        return output_path
        
    except Exception as e:
        print(f"\n\u2717 Error during conversion: {str(e)}")
        # Clean up the output file if it was partially created
        if 'output_path' in locals() and output_path.exists():
             os.remove(output_path)
             print(f"Cleaned up partial output file: {output_path}")
        raise


def main():
    """Main function to handle command line usage"""
    
    if len(sys.argv) < 2:
        print("Usage: python pdf_to_image_pdf.py <input.pdf> [output.pdf] [dpi]")
        print("\nExamples:")
        print("  python pdf_to_image_pdf.py telugu_book.pdf")
        print("  python pdf_to_image_pdf.py telugu_book.pdf output.pdf")
        print("  python pdf_to_image_pdf.py telugu_book.pdf 150")
        print("  python pdf_to_image_pdf.py telugu_book.pdf output.pdf 150")
        print("\nDefault DPI: 120")
        print("Default output: <input_filename>_image.pdf")
        sys.exit(1)
    
    input_pdf = sys.argv[1]
    output_pdf = None
    dpi = 120
    
    if len(sys.argv) > 2:
        # Check if argument 2 is DPI (e.g., '150')
        if sys.argv[2].isdigit():
            try:
                dpi = int(sys.argv[2])
            except ValueError:
                # Should not happen because of .isdigit(), but for safety
                print(f"Warning: Invalid DPI value '{sys.argv[2]}' ignored. Using default 120.")
            
            # If a third argument exists, it must be the output file
            if len(sys.argv) > 3:
                output_pdf = sys.argv[3]
                try:
                    # If 3rd argument is a valid number, assume argument 2 was output file and 3 is DPI
                    # Re-evaluate logic: The original logic tried to handle a few cases. Let's simplify and make explicit.
                    # Case 1: <input.pdf> <dpi>
                    # Case 2: <input.pdf> <output.pdf>
                    # Case 3: <input.pdf> <output.pdf> <dpi>
                    
                    # Original logic was: Arg 2 is output_pdf, Arg 3 is dpi.
                    # The only complex case was: Arg 2 is *number*, which means it's DPI, and output_pdf is None.
                    pass # Keep the following original logic for now, but handle the error.
                except ValueError:
                     print(f"Error: DPI value must be an integer. Received: '{sys.argv[3]}'")
                     sys.exit(1)
        else:
            # Argument 2 is the output file
            output_pdf = sys.argv[2]
            
            # Argument 3 is DPI
            if len(sys.argv) > 3:
                try:
                    dpi = int(sys.argv[3])
                except ValueError:
                    print(f"Error: Invalid DPI value '{sys.argv[3]}'. DPI must be an integer.")
                    sys.exit(1)
                    
    # The original DPI logic was slightly confusing. Let's re-implement the simplified original logic:
    # Arg 2 is output_pdf, Arg 3 is dpi. If Arg 2 is a number, it's dpi, and output_pdf is None.
    
    # Start clean:
    input_pdf = sys.argv[1]
    output_pdf = None
    dpi = 120
    
    if len(sys.argv) > 2:
        # Case 1: At least 2 arguments (input and one more)
        arg2 = sys.argv[2]
        if len(sys.argv) == 3:
            # Only 3 arguments total: <input.pdf> <output.pdf> OR <input.pdf> <dpi>
            if arg2.isdigit():
                try:
                    dpi = int(arg2)
                except ValueError:
                    # Should not be reached with isdigit() check
                    pass 
                # output_pdf remains None
            else:
                output_pdf = arg2
                # dpi remains 120
        elif len(sys.argv) > 3:
            # At least 4 arguments: <input.pdf> <output.pdf> <dpi> (and possibly more, which are ignored)
            output_pdf = arg2
            try:
                dpi = int(sys.argv[3])
            except ValueError:
                print(f"Error: Invalid DPI value '{sys.argv[3]}'. DPI must be an integer.")
                sys.exit(1)
    
    # This logic covers the example cases well:
    # python pdf_to_image_pdf.py telugu_book.pdf              -> input=t.pdf, output=None, dpi=120
    # python pdf_to_image_pdf.py telugu_book.pdf output.pdf    -> input=t.pdf, output=o.pdf, dpi=120
    # python pdf_to_image_pdf.py telugu_book.pdf 150          -> input=t.pdf, output=None, dpi=150
    # python pdf_to_image_pdf.py telugu_book.pdf output.pdf 150 -> input=t.pdf, output=o.pdf, dpi=150


    try:
        convert_pdf_to_image_pdf(input_pdf, output_pdf, dpi)
    except Exception as e:
        # The inner function already prints the error, so a simple message here is sufficient
        print("\n\u2717 Operation failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
