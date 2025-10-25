import os
import io
import tempfile
import shutil
import argparse
from PyPDF2 import PdfReader, PdfWriter
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.oauth2.credentials import Credentials
from PIL import Image
import numpy as np


# ---------- Google Drive setup ----------
def get_drive_service():
    """Builds and returns the Google Drive service."""
    # Ensure you have a valid token.json file for authentication
    creds = Credentials.from_authorized_user_file("token.json", ["https://www.googleapis.com/auth/drive"])
    return build("drive", "v3", credentials=creds)


# Initialize the service globally (assuming token.json is present)
try:
    service = get_drive_service()
except Exception as e:
    print(f"Error initializing Google Drive service. Ensure 'token.json' is valid.")
    print(f"Details: {e}")
    # Setting service to None to handle errors later
    service = None


# ---------- Google Docs OCR ----------
def google_ocr(image_path, output_path):
    """
    Performs OCR on an image file using Google Docs API.
    Uploads the image, exports as plain text, and deletes the file from Drive.
    """
    if not service:
        raise ConnectionError("Google Drive service is not initialized.")

    mime_map = {"pdf": 'application/pdf', "jpg": 'image/jpeg', "png": 'image/png'}
    ext = image_path.split('.')[-1].lower()
    media = MediaFileUpload(image_path, mimetype=mime_map.get(ext, 'image/png'), resumable=False)
    file_metadata = {'name': os.path.basename(image_path), 'mimeType': 'application/vnd.google-apps.document'}

    # Upload file
    uploaded = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    file_id = uploaded.get('id')

    # Export to plain text
    request = service.files().export_media(fileId=file_id, mimeType="text/plain")
    with io.FileIO(output_path, "wb") as f:
        downloader = MediaIoBaseDownload(f, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()

    # Clean up Drive
    service.files().delete(fileId=file_id).execute()
    return output_path


# ---------- Split PDF into 5-page chunks ----------
def split_pdf(input_pdf, temp_dir, chunk_size=5):
    """Splits a PDF into smaller chunks."""
    reader = PdfReader(input_pdf)
    chunks = []
    total_pages = len(reader.pages)
    for i in range(0, total_pages, chunk_size):
        writer = PdfWriter()
        for j in range(i, min(i + chunk_size, total_pages)):
            writer.add_page(reader.pages[j])
        chunk_path = os.path.join(temp_dir, f"chunk_{i // chunk_size + 1}.pdf")
        with open(chunk_path, "wb") as f:
            writer.write(f)
        chunks.append(chunk_path)
    return chunks


# ---------- OCR + Layout ----------
def ocr_pdf(input_pdf, output_txt):
    """
    Performs OCR on a PDF using a combination of DocTR for layout analysis
    and Google Docs for the actual text recognition on cropped regions.
    """
    print(f"Starting OCR for: {input_pdf}")
    predictor = ocr_predictor(pretrained=True)
    temp_dir = tempfile.mkdtemp()
    out_texts = []

    try:
        chunks = split_pdf(input_pdf, temp_dir)
        page_counter = 1

        for chunk_path in chunks:
            doc = DocumentFile.from_pdf(chunk_path)
            result = predictor(doc)

            # The DocTR result pages correspond to the chunk pages
            for page_idx_in_chunk, page in enumerate(result.pages):

                # --- DocTR Layout Analysis ---
                # Get the original image array for cropping
                page_image = doc[page_idx_in_chunk]
                if hasattr(page_image, "numpy"):
                    page_image = page_image.numpy()
                elif isinstance(page_image, str):
                    page_image = np.array(Image.open(page_image))

                # Convert to PIL Image for cropping
                pil_img = Image.fromarray(
                    (page_image * 255).astype(np.uint8)) if page_image.dtype != np.uint8 else Image.fromarray(
                    page_image)
                img_w, img_h = pil_img.size

                # Sort blocks by their left-most coordinate (x1) for column order
                blocks = sorted(page.blocks, key=lambda b: b.geometry[0][0])

                # --- Google OCR on Cropped Blocks ---
                for col_idx, block in enumerate(blocks, start=1):
                    (x1, y1), (x2, y2) = block.geometry
                    # Convert normalized coordinates (0-1) to pixel values
                    x1p, y1p, x2p, y2p = int(x1 * img_w), int(y1 * img_h), int(x2 * img_w), int(y2 * img_h)

                    # Crop and save the image block
                    crop_img_path = os.path.join(temp_dir, f"p{page_counter}_c{col_idx}.png")
                    pil_img.crop((x1p, y1p, x2p, y2p)).save(crop_img_path)

                    # Perform Google OCR on the cropped image
                    ocr_out_path = os.path.join(temp_dir, f"p{page_counter}_c{col_idx}.txt")
                    google_ocr(crop_img_path, ocr_out_path)

                    # Read and store the OCR text
                    with open(ocr_out_path, "r", encoding="utf-8") as f:
                        text = f.read().strip()
                        if text:
                            out_texts.append(f"[Page {page_counter} - Column {col_idx}]\n{text}\n")

                page_counter += 1

        # Write all collected text to the final output file
        with open(output_txt, "w", encoding="utf-8") as out:
            out.write("\n\n".join(out_texts))

    except Exception as e:
        print(f"\nAn error occurred during OCR: {e}")
        return False

    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir)

    print(f"\nOCR complete. Output saved at {output_txt}")
    return True


# ---------- Main Execution with Argument Parsing ----------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract text from a PDF file using DocTR for layout analysis and Google OCR for text recognition."
    )
    parser.add_argument(
        "input_pdf",
        type=str,
        help="The path to the input PDF file to process."
    )

    args = parser.parse_args()

    input_pdf = args.input_pdf

    # Check if the input PDF file exists
    if not os.path.exists(input_pdf):
        print(f"Error: Input file not found at '{input_pdf}'")
        exit(1)

    # Generate the output TXT file name
    base_name, _ = os.path.splitext(input_pdf)
    output_txt = base_name + ".txt"

    # Execute the OCR process
    if service:
        ocr_pdf(input_pdf, output_txt)
    else:
        print("Cannot proceed with OCR. Google Drive service failed to initialize.")
