from __future__ import print_function
import fnmatch
import io
import os
import httplib2
from apiclient import discovery
from apiclient.http import MediaFileUpload, MediaIoBaseDownload
from oauth2client import file, client, tools
from PyPDF2 import PdfReader, PdfWriter
import datetime

SCOPES = ("https://www.googleapis.com/auth/drive")
PAGES_PER_CHUNK = 10

# Authentication with extended token lifespan
store = file.Storage('token.json')
creds = store.get()

if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
    # Set access type to offline to get refresh token
    flow.params['access_type'] = 'offline'
    flow.params['approval_prompt'] = 'force'
    creds = tools.run_flow(flow, store)
    # Store credentials with extended expiry
    store.put(creds)

# Refresh token if it's about to expire (within 7 days)
if creds.token_expiry:
    days_until_expiry = (creds.token_expiry - datetime.datetime.utcnow()).days
    if days_until_expiry < 7:
        creds.refresh(httplib2.Http())
        store.put(creds)

http = creds.authorize(httplib2.Http())
service = discovery.build("drive", "v3", http=http)

def get_file_names():
    """Get list of files organized by type"""
    file_names = {"pdf": [], "jpg": [], "png": [], "gif": [], "bmp": [], "doc": []}
    for x in os.listdir('.'):
        for file_type in file_names.keys():
            if fnmatch.fnmatch(x, "*." + file_type):
                file_names[file_type].append(x.replace("." + file_type, ""))
    return file_names

def split_pdf(input_pdf, pages_per_chunk=PAGES_PER_CHUNK):
    """Split PDF into smaller chunks and return list of chunk filenames"""
    print(f"Splitting {input_pdf} into chunks of {pages_per_chunk} pages...")
    
    reader = PdfReader(input_pdf)
    total_pages = len(reader.pages)
    print(f"Total pages: {total_pages}")
    
    chunk_files = []
    num_chunks = (total_pages + pages_per_chunk - 1) // pages_per_chunk
    
    for chunk_num in range(num_chunks):
        start_page = chunk_num * pages_per_chunk
        end_page = min(start_page + pages_per_chunk, total_pages)
        
        writer = PdfWriter()
        for page_num in range(start_page, end_page):
            writer.add_page(reader.pages[page_num])
        
        chunk_filename = f"{input_pdf}_chunk_{chunk_num + 1}.pdf"
        with open(chunk_filename, 'wb') as output_file:
            writer.write(output_file)
        
        chunk_files.append(chunk_filename)
        print(f"Created chunk {chunk_num + 1}/{num_chunks}: {chunk_filename} (pages {start_page + 1}-{end_page})")
    
    return chunk_files

def ocr(input_file, input_filetype, output):
    """Perform OCR on a single file"""
    mime_types = {
        "pdf": 'application/pdf',
        "jpg": 'image/jpeg',
        "png": 'image/png',
        "gif": 'image/gif',
        "bmp": 'image/bmp',
        "doc": 'application/msword'
    }
    input_mime_type = mime_types[input_filetype]
    file_metadata = {'name': input_file, 'mimeType': 'application/vnd.google-apps.document'}
    
    # Upload the file to Google Drive
    media = MediaFileUpload(input_file, mimetype=input_mime_type, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    
    print(f'Uploaded File ID: {file.get("id")}')
    
    # Export the file to txt and download it
    request = service.files().export_media(fileId=file.get('id'), mimeType="text/plain")
    dl = MediaIoBaseDownload(io.FileIO(output, "wb"), request)
    is_complete = False
    while not is_complete:
        status, is_complete = dl.next_chunk()
    
    # Delete the uploaded file from Google Drive
    service.files().delete(fileId=file["id"]).execute()
    print(f"Output saved to {output}")

def ocr_pdf_chunked(pdf_filename):
    """Process a PDF by splitting it into chunks and performing OCR on each"""
    full_pdf_path = pdf_filename + ".pdf"
    
    # Split the PDF into chunks
    chunk_files = split_pdf(full_pdf_path)
    
    # Process each chunk with OCR
    all_text_files = []
    for chunk_file in chunk_files:
        chunk_output = chunk_file.replace(".pdf", "_text.txt")
        print(f"\nProcessing {chunk_file}...")
        ocr(chunk_file, "pdf", chunk_output)
        all_text_files.append(chunk_output)
    
    # Combine all chunk text files into one final output
    final_output = f"{pdf_filename}_pdf_text.txt"
    print(f"\nCombining all chunks into {final_output}...")
    with open(final_output, 'w', encoding='utf-8') as outfile:
        for text_file in all_text_files:
            with open(text_file, 'r', encoding='utf-8') as infile:
                outfile.write(infile.read())
                outfile.write("\n\n" + "="*50 + "\n\n")  # Separator between chunks
            # Delete chunk text file after combining
            os.remove(text_file)
    
    # Delete chunk PDFs
    for chunk_file in chunk_files:
        os.remove(chunk_file)
        print(f"Deleted chunk: {chunk_file}")
    
    # Delete original PDF
    os.remove(full_pdf_path)
    print(f"Deleted original PDF: {full_pdf_path}")
    
    print(f"\nFinal OCR output saved to: {final_output}")

# Main execution
print("="*60)
print("PDF OCR with Chunking - Starting Process")
print("="*60 + "\n")

# Print files found by type
files = get_file_names()
for file_type in files:
    if files[file_type]:
        print(f"{file_type.upper()} files:")
        for file in files[file_type]:
            print(f"\t{file}")
print()

# Process PDFs with chunking
if files["pdf"]:
    print("Processing PDF files with chunking...")
    for pdf_file in files["pdf"]:
        print(f"\n{'='*60}")
        print(f"Processing: {pdf_file}.pdf")
        print('='*60)
        ocr_pdf_chunked(pdf_file)

# Process other file types normally
for file_type in ["jpg", "png", "gif", "bmp", "doc"]:
    if files[file_type]:
        print(f"\nProcessing {file_type.upper()} files...")
        for file in files[file_type]:
            input_file = f"{file}.{file_type}"
            output_file = f"{file}_{file_type}_text.txt"
            print(f"Converting: {input_file}")
            ocr(input_file, file_type, output_file)

print("\n" + "="*60)
print("All conversions complete!")
print("="*60)