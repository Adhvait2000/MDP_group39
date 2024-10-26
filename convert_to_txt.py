import os
import json
import shutil

# Get the current directory
folder_path = os.getcwd()
output_folder = os.path.join(folder_path, "txt_files")
os.makedirs(output_folder, exist_ok=True)

# Define the image file extensions to skip (these will be copied as-is)
image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"}

# Walk through all files and folders in the current directory recursively
for root, dirs, files in os.walk(folder_path):
    for filename in files:
        file_path = os.path.join(root, filename)
        file_extension = os.path.splitext(filename)[1].lower()

        # Define the target folder in the output directory to maintain structure
        relative_path = os.path.relpath(root, folder_path)
        target_folder = os.path.join(output_folder, relative_path)
        os.makedirs(target_folder, exist_ok=True)

        # If the file is an image or unsupported format, copy it as-is
        if file_extension in image_extensions:
            shutil.copy2(file_path, target_folder)
            continue

        try:
            # If it's a .ipynb file, attempt to convert code cells to .txt
            if file_extension == ".ipynb":
                with open(file_path, 'r', encoding='utf-8') as f:
                    notebook_content = json.load(f)
                # Extract code cells
                code_cells = [cell['source'] for cell in notebook_content['cells'] if cell['cell_type'] == 'code']
                content = '\n'.join([''.join(cell) for cell in code_cells])

            # For other text-based files (.py, .yaml, etc.)
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

            # Define the new filename with .txt extension
            new_filename = os.path.splitext(filename)[0] + ".txt"
            new_file_path = os.path.join(target_folder, new_filename)

            # Write the converted content to the new .txt file
            with open(new_file_path, 'w', encoding='utf-8') as new_file:
                new_file.write(content)

        except (UnicodeDecodeError, json.JSONDecodeError, IOError) as e:
            # If file is inaccessible or conversion fails, copy it as-is
            print(f"Could not convert {file_path}. Copying as-is due to: {e}")
            shutil.copy2(file_path, target_folder)

print(f"Process complete. All files have been saved in {output_folder}, with text files converted to .txt format where possible.")
