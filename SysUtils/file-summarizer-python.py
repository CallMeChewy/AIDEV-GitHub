#!/usr/bin/env python3
"""
File Content Summarizer

This script takes multiple files as input and combines their contents into a single summary file.
Each file's content is added with a header showing the filename.

Usage:
    python file_summarizer.py file1.txt file2.txt ... [-o output_file.txt]
    
Arguments:
    file1.txt, file2.txt, ... : Input files to be summarized
    -o, --output : Optional argument to specify output file (default: summary.txt)
"""

import argparse
import os
import sys

def create_summary(input_files, output_file):
    """
    Create a summary file from the contents of input files.
    
    Args:
        input_files (list): List of file paths to summarize
        output_file (str): Path to the output summary file
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as out_f:
            for file_path in input_files:
                if not os.path.exists(file_path):
                    print(f"Warning: File {file_path} does not exist. Skipping.", file=sys.stderr)
                    continue
                    
                try:
                    with open(file_path, 'r', encoding='utf-8') as in_f:
                        # Write file header
                        out_f.write(f"\n\n==== {os.path.basename(file_path)} ====\n\n")
                        # Write file content
                        out_f.write(in_f.read())
                except Exception as e:
                    print(f"Error reading file {file_path}: {str(e)}", file=sys.stderr)
        
        print(f"Summary created successfully: {output_file}")
        return True
    
    except Exception as e:
        print(f"Error creating summary file: {str(e)}", file=sys.stderr)
        return False

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Combine multiple files into a single summary file")
    parser.add_argument('files', nargs='+', help='Input files to summarize')
    parser.add_argument('-o', '--output', default='summary.txt', help='Output summary file (default: summary.txt)')
    
    args = parser.parse_args()
    
    if not args.files:
        print("Error: No input files provided.", file=sys.stderr)
        parser.print_help()
        return 1
    
    # Create the summary
    success = create_summary(args.files, args.output)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
