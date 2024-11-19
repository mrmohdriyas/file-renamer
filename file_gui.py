import os
import json
import customtkinter as ctk
from tkinter import filedialog, messagebox

# Set the appearance and theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class FileRenamerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Renamer")
        self.root.geometry("800x700")

        self.directory_path = ctk.StringVar()
        self.directory_path.trace("w", self.on_directory_entry_change)

        self.create_widgets()

    def create_widgets(self):
        title_label = ctk.CTkLabel(self.root, text="File Renamer", font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(pady=10)

        select_button = ctk.CTkButton(self.root, text="Select Directory", command=self.select_directory)
        select_button.pack(pady=10)

        directory_entry = ctk.CTkEntry(self.root, textvariable=self.directory_path, width=400)
        directory_entry.pack(pady=10)

        self.status_label = ctk.CTkLabel(self.root, text="")
        self.status_label.pack(pady=5)

        prefix_label = ctk.CTkLabel(self.root, text="Prefixes to remove (comma separated):")
        prefix_label.pack(pady=5)
        self.prefix_entry = ctk.CTkEntry(self.root, width=400)
        self.prefix_entry.pack(pady=5)
        self.prefix_entry.insert(0, "IMG_,VID_")

        extension_label = ctk.CTkLabel(self.root, text="File extensions to rename (comma separated):")
        extension_label.pack(pady=5)
        self.extension_entry = ctk.CTkEntry(self.root, width=400)
        self.extension_entry.pack(pady=5)
        self.extension_entry.insert(0, ".jpg,.mp4")

        insert_prefix_label = ctk.CTkLabel(self.root, text="Prefix to insert:")
        insert_prefix_label.pack(pady=5)
        self.insert_prefix_entry = ctk.CTkEntry(self.root, width=400)
        self.insert_prefix_entry.pack(pady=5)

        self.rename_button = ctk.CTkButton(self.root, text="Rename Files", command=self.rename_files, state=ctk.DISABLED)
        self.rename_button.pack(pady=10)

        self.undo_button = ctk.CTkButton(self.root, text="Undo Rename", command=self.undo_rename, state=ctk.DISABLED)
        self.undo_button.pack(pady=10)

        self.save_log_button = ctk.CTkButton(self.root, text="Save Log", command=self.save_log, state=ctk.DISABLED)
        self.save_log_button.pack(pady=10)

        self.result_text = ctk.CTkTextbox(self.root, width=700, height=200)
        self.result_text.pack(pady=10)

        self.progress_bar = ctk.CTkProgressBar(self.root, width=400)
        self.progress_bar.pack(pady=10)

    def human_readable_size(self, size):
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        unit_index = 0
        while size >= 1024.0 and unit_index < len(units) - 1:
            size /= 1024.0
            unit_index += 1
        return f"{size:.2f} {units[unit_index]}"

    def rename_files(self):
        directory = self.directory_path.get()
        prefixes = self.prefix_entry.get().split(',')
        extensions = self.extension_entry.get().split(',')
        insert_prefix = self.insert_prefix_entry.get()

        count = 0
        total_size = 0
        files_renamed = False
        rename_mapping = []
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        total_files = len(files)
        self.progress_bar.set(0)

        for filename in files:
            self.progress_bar.set((count + 1) / total_files)
            self.root.update_idletasks()
            file_path = os.path.join(directory, filename)
            total_size += os.path.getsize(file_path)
            if any(filename.startswith(prefix) for prefix in prefixes) and any(filename.lower().endswith(ext) for ext in extensions):
                new_filename = filename
                for prefix in prefixes:
                    if new_filename.startswith(prefix):
                        new_filename = insert_prefix + new_filename[len(prefix):]
                if new_filename != filename:
                    files_renamed = True
                    count += 1
                    old_file = os.path.join(directory, filename)
                    new_file = os.path.join(directory, new_filename)
                    os.rename(old_file, new_file)
                    rename_mapping.append((new_file, old_file))
                    if count == 1:
                        self.result_text.insert(ctk.END, "Renamed files:\n")
                    self.result_text.insert(ctk.END, f'{count}. {filename} -> {new_filename}\n')

            self.status_label.configure(text=f"{count} {'item' if total_files == 1 else 'items'}    {self.human_readable_size(total_size)}")

        if not files_renamed:
            messagebox.showinfo("Info", "No files need to be renamed. All files are already in the desired format.")
        else:
            with open(os.path.join(directory, 'rename_log.json'), 'w') as log_file:
                json.dump(rename_mapping, log_file)
            self.undo_button.configure(state=ctk.NORMAL)
            self.save_log_button.configure(state=ctk.NORMAL)
            messagebox.showinfo("Renaming Complete", "Files have been renamed successfully!")

    def undo_rename(self):
        directory = self.directory_path.get()
        log_file_path = os.path.join(directory, 'rename_log.json')
        if not os.path.exists(log_file_path):
            messagebox.showerror("Error", "No rename log found. Nothing to undo.")
            return

        with open(log_file_path, 'r') as log_file:
            rename_mapping = json.load(log_file)

        count = 0
        for new_file, old_file in rename_mapping:
            if os.path.exists(new_file):
                os.rename(new_file, old_file)
                count += 1
                if count == 1:
                    self.result_text.insert(ctk.END, "Undone renaming:\n")
                self.result_text.insert(ctk.END, f'{count}. {os.path.basename(new_file)} -> {os.path.basename(old_file)}\n')

        os.remove(log_file_path)
        self.undo_button.configure(state=ctk.DISABLED)
        self.save_log_button.configure(state=ctk.DISABLED)
        messagebox.showinfo("Undo Complete", "Renaming has been undone.")

    def select_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.directory_path.set(directory)
            self.result_text.delete("1.0", ctk.END)
            self.rename_button.configure(state=ctk.NORMAL)
            self.undo_button.configure(state=ctk.DISABLED)
            
            total_size = sum(os.path.getsize(os.path.join(directory, f)) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)))
            total_files = len([f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))])
            self.status_label.configure(text=f"{total_files} {'item' if total_files == 1 else 'items'}    {self.human_readable_size(total_size)}")

    def on_directory_entry_change(self, *args):
        path = self.directory_path.get()
        if os.path.exists(path) and os.path.isdir(path):
            self.rename_button.configure(state=ctk.NORMAL)
        else:
            self.rename_button.configure(state=ctk.DISABLED)

    def save_log(self):
        directory = self.directory_path.get()
        log_file_path = os.path.join(directory, 'rename_log.json')
        if not os.path.exists(log_file_path):
            messagebox.showerror("Error", "No rename log found. Nothing to save.")
            return

        with open(log_file_path, 'r') as log_file:
            rename_mapping = json.load(log_file)

        log_save_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if log_save_path:
            with open(log_save_path, 'w') as log_save_file:
                for new_file, old_file in rename_mapping:
                    log_save_file.write(f'{old_file} -> {new_file}\n')
            messagebox.showinfo("Log Saved", "Rename log has been saved.")

if __name__ == "__main__":
    app = ctk.CTk()
    FileRenamerApp(app)
    app.mainloop()
