import os
import io
import time
import json
from google.cloud import documentai
from google.cloud import storage
from google.oauth2 import service_account
from google.api_core import operations_v1

# --- CONFIGURATION (UPDATE THESE VALUES) ---
PROJECT_ID = "YOUR_PROJECT_ID" # Your GCP Project ID
LOCATION = "us" # Document AI processor location (e.g., 'us' or 'eu')
PROCESSOR_ID = "a0b1c2d3e4f5g6h7" # Example: Replace with the actual OCR Processor ID
GCS_INPUT_BUCKET = "my-newspaper-input-data" # Must be an existing GCS bucket name
GCS_OUTPUT_BUCKET = "my-ocr-results-output" # Must be an existing GCS bucket name
LOCAL_PDF_PATH = "path/to/your/multipage_newspaper.pdf" # Local path for input PDF
LOCAL_OUTPUT_TEXT_PATH = "newspaper_ocr_output.txt" # Local path for final text output
CREDENTIALS_JSON_PATH = "path/to/your/credentials.json" # Path to your Service Account JSON key file
# -------------------------------------------

def authenticate_client(credentials_path):
    """Loads credentials from a Service Account JSON file."""
    if not os.path.exists(credentials_path):
        raise FileNotFoundError(f"Credentials file not found at: {credentials_path}")
    
    print(f"Loading credentials from {credentials_path}...")
    
    try:
        credentials = service_account.Credentials.from_service_account_file(credentials_path)
        return credentials
    except Exception as e:
        raise ValueError(
            f"Failed to load credentials from {credentials_path}. "
            "Please ensure this is a Google Cloud Service Account Key JSON file, not an OAuth 2.0 Client ID file. "
            f"Original error: {e}"
        )

def upload_file_to_gcs(credentials, bucket_name, local_file_path, gcs_destination_name):
    """Uploads a local file to GCS and returns the GCS URI."""
    storage_client = storage.Client(credentials=credentials)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(gcs_destination_name)
    
    print(f"Uploading {local_file_path} to gs://{bucket_name}/{gcs_destination_name}...")
    blob.upload_from_filename(local_file_path)
    return f"gs://{bucket_name}/{gcs_destination_name}"

def download_and_structure_ocr(
    credentials,
    project_id: str,
    location: str,
    gcs_output_uri: str,
    local_output_path: str,
    gcs_input_uri: str,
):
    """
    Downloads Document AI output from GCS and structures the columnar text.
    """
    print("Starting post-processing and text structuring...")

    storage_client = storage.Client(credentials=credentials)
    bucket_name = gcs_output_uri.split("//")[1].split("/")[0]
    prefix = gcs_output_uri.split("//")[1].split("/", 1)[1]

    output_bucket = storage_client.get_bucket(bucket_name)
    blobs = output_bucket.list_blobs(prefix=prefix)
    
    all_structured_text = []
    
    # Initialize Document AI client for parsing Document objects
    docai_client = documentai.DocumentProcessorServiceClient(credentials=credentials)

    for blob in blobs:
        if not blob.name.endswith(".json"):
            continue

        # Download and parse the Document AI output JSON
        json_data = blob.download_as_bytes()
        document = documentai.Document.from_json(json_data, ignore_unknown_fields=True)
        
        # Determine the page number for the header
        try:
            page_range = blob.name.split('/')[-1].split('.')[0].split('-')
            page_num = page_range[1]
        except (IndexError, AttributeError):
            page_num = "Unknown" 

        # --- Columnar Segregation and Sorting ---
        for page in document.pages:
            page_text = f"\n\n--- NEWSPAPER PAGE {page_num} ---\n\n"
            
            text_blocks = []
            
            # The 'blocks' represent logical groupings, which often align with columns
            for block in page.blocks:
                if block.layout.bounding_poly.normalized_vertices:
                    # Calculate the center X-coordinate (normalized to 0-1)
                    x_coords = [v.x for v in block.layout.bounding_poly.normalized_vertices]
                    center_x = sum(x_coords) / len(x_coords)
                    
                    # Extract the block's text using the document's text content
                    if block.layout.text_anchor and block.layout.text_anchor.text_segments:
                        start_index = block.layout.text_anchor.text_segments[0].start_index
                        end_index = block.layout.text_anchor.text_segments[0].end_index
                        block_text = document.text[start_index:end_index].strip()

                        if block_text:
                            text_blocks.append((center_x, block_text))
            
            # Sort the blocks by their calculated center_x coordinate (left-to-right)
            text_blocks.sort(key=lambda x: x[0])
            
            # Reconstruct the column-segregated text
            for i, (_, text) in enumerate(text_blocks):
                column_header = f"--- COLUMN {i + 1} ---\n"
                page_text += column_header + text + "\n\n"

            all_structured_text.append(page_text)

    # Write all structured text to the local output file
    with open(local_output_path, "w", encoding="utf-8") as f:
        f.write("".join(all_structured_text))

    print(f"\nSuccessfully wrote structured OCR to {local_output_path}")

