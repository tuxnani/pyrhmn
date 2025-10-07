import os
import tkinter as tk
from tkinter import messagebox, scrolledtext, simpledialog, Toplevel
import sys

# --- Google API Imports ---
# These are the necessary libraries for interacting with Google Drive
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    # This block ensures the app provides feedback if libraries are missing
    # when run as a script before being compiled into an EXE.
    tk_root = tk.Tk()
    tk_root.withdraw()
    messagebox.showerror(
        "Missing Libraries",
        "Required libraries (google-api-python-client, google-auth-oauthlib, google-auth) "
        "are not installed. Please run 'pip install google-api-python-client google-auth-oauthlib google-auth'."
    )
    sys.exit(1)


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
TOKEN_FILE = 'token.json'
CREDENTIALS_FILE = 'credentials.json'

class DriveListerApp:
    def __init__(self, master):
        self.master = master
        master.title("Google Drive File Lister")
        master.geometry("800x600")
        master.config(bg="#f0f4f8")

        # Set up a frame for input
        input_frame = tk.Frame(master, bg="#f0f4f8", padx=20, pady=20)
        input_frame.pack(pady=10)

        # 1. Folder ID Input
        tk.Label(input_frame, text="Google Drive Folder ID:", font=("Inter", 12, "bold"), bg="#f0f4f8").pack(anchor="w")
        self.folder_id_entry = tk.Entry(input_frame, width=50, font=("Inter", 12), bd=2, relief="groove")
        self.folder_id_entry.insert(0, "e.g., 1A2bC3dE4fG5hI6jK7lM")
        self.folder_id_entry.pack(pady=5)

        # 2. Authentication Button (for setup)
        tk.Label(input_frame, text="1. Run Authentication Setup (Only needs to be run once):", font=("Inter", 10), bg="#f0f4f8").pack(anchor="w", pady=(10, 0))
        self.auth_button = tk.Button(input_frame, text="Run OAuth Setup", command=self.run_oauth_flow, bg="#4CAF50", fg="white", font=("Inter", 12, "bold"), relief="raised", bd=3)
        self.auth_button.pack(pady=5)
        
        # 3. List Files Button
        tk.Label(input_frame, text="2. List Files:", font=("Inter", 10), bg="#f0f4f8").pack(anchor="w", pady=(10, 0))
        self.list_button = tk.Button(input_frame, text="List Files and Sizes", command=self.process_list_files, bg="#2196F3", fg="white", font=("Inter", 14, "bold"), relief="raised", bd=3)
        self.list_button.pack(pady=10)

        # 4. Output Area
        tk.Label(master, text="Results:", font=("Inter", 12, "bold"), bg="#f0f4f8").pack(anchor="w", padx=20)
        self.output_text = scrolledtext.ScrolledText(master, wrap=tk.WORD, font=("Consolas", 10), height=15, width=90, bg="white", fg="#333", bd=2, relief="sunken")
        self.output_text.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        self.output_text.insert(tk.END, "Click 'Run OAuth Setup' first to generate your token.json file.\n")
        self.output_text.insert(tk.END, "Then paste your Google Drive Folder ID and click 'List Files and Sizes'.")

    def log_output(self, message):
        """Helper function to append text to the output area."""
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)
        self.master.update_idletasks() # Force update the UI

    def run_oauth_flow(self):
        """Handles the initial browser-based authentication to generate token.json."""
        self.log_output("\n--- Running OAuth Setup ---")

        if not os.path.exists(CREDENTIALS_FILE):
            self.log_output(f"ERROR: {CREDENTIALS_FILE} not found.")
            messagebox.showerror("Error", f"Please place your downloaded {CREDENTIALS_FILE} file in the same directory as this application.")
            return

        try:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            
            # Use 'run_local_server' to automatically open the browser
            self.log_output("Opening browser for authorization. Please follow the steps in the browser.")
            creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open(TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())

            self.log_output(f"SUCCESS: Authentication complete. {TOKEN_FILE} created.")
            messagebox.showinfo("Success", f"Authentication successful! You can now use the 'List Files and Sizes' button.")

        except Exception as e:
            self.log_output(f"AUTH ERROR: Failed to complete OAuth flow: {e}")
            messagebox.showerror("Authentication Error", f"Failed to authenticate. See output for details. Ensure your {CREDENTIALS_FILE} is valid.")


    def authenticate(self):
        """Loads or refreshes credentials."""
        creds = None
        
        # The app requires token.json, which is generated by the OAuth flow.
        if os.path.exists(TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

        # If there are no (valid) credentials available, prompt the user.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                self.log_output("Refreshing token...")
                creds.refresh(Request())
                with open(TOKEN_FILE, 'w') as token:
                    token.write(creds.to_json())
            else:
                self.log_output(f"ERROR: {TOKEN_FILE} is missing or invalid. Please run the 'Run OAuth Setup' first.")
                return None
        return creds

    def format_bytes(self, size_str):
        """
        Converts a size in bytes to a human-readable format (e.g., KB, MB, GB).
        """
        if size_str is None:
            return 'N/A (Google Native File)'
        
        try:
            size = int(size_str)
        except ValueError:
            return 'Size Error'

        if size == 0:
            return '0 B'
        
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        i = 0
        while size >= 1024 and i < len(units) - 1:
            size /= 1024.0
            i += 1
            
        return f"{size:.2f} {units[i]}"

    def list_files_in_folder(self, folder_id, service):
        """
        Fetches files and their size from the given Google Drive folder ID.
        """
        results = []
        page_token = None
        
        self.log_output(f"Fetching files for Folder ID: {folder_id}...")

        while True:
            try:
                response = service.files().list(
                    q=f"'{folder_id}' in parents and trashed=false",
                    spaces='drive',
                    # Request 'size' along with 'id', 'name', and 'mimeType'
                    fields='nextPageToken, files(id, name, size, mimeType)', 
                    pageToken=page_token
                ).execute()
                
                for file in response.get('files', []):
                    # Only process files, skip folders
                    if file.get('mimeType') != 'application/vnd.google-apps.folder':
                        results.append({
                            'name': file.get('name', 'Untitled'),
                            'size': file.get('size'), 
                        })

                page_token = response.get('nextPageToken', None)
                if not page_token:
                    break
            except HttpError as error:
                self.log_output(f'DRIVE API ERROR: An HTTP error occurred: {error}')
                return []
            except Exception as e:
                self.log_output(f'UNKNOWN ERROR: An unexpected error occurred: {e}')
                return []
        
        return results

    def process_list_files(self):
        """Main method to run the file listing and display results."""
        folder_id = self.folder_id_entry.get().strip()
        self.output_text.delete(1.0, tk.END) # Clear previous output
        
        if not folder_id or folder_id == "e.g., 1A2bC3dE4fG5hI6jK7lM":
            self.log_output("ERROR: Please enter a valid Google Drive Folder ID.")
            messagebox.showwarning("Input Error", "Please enter a valid Google Drive Folder ID.")
            return

        creds = self.authenticate()
        if not creds:
            self.log_output("Authentication failed. Cannot proceed.")
            return

        try:
            # Build the Drive service
            service = build('drive', 'v3', credentials=creds)
            
            # Fetch the files
            files = self.list_files_in_folder(folder_id, service)

            if files:
                self.log_output("\n--- File List and Sizes ---")
                
                # Setup header for clean, columnar output
                header = "{:<5} {:<60} {:>25}".format("No.", "File Name", "File Size")
                self.log_output("-" * 90)
                self.log_output(header)
                self.log_output("-" * 90)

                for i, file in enumerate(files, start=1):
                    file_size_formatted = self.format_bytes(file.get('size'))
                    
                    line = "{:<5} {:<60} {:>25}".format(
                        i, 
                        file['name'], 
                        file_size_formatted
                    )
                    self.log_output(line)

                self.log_output("-" * 90)
                self.log_output(f"SUCCESS: {len(files)} files listed.")
            else:
                self.log_output(f"INFO: No files found in folder ID {folder_id} or a previous error occurred.")

        except Exception as e:
            self.log_output(f"CRITICAL ERROR: {e}")
            messagebox.showerror("Application Error", f"A critical error occurred: {e}")


if __name__ == '__main__':
    root = tk.Tk()
    app = DriveListerApp(root)
    root.mainloop()
