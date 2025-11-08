import requests
import os
import time

# --- Configuration ---
# The file containing all your URLs, one per line
URL_FILE = 'urls.txt'

# The log file to track successfully downloaded URLs
LOG_FILE = 'downloaded.log'

# The directory where PDFs will be saved
DOWNLOAD_DIR = 'pdf_downloads'

# How many files to download per session
BATCH_SIZE = 10

# A polite delay (in seconds) between requests to avoid overwhelming the server
DELAY_BETWEEN_REQUESTS = 1 
# --- End of Configuration ---


def get_unique_filepath(directory, filename):
    """
    Checks if a file exists and returns a unique path by adding _1, _2, etc.
    """
    filepath = os.path.join(directory, filename)
    
    if not os.path.exists(filepath):
        # If the path doesn't exist, it's already unique
        return filepath
    
    # If it exists, find a unique name
    base, ext = os.path.splitext(filename)
    counter = 1
    while os.path.exists(filepath):
        # Create a new filename like "myfile_1.pdf", "myfile_2.pdf"
        new_filename = f"{base}_{counter}{ext}"
        filepath = os.path.join(directory, new_filename)
        counter += 1
        
    return filepath

def main():
    """
    Main function to run the batch downloader.
    """
    # --- 1. Setup Environment ---
    
    # Create the download directory if it doesn't exist
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)
        print(f"Created download directory: {DOWNLOAD_DIR}")
    
    # Check if the URL_FILE exists
    if not os.path.exists(URL_FILE):
        print(f"Error: URL file not found: {URL_FILE}")
        print("Please create this file and populate it with your PDF URLs, one per line.")
        # Create a dummy file for the user
        with open(URL_FILE, 'w') as f:
            f.write("https.example.com/file1.pdf\n")
            f.write("https.example.com/file2.pdf\n")
        print(f"An example {URL_FILE} has been created for you.")
        return

    # Create the log file if it doesn't exist
    if not os.path.exists(LOG_FILE):
        open(LOG_FILE, 'a').close()
        print(f"Created new log file: {LOG_FILE}")

    # --- 2. Read State and Calculate Work ---
    
    try:
        # Read all URLs from the master list. Use a set for efficiency.
        with open(URL_FILE, 'r') as f:
            all_urls = {line.strip() for line in f if line.strip()}
        
        # Read all successfully downloaded URLs from the log file.
        with open(LOG_FILE, 'r') as f:
            done_urls = {line.strip() for line in f if line.strip()}
    except Exception as e:
        print(f"Error reading URL/log files: {e}")
        return

    # Calculate the set of URLs that still need to be downloaded
    pending_urls = list(all_urls - done_urls)
    
    if not pending_urls:
        print("All files are already downloaded. Nothing to do.")
        return

    print(f"Found {len(all_urls)} total URLs.")
    print(f"Found {len(done_urls)} already downloaded.")
    print(f"Found {len(pending_urls)} URLs remaining.")

    # --- 3. Select Batch for This Session ---
    
    # Get the next batch of URLs to download
    urls_to_download_this_session = pending_urls[:BATCH_SIZE]
    
    print(f"\nStarting a new batch of {len(urls_to_download_this_session)} files...")

    # Use a session object for connection pooling
    session = requests.Session()
    # Set a user-agent to look like a real browser
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})

    success_count = 0
    
    # --- 4. Process the Batch ---
    
    for url in urls_to_download_this_session:
        try:
            # Generate a base filename from the URL
            # Takes the last part of the URL (e.g., "file.pdf")
            # and splits at "?" to remove query parameters
            filename_from_url = url.split('/')[-1].split('?')[0]

            # Basic sanitization
            safe_filename = "".join(c for c in filename_from_url if c.isalnum() or c in ('.', '_', '-'))
            
            # Ensure it has a .pdf extension
            if not safe_filename.lower().endswith('.pdf'):
                safe_filename += ".pdf"

            # Get a unique filepath (handles "file.pdf", "file_1.pdf", etc.)
            filepath = get_unique_filepath(DOWNLOAD_DIR, safe_filename)
            
            print(f"Downloading: {url}\n         -> {filepath}")
            
            # Make the request
            response = session.get(url, timeout=30, allow_redirects=True)
            
            # Raise an error for bad responses (404, 500, etc.)
            response.raise_for_status()

            # Check if the content is actually a PDF
            content_type = response.headers.get('content-type', '').lower()
            if 'application/pdf' not in content_type:
                print(f"   ...Warning: Content-type is '{content_type}', not 'application/pdf'. Saving anyway.")

            # Write the file content
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            # --- 5. Log Success ---
            # IMPORTANT: Only log *after* the file is successfully saved.
            with open(LOG_FILE, 'a') as f:
                f.write(url + '\n')
            
            print("   ...Success.")
            success_count += 1

        except requests.exceptions.RequestException as e:
            print(f"   ...Failed to download {url}: {e}")
        except Exception as e:
            print(f"   ...An unexpected error occurred for {url}: {e}")
        finally:
            # Always pause to be polite to the server
            time.sleep(DELAY_BETWEEN_REQUESTS)

    # --- 6. Report and Exit ---
    print(f"\nBatch complete. Successfully downloaded {success_count} files this session.")
    
    remaining = len(pending_urls) - len(urls_to_download_this_session)
    if remaining > 0:
        print(f"{remaining} files remaining in total. Run the script again to download the next batch.")
    else:
        print("All files have been successfully downloaded!")

if __name__ == "__main__":
    main()
