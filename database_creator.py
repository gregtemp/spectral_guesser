import os
import json
import tkinter as tk
from tkinterdnd2 import TkinterDnD, DND_FILES

display_font = "Cascadia Code"

#
#           DICT MANAGEMENT
#

# take a folder and list all the .wav files
def get_wav_files(folder_path):
    """
    Returns a list of .wav files in the given folder.

    Parameters:
    folder_path (str): The path to the folder to search for .wav files.

    Returns:
    list: A list of .wav file paths.
    """
    wav_files = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.wav'):                   # possible to include other file types here
                wav_files.append(os.path.join(root, file))
    return wav_files

# adds .wav files at target_path to target_label in target_dict
def add_folder_to_dict(target_dict, target_label, target_path):
    """
    Adds all the the .wav files in the target_path folder to the target_dict at the key target_label

    Parameters:
    target_dict (dict): The dictionary to add the filepaths to
    target_label (str): Key to add filepaths to in the target_dict (as a set)
    target_path (str): The path to the folder to search for .wav files.

    Returns nothing
    """
    filename_list = get_wav_files(target_path)
    if target_label not in target_dict:
        target_dict[target_label] = set(filename_list)  # Use a set to avoid duplicates
    else:
        target_dict[target_label].update(filename_list)  # Update the set with new files

# load json and return as dict
def load_json_to_dict(target_dict, json_path):
    """
    Loads json to dict
    also converts lists of filenames to sets

    Parameters:
    target_dict (dict): dict to load to
    json_path (str): json file with sample dict

    """

    with open(json_path, 'r') as json_file:
        json_dict = json.load(json_file)
        
    # Convert lists back to sets
    for key in json_dict:
        json_dict[key] = set(json_dict[key])
    
    target_dict.update(json_dict)
    


# save dictionary to json
def save_dict_to_json(dict_to_save, json_path):
    """
    Saves json to dict

    Parameters:
    dict_to_save (dict): dictionary to save as json
    json_path (str): json file path to save to

    Returns nothing
    """
    # Convert the sets back to lists
    dict_to_save = {key: list(value) for key, value in dict_to_save.items()}
    
    with open(json_path, 'w') as json_file:
        json.dump(dict_to_save, json_file, indent=4)  # Using indent for pretty-printing

    print(f"Json file ready -> {json_path}")


#
#           TKINTER
#

# setup window style for tkinter (shape size etc)
def setup_window_style(root):
    root.title("Sample Organizer")
    
    font = (display_font, 10)
    root.option_add("*Font", font)

    # Set window size
    root.geometry("600x400")


def update_key_listbox(key_listbox, samples_dict):
    # Populate key listbox
    for key in samples_dict.keys():
        key_listbox.insert(tk.END, key)

def update_sample_listbox(samples_dict, selected_label, sample_listbox):
    sample_listbox.delete(0, tk.END)
    if selected_label in samples_dict:
        for sample_filename in samples_dict[selected_label]:
            # sample_listbox.insert(tk.END, item)
            folder_name = os.path.basename(os.path.dirname(sample_filename))
            sample_name = os.path.splitext(os.path.basename(sample_filename))[0]
            sample_listbox.insert(tk.END, f"{folder_name:<15} {sample_name}")



# show list boxes for sample labels and names (folder    samp_name)
def add_list_boxes(frame, samples_dict):
    def update_sample_list(event):
        selected_indices = key_listbox.curselection()
        if not selected_indices:
            return
        selected_index = selected_indices[0]
        selected_label = key_listbox.get(selected_index)
        sample_listbox.delete(0, tk.END)
        sorted_list = sorted(samples_dict[selected_label])
        for sample_filename in sorted_list:
            folder_name = os.path.basename(os.path.dirname(sample_filename))
            sample_name = os.path.splitext(os.path.basename(sample_filename))[0]
            sample_listbox.insert(tk.END, f"{folder_name:<15} {sample_name}")
    
    # Create a PanedWindow to hold the Listboxes
    paned_window = tk.PanedWindow(frame, orient=tk.HORIZONTAL)
    paned_window.pack(fill=tk.BOTH, expand=True)

    # Create Listbox for keys
    key_listbox = tk.Listbox(paned_window, selectmode=tk.SINGLE)
    paned_window.add(key_listbox)

    # Create Listbox for samples
    sample_listbox = tk.Listbox(paned_window, selectmode=tk.SINGLE)
    paned_window.add(sample_listbox)

    
    # Populate key listbox
    for key in samples_dict.keys():
        key_listbox.insert(tk.END, key)

    # Bind the selection event to update the sample list
    key_listbox.bind('<<ListboxSelect>>', update_sample_list)

    return key_listbox, sample_listbox

