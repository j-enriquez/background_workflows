import os


def read_python_files(directory):
    """
    Recursively finds and reads all Python files in the given directory.
    Prints the file path and its contents.
    """
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py") or file.endswith(".md") or file.endswith(".txt") or file.endswith(".yml"):
                file_path = os.path.join(root, file)
                print(f"\n=== FILE: {file_path} ===\n")
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        print(f.read())
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")


if __name__ == "__main__":
    for target_directory in ["../background_workflows","../docs"]:
        if os.path.isdir(target_directory):
            read_python_files(target_directory)
        else:
            print("Invalid directory path.")
