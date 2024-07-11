import os
import json
import customtkinter as ctk
from tkinter import filedialog, messagebox

# Set the appearance and theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

def human_readable_size(size):
    # Convert size to a human-readable format
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0
    while size >= 1024.0 and unit_index < len(units) - 1:
        size /= 1024.0
        unit_index += 1
    return f"{size:.2f} {units[unit_index]}"

def rename_files(directory, prefixes, extensions, insert_prefix):
    count = 0
    total_size = 0
    files_renamed = False
    rename_mapping = []
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    total_files = len(files)
    progress_bar.set(0)

    for filename in files:
        progress_bar.set((count + 1) / total_files)
        app.update_idletasks()
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
                    result_text.insert(ctk.END, "Renamed files:\n")
                result_text.insert(ctk.END, f'{count}. {filename} -> {new_filename}\n')
        
        # Update status label dynamically
        status_label.configure(text=f"{count} {'item' if total_files == 1 else 'items'}    {human_readable_size(total_size)}")

    if not files_renamed:
        messagebox.showinfo("Info", "No files need to be renamed. All files are already in the desired format.")
    else:
        with open(os.path.join(directory, 'rename_log.json'), 'w') as log_file:
            json.dump(rename_mapping, log_file)
        undo_button.configure(state=ctk.NORMAL)
        save_log_button.configure(state=ctk.NORMAL)
        messagebox.showinfo("Renaming Complete", "Files have been renamed successfully!")

def undo_rename(directory):
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
                result_text.insert(ctk.END, "Undone renaming:\n")
            result_text.insert(ctk.END, f'{count}. {os.path.basename(new_file)} -> {os.path.basename(old_file)}\n')

    os.remove(log_file_path)
    undo_button.configure(state=ctk.DISABLED)
    save_log_button.configure(state=ctk.DISABLED)
    messagebox.showinfo("Undo Complete", "Renaming has been undone.")

def select_directory():
    directory = filedialog.askdirectory()
    if directory:
        directory_path.set(directory)
        result_text.delete("1.0", ctk.END)
        rename_button.configure(state=ctk.NORMAL)
        undo_button.configure(state=ctk.DISABLED)
        
        # Calculate total size and file count
        total_size = sum(os.path.getsize(os.path.join(directory, f)) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)))
        total_files = len([f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))])
        status_label.configure(text=f"{total_files} {'item' if total_files == 1 else 'items'}    {human_readable_size(total_size)}")

def on_directory_entry_change(*args):
    path = directory_path.get()
    if os.path.exists(path) and os.path.isdir(path):
        rename_button.configure(state=ctk.NORMAL)
    else:
        rename_button.configure(state=ctk.DISABLED)

def save_log(directory):
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

# Create the main application window
app = ctk.CTk()
app.title("File Renamer")
app.geometry("800x700")

# Directory path variable
directory_path = ctk.StringVar()
directory_path.trace("w", on_directory_entry_change)

# Create and place widgets
title_label = ctk.CTkLabel(app, text="File Renamer", font=ctk.CTkFont(size=20, weight="bold"))
title_label.pack(pady=10)

select_button = ctk.CTkButton(app, text="Select Directory", command=select_directory)
select_button.pack(pady=10)

directory_entry = ctk.CTkEntry(app, textvariable=directory_path, width=400)
directory_entry.pack(pady=10)

status_label = ctk.CTkLabel(app, text="")
status_label.pack(pady=5)

prefix_label = ctk.CTkLabel(app, text="Prefixes to remove (comma separated):")
prefix_label.pack(pady=5)
prefix_entry = ctk.CTkEntry(app, width=400)
prefix_entry.pack(pady=5)
prefix_entry.insert(0, "IMG_,VID_")

extension_label = ctk.CTkLabel(app, text="File extensions to rename (comma separated):")
extension_label.pack(pady=5)
extension_entry = ctk.CTkEntry(app, width=400)
extension_entry.pack(pady=5)
extension_entry.insert(0, ".jpg,.mp4")

insert_prefix_label = ctk.CTkLabel(app, text="Prefix to insert:")
insert_prefix_label.pack(pady=5)
insert_prefix_entry = ctk.CTkEntry(app, width=400)
insert_prefix_entry.pack(pady=5)

rename_button = ctk.CTkButton(app, text="Rename Files", command=lambda: rename_files(directory_path.get(), prefix_entry.get().split(','), extension_entry.get().split(','), insert_prefix_entry.get()), state=ctk.DISABLED)
rename_button.pack(pady=10)

undo_button = ctk.CTkButton(app, text="Undo Rename", command=lambda: undo_rename(directory_path.get()), state=ctk.DISABLED)
undo_button.pack(pady=10)

save_log_button = ctk.CTkButton(app, text="Save Log", command=lambda: save_log(directory_path.get()), state=ctk.DISABLED)
save_log_button.pack(pady=10)

result_text = ctk.CTkTextbox(app, width=700, height=200)
result_text.pack(pady=10)

progress_bar = ctk.CTkProgressBar(app, width=400)
progress_bar.pack(pady=10)

# Run the application
app.mainloop()