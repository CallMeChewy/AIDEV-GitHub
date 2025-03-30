#!/usr/bin/env python3
"""
File Content Summarizer

This script combines the contents of all .md and .py files in the current directory
into a single summary file with a timestamp in the filename.

Usage:
    python file_summarizer.py [-o output_directory]
    
Arguments:
    -o, --output : Optional argument to specify output directory (default: current directory)
"""

import argparse
import os
import sys
import glob
import datetime

def create_summary(output_dir=None):
    """
    Create a summary file from all .md and .py files in the current directory.
    
    Args:
        output_dir (str, optional): Directory to save the output file. Defaults to current directory.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Get current timestamp in MM-DD-YY HH:MM AM/PM format
        now = datetime.datetime.now()
        timestamp = now.strftime("%m-%d-%y %I:%M %p")
        
        # Create output filename with timestamp
        output_filename = f"Summary {timestamp}.txt"
        
        # Set output directory to current directory if not specified
        if not output_dir:
            output_dir = os.getcwd()
        
        # Full path to output file
        output_path = os.path.join(output_dir, output_filename)
        
        # Get all .md and .py files in the current directory
        md_files = glob.glob("*.md")
        py_files = glob.glob("*.py")
        input_files = sorted(md_files + py_files)
        
        if not input_files:
            print("No .md or .py files found in the current directory.")
            return False
            
        with open(output_path, 'w', encoding='utf-8') as out_f:
            out_f.write(f"Summary created on {timestamp}\n\n")
            
            for file_path in input_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as in_f:
                        # Write file header
                        out_f.write(f"\n\n==== {os.path.basename(file_path)} ====\n\n")
                        # Write file content
                        out_f.write(in_f.read())
                except Exception as e:
                    print(f"Error reading file {file_path}: {str(e)}", file=sys.stderr)
        
        print(f"Summary created successfully: {output_path}")
        print(f"Processed {len(input_files)} files ({len(md_files)} .md, {len(py_files)} .py)")
        return True
    
    except Exception as e:
        print(f"Error creating summary file: {str(e)}", file=sys.stderr)
        return False

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Combine .md and .py files into a single summary file")
    parser.add_argument('-o', '--output', help='Output directory (default: current directory)')
    
    args = parser.parse_args()
    
    # Create the summary
    success = create_summary(args.output)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
