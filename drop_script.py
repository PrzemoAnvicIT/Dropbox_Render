import tkinter as tk
from tkinter import ttk, messagebox
import dropbox
from datetime import datetime
# Initialize the Dropbox client with your access token

ACCESS_TOKEN = 'YOUR_TOKEN_HERE'  # Replace with your access token

class DropboxApp:
    def __init__(self, root):
        self.dbx = dropbox.Dropbox(ACCESS_TOKEN)

        self.root = root
        self.root.title("Dropbox File Lister")
        self.root.geometry("900x700")

        self.create_widgets()

    def create_widgets(self):
        # Create and place the folder path entry
        self.folder_path_label = ttk.Label(self.root, text="Dropbox Folder Paths (comma separated):", font=('Consolas', 12))
        self.folder_path_label.pack(pady=10)

        self.folder_path_entry = ttk.Entry(self.root, width=70, font=('Consolas', 12))
        self.folder_path_entry.pack(pady=10)

        # Create and place the list files button
        self.list_files_button = ttk.Button(self.root, text="List Files", command=self.create_tabs)
        self.list_files_button.pack(pady=10)

        # Create the notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(pady=10, padx=10, fill='both', expand=True)

    def create_tabs(self):
        folder_paths = self.folder_path_entry.get().split(',')
        if not folder_paths:
            messagebox.showerror("Error", "Please enter at least one folder path")
            return

        # Clear existing tabs
        for tab in self.notebook.tabs():
            self.notebook.forget(tab)

        for folder_path in folder_paths:
            folder_path = folder_path.strip()
            if not folder_path.startswith('/'):
                folder_path = '/' + folder_path
            
            tab_frame = ttk.Frame(self.notebook)
            self.notebook.add(tab_frame, text=folder_path)

            files_text = tk.Text(tab_frame, wrap='word', state='normal', font=('Consolas', 12), bg="#2e2e2e", fg="white")
            files_text.pack(pady=10, padx=10, fill='both', expand=True)
            files_text.tag_configure('label', foreground='lightblue')
            files_text.tag_configure('value', foreground='white')

            self.list_files(folder_path, files_text)

    def list_files(self, folder_path, files_text):
        try:
            response = self.dbx.files_list_folder(folder_path, recursive=True)
            files_text.config(state='normal')
            files_text.delete(1.0, tk.END)

            file_entries = []
            for entry in response.entries:
                if isinstance(entry, dropbox.files.FileMetadata):
                    file_entries.append(entry)
            
            while response.has_more:
                response = self.dbx.files_list_folder_continue(response.cursor)
                for entry in response.entries:
                    if isinstance(entry, dropbox.files.FileMetadata):
                        file_entries.append(entry)

            # Sort files by creation time
            sorted_files = sorted(file_entries, key=lambda e: e.client_modified)

            # Display file details
            for entry in sorted_files:
                file_name = entry.name
                file_type = file_name.split('.')[-1]
                size = entry.size
                if size >= 1024 ** 3:
                    size_str = f"{size / 1024 ** 3:.2f} GB"
                else:
                    size_str = f"{size / 1024 ** 2:.2f} MB"
                
                files_text.insert(tk.END, "File: ", 'label')
                files_text.insert(tk.END, f"{file_name}\n", 'value')
                files_text.insert(tk.END, "Type: ", 'label')
                files_text.insert(tk.END, f"{file_type}\n", 'value')
                files_text.insert(tk.END, "Created at: ", 'label')
                files_text.insert(tk.END, f"{entry.client_modified}\n", 'value')
                files_text.insert(tk.END, "Size: ", 'label')
                files_text.insert(tk.END, f"{size_str}\n", 'value')
                files_text.insert(tk.END, "-" * 40 + "\n", 'label')

            if sorted_files:
                # Display total number of files
                total_files = len(sorted_files)
                files_text.insert(tk.END, f"\nTotal number of files: {total_files}\n", 'label')

                # Display the newest and oldest file details
                oldest_file = sorted_files[0]
                newest_file = sorted_files[-1]

                files_text.insert(tk.END, "\n" + "-" * 40 + "\n", 'label')
                files_text.insert(tk.END, "Oldest File\n", 'label')
                files_text.insert(tk.END, "File: ", 'label')
                files_text.insert(tk.END, f"{oldest_file.name}\n", 'value')
                files_text.insert(tk.END, "Type: ", 'label')
                files_text.insert(tk.END, f"{oldest_file.name.split('.')[-1]}\n", 'value')
                files_text.insert(tk.END, "Created at: ", 'label')
                files_text.insert(tk.END, f"{oldest_file.client_modified}\n", 'value')
                files_text.insert(tk.END, "Size: ", 'label')
                size = oldest_file.size
                if size >= 1024 ** 3:
                    size_str = f"{size / 1024 ** 3:.2f} GB"
                else:
                    size_str = f"{size / 1024 ** 2:.2f} MB"
                files_text.insert(tk.END, f"{size_str}\n", 'value')

                files_text.insert(tk.END, "\n" + "-" * 40 + "\n", 'label')
                files_text.insert(tk.END, "Newest File\n", 'label')
                files_text.insert(tk.END, "File: ", 'label')
                files_text.insert(tk.END, f"{newest_file.name}\n", 'value')
                files_text.insert(tk.END, "Type: ", 'label')
                files_text.insert(tk.END, f"{newest_file.name.split('.')[-1]}\n", 'value')
                files_text.insert(tk.END, "Created at: ", 'label')
                files_text.insert(tk.END, f"{newest_file.client_modified}\n", 'value')
                files_text.insert(tk.END, "Size: ", 'label')
                size = newest_file.size
                if size >= 1024 ** 3:
                    size_str = f"{size / 1024 ** 3:.2f} GB"
                else:
                    size_str = f"{size / 1024 ** 2:.2f} MB"
                files_text.insert(tk.END, f"{size_str}\n", 'value')

                # Calculate and display the time difference
                time_difference = newest_file.client_modified - oldest_file.client_modified
                files_text.insert(tk.END, "\n" + "-" * 40 + "\n", 'label')
                files_text.insert(tk.END, f"Time difference between oldest and newest file: {time_difference}\n", 'label')

            files_text.config(state='disabled')

        except dropbox.exceptions.ApiError as err:
            messagebox.showerror("Error", f"Failed to list folder contents: {err}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DropboxApp(root)
    root.mainloop()
