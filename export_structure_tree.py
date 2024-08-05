import os
import fnmatch

def generate_tree(path, exclude, indent=0):
    """
    Генерирует текстовое представление структуры папок и файлов в виде дерева, исключая определенные файлы и папки по маскам.

    :param path: Путь к директории, структуру которой нужно отобразить.
    :param exclude: Список файлов и папок или масок, которые нужно исключить.
    :param indent: Отступ для вложенных уровней.
    :return: Текстовое представление структуры.
    """
    structure = ""
    try:
        items = sorted(os.listdir(path))
        for index, item in enumerate(items):
            item_path = os.path.join(path, item)
            if any(fnmatch.fnmatch(item, pat) for pat in exclude):
                continue

            if os.path.isdir(item_path):
                if index == len(items) - 1:
                    structure += " " * indent + "└── " + item + "\n"
                    structure += generate_tree(item_path, exclude, indent + 4)
                else:
                    structure += " " * indent + "├── " + item + "\n"
                    structure += generate_tree(item_path, exclude, indent + 4)
            else:
                if index == len(items) - 1:
                    structure += " " * indent + "└── " + item + "\n"
                else:
                    structure += " " * indent + "├── " + item + "\n"
    except PermissionError:
        structure += " " * indent + "├── [Permission Denied]\n"
    return structure

def save_tree_to_file(base_path, output_file, exclude):
    """
    Сохраняет текстовое представление структуры папок и файлов в файл, исключая определенные файлы и папки по маскам.

    :param base_path: Путь к базовой директории.
    :param output_file: Путь к выходному текстовому файлу.
    :param exclude: Список файлов и папок или масок, которые нужно исключить.
    """
    tree = generate_tree(base_path, exclude)
    with open(output_file, 'w') as f:
        f.write(tree)

# Путь к базовой директории
# base_path = '/Users/oca/Projects/Python/Transcribe/'
base_path = '/Users/oca/Projects/RPS/Techwind_NextJs_v2.2.0/Techwind_NextJs/Dashboard'

# Путь к выходному текстовому файлу
output_file = 'export_tree_structure.txt'

# Список файлов и папок, которые нужно исключить
exclude = [
    'postgres_data','.idea','.venv','.git','.DS_Store','.dockerignore', '.gitignore',
    '*.jpg','*.svg','*.png', '*.mp3'
]

# Сохраняем структуру в файл
save_tree_to_file(base_path, output_file, exclude)