def delete_gcs_files(credentials, bucket_name, gcs_uri):
    """Deletes all blobs under a specific GCS prefix."""
    storage_client = storage.Client(credentials=credentials)
    bucket = storage_client.bucket(bucket_name)
    prefix = gcs_uri.split("//")[1].split("/", 1)[1]
    
    blobs = bucket.list_blobs(prefix=prefix)
    
    delete_count = 0
    for blob in blobs:
        blob.delete()
        delete_count += 1
    
    print(f"Cleaned up {delete_count} temporary files under gs://{bucket_name}/{prefix}")

def process_document_ai_batch(credentials, project_id, location, processor_id, gcs_input_uri, gcs_output_uri):
    """Starts the Document AI batch process and waits for completion."""
    docai_client = documentai.DocumentProcessorServiceClient(credentials=credentials)

    processor_name = docai_client.processor_path(project_id, location, processor_id)
    
    # --- CORRECTED: Use 'documents' field instead of 'gcs_documents' ---
    
    # 1. Create the singular GcsDocument object
    single_gcs_document = documentai.GcsDocument(
        gcs_uri=gcs_input_uri,
        mime_type="application/pdf"
    )

    # 2. Create the GcsDocuments wrapper message with 'documents' field
    gcs_documents_wrapper = documentai.GcsDocuments(
        documents=[single_gcs_document]  # Changed from 'gcs_documents' to 'documents'
    )

    # 3. Pass the wrapper object to the BatchDocumentsInputConfig constructor
    input_config = documentai.BatchDocumentsInputConfig(
        gcs_documents=gcs_documents_wrapper
    )

    # --- END FIX ---

    output_config = documentai.DocumentOutputConfig(
        gcs_output_config=documentai.DocumentOutputConfig.GcsOutputConfig(
            gcs_uri=gcs_output_uri
        )
    )

    request = documentai.BatchProcessRequest(
        name=processor_name,
        input_documents=input_config,
        document_output_config=output_config,
    )

    # Start the batch process
    operation = docai_client.batch_process_documents(request=request)

    print(f"Waiting for Document AI operation to complete...")
    operation.result()  # Wait for completion
    print("Document AI batch process complete.")

def main():
    """Orchestrates the local upload, Document AI processing, and local download/structuring."""
    
    if not os.path.exists(LOCAL_PDF_PATH):
        print(f"ERROR: Local PDF file not found at {LOCAL_PDF_PATH}")
        return

    try:
        # 1. AUTHENTICATION
        credentials = authenticate_client(CREDENTIALS_JSON_PATH)

        # Generate unique GCS paths for input and output
        timestamp = time.strftime("%Y%m%d%H%M%S")
        input_file_name = os.path.basename(LOCAL_PDF_PATH)
        gcs_input_destination = f"temp_input/{input_file_name}_{timestamp}.pdf"
        gcs_output_prefix = f"temp_output/{input_file_name.replace('.pdf', '')}_{timestamp}/"
        
        # 2. LOCAL UPLOAD to GCS
        gcs_input_uri = upload_file_to_gcs(
            credentials, GCS_INPUT_BUCKET, LOCAL_PDF_PATH, gcs_input_destination
        )
        gcs_output_uri = f"gs://{GCS_OUTPUT_BUCKET}/{gcs_output_prefix}"
        
        # 3. DOCUMENT AI PROCESSING
        process_document_ai_batch(
            credentials,
            PROJECT_ID,
            LOCATION,
            PROCESSOR_ID,
            gcs_input_uri,
            gcs_output_uri,
        )

        # 4. DOWNLOAD and STRUCTURE OCR
        download_and_structure_ocr(
            credentials,
            PROJECT_ID,
            LOCATION,
            gcs_output_uri,
            LOCAL_OUTPUT_TEXT_PATH,
            gcs_input_uri,
        )
        
    except Exception as e:
        print(f"\nAn error occurred during the process: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # 5. CLEAN UP TEMPORARY GCS FILES
        if 'credentials' in locals() and 'gcs_input_uri' in locals() and credentials:
            try:
                delete_gcs_files(credentials, GCS_INPUT_BUCKET, gcs_input_uri)
            except Exception as e:
                print(f"Error cleaning up input files: {e}")
        if 'credentials' in locals() and 'gcs_output_uri' in locals() and credentials:
            try:
                delete_gcs_files(credentials, GCS_OUTPUT_BUCKET, gcs_output_uri)
            except Exception as e:
                print(f"Error cleaning up output files: {e}")

if __name__ == "__main__":
    main()