def add_load_save_buttons(frame, samples_dict):
    # Add Load and Save buttons
    button_frame = tk.Frame(frame)
    button_frame.pack(fill=tk.X, pady=5)

    def load_samples():
        load_json_to_dict(samples_dict, "samples.json")
        key_listbox.delete(0, tk.END)
        for key in samples_dict:
            key_listbox.insert(tk.END, key)

    def save_samples():
        save_dict_to_json(samples_dict, "samples.json")

    load_button = tk.Button(button_frame, text="Load JSON", command=load_samples)
    load_button.pack(side=tk.LEFT, padx=5)

    save_button = tk.Button(button_frame, text="Save JSON", command=save_samples)
    save_button.pack(side=tk.LEFT, padx=5)


def add_key_button(root, frame, samples_dict, key_listbox):
    
    button_frame = tk.Frame(frame)
    button_frame.pack(pady=10)

    def add_new_key():
        def save_new_key(event=None):
            new_key = key_entry.get().strip()
            if new_key and new_key not in samples_dict:
                samples_dict[new_key] = set()
                key_listbox.insert(tk.END, new_key)
            popup.destroy()

        popup = tk.Toplevel(root)
        popup.title("Add New Key/Label to Dictionary")

        tk.Label(popup, text="Enter new key name:").pack(pady=10)
        key_entry = tk.Entry(popup)
        key_entry.pack(padx=10, pady=10)
        key_entry.focus_set()  # Automatically focus on the text box
        key_entry.bind("<Return>", save_new_key)  # Bind Enter key to save

        save_button = tk.Button(popup, text="Save", command=save_new_key)
        save_button.pack(pady=10)
    
    add_key_button = tk.Button(button_frame, text="Add Key", command=add_new_key)
    add_key_button.pack(side=tk.LEFT, padx=5)


def on_drop(event, target_dict, key_listbox, sample_listbox):
    folder_path = event.data.strip('{}')  # Remove curly braces if present
    selected_label = key_listbox.get(tk.ACTIVE)
    if os.path.isdir(folder_path):
        add_folder_to_dict(target_dict, selected_label, folder_path)
        update_sample_listbox(target_dict, selected_label, sample_listbox)
    

# create the main window to display tkinter ui
def create_main_window(samples_dict):

    root = TkinterDnD.Tk()  # Use TkinterDnD instead of tk.Tk
    setup_window_style(root)

    frame = tk.Frame(root)
    frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    key_listbox, sample_listbox = add_list_boxes(frame, samples_dict)
    add_key_button(root, frame, samples_dict, key_listbox)
    add_load_save_buttons(frame, samples_dict)

    sample_listbox.drop_target_register(DND_FILES)
    sample_listbox.dnd_bind('<<Drop>>', lambda e: on_drop(e, samples_dict, key_listbox, sample_listbox))

    root.mainloop()








#
#           TESTS
#

# Basic loading folders and load/save json
def test1():
    samples_dict = {}

    kick_path1 = "C:\\Users\\gregt\\Documents\\Samples\\just_kicks"
    kick_path2 = "C:\\Users\\gregt\\Documents\\Samples\\Seppa\\CHOP FADE LEVEL VOL 1\\CFL1 Drums\\Kicks"
    snare_path = "C:\\Users\\gregt\\Documents\\Samples\\Seppa\\CHOP FADE LEVEL VOL 1\\CFL1 Drums\\Snares"

    add_folder_to_dict(samples_dict, "kick", kick_path1)
    add_folder_to_dict(samples_dict, "kick", kick_path2)
    add_folder_to_dict(samples_dict, "snare", snare_path)
    # print(samples_dict)

    # Save the dictionary to a JSON file
    save_dict_to_json(samples_dict, "samples.json")

    # Load the dictionary from the JSON file
    loaded_samples_dict = {}
    load_json_to_dict(loaded_samples_dict, "samples.json")
    print(loaded_samples_dict)



#
#           MAIN
#

if __name__ == "__main__":
    samples_dict = {}
    load_json_to_dict(samples_dict, "samples.json")
    create_main_window(samples_dict)
    # test1()
    