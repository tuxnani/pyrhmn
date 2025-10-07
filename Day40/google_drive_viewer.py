import tkinter as tk
from tkinter import ttk, messagebox
import os.path
import pickle
from datetime import datetime
import pandas as pd

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.pickle
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']

class GoogleDriveViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Google Drive File Viewer")
        self.root.geometry("1100x650")
        
        self.service = None
        self.current_folder_id = 'root'
        self.folder_stack = []  # For navigation history
        self.all_items = []  # All items in current folder
        self.current_page = 0
        self.items_per_page = 1000
        
        self.setup_ui()
        
    def setup_ui(self):
        # Top frame for login button
        top_frame = tk.Frame(self.root, pady=10)
        top_frame.pack(fill=tk.X)
        
        self.login_btn = tk.Button(
            top_frame, 
            text="Sign in with Google", 
            command=self.authenticate,
            bg="#4285f4",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=5
        )
        self.login_btn.pack(side=tk.LEFT, padx=10)
        
        self.status_label = tk.Label(
            top_frame, 
            text="Not signed in", 
            font=("Arial", 10)
        )
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        self.refresh_btn = tk.Button(
            top_frame,
            text="Refresh",
            command=self.refresh_current_folder,
            state=tk.DISABLED,
            padx=10,
            pady=5
        )
        self.refresh_btn.pack(side=tk.LEFT, padx=5)
        
        self.export_btn = tk.Button(
            top_frame,
            text="Export Current View",
            command=self.export_to_excel,
            state=tk.DISABLED,
            bg="#34a853",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=5
        )
        self.export_btn.pack(side=tk.RIGHT, padx=10)
        
        # Navigation frame
        nav_frame = tk.Frame(self.root, pady=5)
        nav_frame.pack(fill=tk.X)
        
        self.back_btn = tk.Button(
            nav_frame,
            text="← Back",
            command=self.navigate_back,
            state=tk.DISABLED,
            padx=10,
            pady=3
        )
        self.back_btn.pack(side=tk.LEFT, padx=10)
        
        self.path_label = tk.Label(
            nav_frame,
            text="Location: My Drive",
            font=("Arial", 9),
            fg="#666"
        )
        self.path_label.pack(side=tk.LEFT, padx=10)
        
        # Pagination frame
        pagination_frame = tk.Frame(self.root, pady=5)
        pagination_frame.pack(fill=tk.X)
        
        self.prev_btn = tk.Button(
            pagination_frame,
            text="← Previous",
            command=self.previous_page,
            state=tk.DISABLED,
            padx=10,
            pady=3
        )
        self.prev_btn.pack(side=tk.LEFT, padx=10)
        
        self.page_label = tk.Label(
            pagination_frame,
            text="Page 1 of 1",
            font=("Arial", 9)
        )
        self.page_label.pack(side=tk.LEFT, padx=10)
        
        self.next_btn = tk.Button(
            pagination_frame,
            text="Next →",
            command=self.next_page,
            state=tk.DISABLED,
            padx=10,
            pady=3
        )
        self.next_btn.pack(side=tk.LEFT, padx=5)
        
        self.items_count_label = tk.Label(
            pagination_frame,
            text="",
            font=("Arial", 9),
            fg="#666"
        )
        self.items_count_label.pack(side=tk.RIGHT, padx=10)
        
        # Frame for treeview
        tree_frame = tk.Frame(self.root)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        
        # Treeview
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("name", "type", "size", "modified"),
            show="headings",
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        # Define columns
        self.tree.heading("name", text="Name")
        self.tree.heading("type", text="Type")
        self.tree.heading("size", text="Size")
        self.tree.heading("modified", text="Last Modified")
        
        self.tree.column("name", width=450)
        self.tree.column("type", width=100)
        self.tree.column("size", width=120)
        self.tree.column("modified", width=180)
        
        # Double-click to open folders
        self.tree.bind("<Double-Button-1>", self.on_item_double_click)
        
        # Pack everything
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
    def authenticate(self):
        """Authenticate with Google Drive API"""
        creds = None
        
        # Check if token.pickle exists
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, let user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists('credentials.json'):
                    messagebox.showerror(
                        "Error", 
                        "credentials.json file not found!\n\n"
                        "Please download OAuth credentials from Google Cloud Console."
                    )
                    return
                
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    messagebox.showerror("Authentication Error", str(e))
                    return
            
            # Save credentials for next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        try:
            self.service = build('drive', 'v3', credentials=creds)
            self.status_label.config(text="Signed in successfully", fg="green")
            self.login_btn.config(text="Sign Out", command=self.sign_out)
            self.refresh_btn.config(state=tk.NORMAL)
            self.export_btn.config(state=tk.NORMAL)
            
            # Load root folder automatically after sign in
            self.load_folder('root')
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect: {str(e)}")
    
    def sign_out(self):
        """Sign out and clear credentials"""
        if os.path.exists('token.pickle'):
            os.remove('token.pickle')
        
        self.service = None
        self.status_label.config(text="Not signed in", fg="black")
        self.login_btn.config(text="Sign in with Google", command=self.authenticate)
        self.refresh_btn.config(state=tk.DISABLED)
        self.export_btn.config(state=tk.DISABLED)
        self.back_btn.config(state=tk.DISABLED)
        
        # Clear tree and reset state
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.all_items = []
        self.folder_stack = []
        self.current_folder_id = 'root'
        self.path_label.config(text="Location: My Drive")
        
    def load_folder(self, folder_id, folder_name=None):
        """Load contents of a specific folder with pagination"""
        if not self.service:
            messagebox.showwarning("Warning", "Please sign in first")
            return
        
        try:
            # Clear existing items
            self.all_items = []
            
            # Query for items in the folder
            query = f"'{folder_id}' in parents and trashed=false"
            page_token = None
            
            while True:
                results = self.service.files().list(
                    q=query,
                    pageSize=1000,
                    fields="nextPageToken, files(id, name, size, modifiedTime, mimeType)",
                    pageToken=page_token
                ).execute()
                
                items = results.get('files', [])
                self.all_items.extend(items)
                
                page_token = results.get('nextPageToken')
                if not page_token:
                    break
            
            # Sort: folders first, then files, alphabetically
            self.all_items.sort(key=lambda x: (
                x['mimeType'] != 'application/vnd.google-apps.folder',
                x['name'].lower()
            ))
            
            # Update current folder tracking
            self.current_folder_id = folder_id
            self.current_page = 0
            
            # Update path display
            if folder_name:
                self.path_label.config(text=f"Location: {folder_name}")
            elif folder_id == 'root':
                self.path_label.config(text="Location: My Drive")
            
            # Enable/disable back button
            if self.folder_stack:
                self.back_btn.config(state=tk.NORMAL)
            else:
                self.back_btn.config(state=tk.DISABLED)
            
            # Display first page
            self.display_current_page()
            
        except HttpError as error:
            messagebox.showerror("Error", f"An error occurred: {error}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load folder: {str(e)}")
    
    def display_current_page(self):
        """Display items for the current page"""
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Calculate page boundaries
        start_idx = self.current_page * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, len(self.all_items))
        
        # Get items for current page
        page_items = self.all_items[start_idx:end_idx]
        
        # Populate treeview
        for item in page_items:
            name = item['name']
            mime_type = item.get('mimeType', '')
            
            # Determine type
            if mime_type == 'application/vnd.google-apps.folder':
                item_type = "📁 Folder"
            else:
                item_type = "📄 File"
            
            size = self.format_size(item.get('size', '0')) if item_type == "📄 File" else "-"
            modified = self.format_date(item.get('modifiedTime', ''))
            
            # Store item id in tags for navigation
            self.tree.insert("", tk.END, values=(name, item_type, size, modified), 
                           tags=(item['id'], mime_type))
        
        # Update pagination controls
        total_pages = (len(self.all_items) + self.items_per_page - 1) // self.items_per_page
        if total_pages == 0:
            total_pages = 1
        
        self.page_label.config(text=f"Page {self.current_page + 1} of {total_pages}")
        self.items_count_label.config(
            text=f"Showing {start_idx + 1}-{end_idx} of {len(self.all_items)} items"
        )
        
        # Enable/disable pagination buttons
        self.prev_btn.config(state=tk.NORMAL if self.current_page > 0 else tk.DISABLED)
        self.next_btn.config(state=tk.NORMAL if end_idx < len(self.all_items) else tk.DISABLED)
    
    def previous_page(self):
        """Go to previous page"""
        if self.current_page > 0:
            self.current_page -= 1
            self.display_current_page()
    
    def next_page(self):
        """Go to next page"""
        total_pages = (len(self.all_items) + self.items_per_page - 1) // self.items_per_page
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.display_current_page()
    
    def on_item_double_click(self, event):
        """Handle double-click on items"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        tags = item['tags']
        
        if len(tags) >= 2:
            item_id = tags[0]
            mime_type = tags[1]
            
            # If it's a folder, navigate into it
            if mime_type == 'application/vnd.google-apps.folder':
                folder_name = item['values'][0]
                # Save current location to stack
                self.folder_stack.append({
                    'id': self.current_folder_id,
                    'name': self.path_label.cget("text").replace("Location: ", "")
                })
                self.load_folder(item_id, folder_name)
    
    def navigate_back(self):
        """Navigate back to previous folder"""
        if self.folder_stack:
            previous = self.folder_stack.pop()
            self.load_folder(previous['id'], previous['name'])
    
    def refresh_current_folder(self):
        """Refresh the current folder view"""
        current_name = self.path_label.cget("text").replace("Location: ", "")
        self.load_folder(self.current_folder_id, current_name if current_name != "My Drive" else None)
    
    def format_size(self, size_str):
        """Format file size to human readable format"""
        try:
            size = int(size_str)
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if size < 1024.0:
                    return f"{size:.2f} {unit}"
                size /= 1024.0
            return f"{size:.2f} PB"
        except (ValueError, TypeError):
            return "N/A"
    
    def format_date(self, date_str):
        """Format ISO date string to readable format"""
        if not date_str:
            return "N/A"
        try:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return date_str
    
    def export_to_excel(self):
        """Export current view (current page only) to Excel file"""
        # Get only visible items from current page
        visible_items = []
        for item_id in self.tree.get_children():
            item = self.tree.item(item_id)
            values = item['values']
            visible_items.append({
                'Name': values[0],
                'Type': values[1],
                'Size': values[2],
                'Last Modified': values[3]
            })
        
        if not visible_items:
            messagebox.showwarning("Warning", "No data to export")
            return
        
        try:
            # Create DataFrame
            df = pd.DataFrame(visible_items)
            
            # Generate filename with timestamp and location
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            location = self.path_label.cget("text").replace("Location: ", "").replace(" ", "_")
            filename = f'gdrive_{location}_page{self.current_page + 1}_{timestamp}.xlsx'
            
            # Export to Excel
            df.to_excel(filename, index=False, engine='openpyxl')
            
            messagebox.showinfo(
                "Success", 
                f"Exported {len(visible_items)} items from current view to:\n{filename}"
            )
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {str(e)}")

def main():
    root = tk.Tk()
    app = GoogleDriveViewer(root)
    root.mainloop()

if __name__ == '__main__':
    main()