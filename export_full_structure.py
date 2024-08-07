import os
import zipfile
import fnmatch

def write_project_structure_to_file(root_dir, output_file, exclude_patterns=None):
    if exclude_patterns is None:
        exclude_patterns = []


    def should_exclude(path):
        # Проверка по маске
        for pattern in exclude_patterns:
            if fnmatch.fnmatch(path, pattern):
                return True
        return False


    def write_files_in_dir(dir_path, relative_path):
        for entry in os.listdir(dir_path):
            full_path = os.path.join(dir_path, entry)
            rel_path = os.path.join(relative_path, entry)

            # Преобразуем относительный путь в абсолютный для проверки исключений
            abs_path = os.path.abspath(full_path)

            if should_exclude(abs_path):
                continue

            if os.path.isdir(full_path):
                f.write(f"{rel_path}/\n")
                write_files_in_dir(full_path, rel_path)
            else:
                f.write(f"{rel_path}\n")
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as file:
                    f.write(file.read())
                    f.write("\n")


    with open(output_file, 'w', encoding='utf-8') as f:
        write_files_in_dir(root_dir, "")

def zip_project_file(input_file, output_zip):
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(input_file)

# Parameters
project_root = '/Users/oca/Projects/Python/Transcribe'
output_txt_file = 'project_structure.txt'
output_zip_file = 'project_structure.zip'
exclude_patterns = [
    '*postgres_data/*', '*.idea/*', '*.venv/*', '*.git/*', '*.DS_Store', '*.dockerignore', '*.gitignore',
    '*.jpg', '*.svg', '*.png', '*.mp3', '*poetry*', '*pyproject.toml', '*.zip','*.txt',
    '*export_*.py', '*.md', '.env'
]

# Execute the functions
write_project_structure_to_file(project_root, output_txt_file, exclude_patterns)
zip_project_file(output_txt_file, output_zip_file)

print(f"Project structure has been written to {output_txt_file} and zipped as {output_zip_file}.")