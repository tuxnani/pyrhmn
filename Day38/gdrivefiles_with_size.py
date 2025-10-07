import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def list_files_in_folder(folder_id):
    """
    Lists all files (name and size) in a given Google Drive folder.
    
    Note: The 'size' field is not available for Google Workspace files 
    (like Google Docs, Sheets, Slides, etc.). It will be None for those files.
    
    Args:
        folder_id: The ID of the Google Drive folder.
    Returns:
        A list of dictionaries, each containing 'name', 'id', and 'size' (in bytes) of the file.
    """
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('drive', 'v3', credentials=creds)

        results = []
        page_token = None
        while True:
            # Modified 'fields' to include 'size'
            response = service.files().list(
                q=f"'{folder_id}' in parents and trashed=false",
                spaces='drive',
                # Request 'size' along with 'id', 'name', and 'mimeType'
                fields='nextPageToken, files(id, name, size, mimeType)', 
                pageToken=page_token
            ).execute()
            
            for file in response.get('files', []):
                # Drive items (like Google Docs) don't have a size property.
                # Also, we check that it's not a folder
                if file.get('mimeType') != 'application/vnd.google-apps.folder':
                    results.append({
                        'name': file.get('name'),
                        'id': file.get('id'),
                        # Add size, which will be None for Google native files (Docs, Sheets, etc.)
                        'size': file.get('size'), 
                        'mimeType': file.get('mimeType')
                    })

            page_token = response.get('nextPageToken', None)
            if not page_token:
                break
        return results

    except HttpError as error:
        print(f'An error occurred: {error}')
        return []

def format_bytes(size):
    """
    Converts a size in bytes to a human-readable format (e.g., KB, MB, GB).
    """
    if size is None:
        return 'N/A (Google Native File)'
    
    size = int(size)
    if size == 0:
        return '0 B'
    
    # Define the units
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    
    # Calculate the exponent for the unit
    i = 0
    while size >= 1024 and i < len(units) - 1:
        size /= 1024.0
        i += 1
        
    return f"{size:.2f} {units[i]}"

if __name__ == '__main__':
    # Replace this with your actual folder ID
    # Use a real folder ID or set it to the placeholder to see the warning
    folder_id = '1wcRwEIs9jDvQGqlJuJ1PF4_En9QiPRxS' 

    if folder_id == 'YOUR_GOOGLE_DRIVE_FOLDER_ID':
        print("Please replace 'YOUR_GOOGLE_DRIVE_FOLDER_ID' with your actual Google Drive folder ID.")
        print("Example: folder_id = '1wcRwEIs9jDvQGqlJuJ1PF4_En9QiPRxS'")
    else:
        files = list_files_in_folder(folder_id)

        output_file = 'drive_file_list_with_size.txt'
        if files:
            print(f"Listing files from folder ID: {folder_id}")
            print("-" * 50)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"Files in the folder (ID: {folder_id}):\n")
                f.write("-" * 50 + "\n")
                
                # Format header
                header = "{:<5} {:<60} {:>25}".format("No.", "File Name", "File Size")
                print(header)
                f.write(header + "\n")
                
                print("-" * 50)
                f.write("-" * 50 + "\n")

                for i, file in enumerate(files, start=1):
                    # Format size for display
                    file_size_formatted = format_bytes(file.get('size'))
                    
                    # Output line format
                    line = "{:<5} {:<60} {:>25}".format(
                        i, 
                        file['name'], 
                        file_size_formatted
                    )
                    
                    print(line)
                    f.write(line + "\n")
                
                f.write("\nTotal files: {}\n".format(len(files)))

            print("-" * 50)
            print(f"{len(files)} files (including name and size) written to {output_file}")
        else:
            print("No files found or an error occurred.")