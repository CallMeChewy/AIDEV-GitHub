import os
import re
import shutil
from pathlib import Path

def convert_markdown_to_text(source_dir="Docs/KnowledgeDatabaseIndex", dest_dir="Text"):
    """
    Converts all Markdown (.md) files in the source directory to text (.txt) files,
    placing them in a 'Text' subdirectory while preserving the folder structure.
    Also updates internal references from .md to .txt.
    
    Args:
        source_dir: The source directory containing Markdown files
        dest_dir: The destination subdirectory (default: "Text")
    """
    # Ensure the source directory exists
    if not os.path.exists(source_dir):
        print(f"Error: Source directory '{source_dir}' does not exist.")
        return
        
    # Create the destination directory if it doesn't exist
    text_dir = os.path.join(source_dir, dest_dir)
    os.makedirs(text_dir, exist_ok=True)
    
    # Regular expression to find Markdown references like [text](filename.md)
    md_ref_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\.md\)')
    
    # Find all .md files in the source directory and its subdirectories
    md_files = []
    for root, _, files in os.walk(source_dir):
        # Skip the Text directory itself
        if os.path.abspath(root).startswith(os.path.abspath(text_dir)):
            continue
            
        for file in files:
            if file.endswith('.md'):
                md_files.append(os.path.join(root, file))
    
    print(f"Found {len(md_files)} Markdown files to convert.")
    
    # Process each file
    for md_file in md_files:
        # Create relative path to maintain directory structure
        rel_path = os.path.relpath(md_file, source_dir)
        
        # Create destination directory structure
        dest_file_dir = os.path.join(text_dir, os.path.dirname(rel_path))
        os.makedirs(dest_file_dir, exist_ok=True)
        
        # Generate output filename
        txt_filename = os.path.basename(md_file).replace('.md', '.txt')
        txt_file = os.path.join(dest_file_dir, txt_filename)
        
        print(f"Converting: {md_file} -> {txt_file}")
        
        # Read the content of the Markdown file
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update internal references from .md to .txt
        content = md_ref_pattern.sub(r'[\1](\2.txt)', content)
        
        # Update any other explicit mentions of .md files
        content = re.sub(r'(\S+)\.md\b', r'\1.txt', content)
        
        # Write the updated content to the text file
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    print(f"\nConversion complete. {len(md_files)} files converted to .txt format in the {dest_dir} directory.")

if __name__ == "__main__":
    # Use the specified base directory
    source_dir = "Docs/KnowledgeDatabaseIndex"
    
    # Run the conversion
    convert_markdown_to_text(source_dir)