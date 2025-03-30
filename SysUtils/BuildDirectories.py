# BuildDirectories.py

import os

def create_directory(path):
    try:
        os.makedirs(path, exist_ok=True)
        print(f"Created: {path}")
    except Exception as e:
        print(f"Failed to create {path}: {e}")

def main():
    base_dir = os.getcwd()

    directories = [
        "..Exclude",
        "AddThese",
        "AddTheseNow",
        "Core",
        "Docs/API",
        "GUI",
        "KnowledgeDatabase/OldVersions",
        "Notes/2024-03-21",
        "Scripts",
        "SysUtils",
        "Tests/Integration",
        "Tests/Unit",
        "UI",
        "Utils"
    ]

    for directory in directories:
        create_directory(os.path.join(base_dir, directory))

    # Create empty placeholder files to represent the structure (optional)
    print("\nDirectory structure created.")

if __name__ == "__main__":
    main()
