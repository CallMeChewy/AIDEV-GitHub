#!/bin/bash
#
# File Summarizer Shell Script
# Combines multiple files into a single summary file
#
# Usage:
#   ./summarize_files.sh -o output_file.txt file1.txt file2.txt ...
#   ./summarize_files.sh -o output_file.txt -d directory/  # process all files in directory
#

# Default output file
OUTPUT_FILE="summary.txt"
FILE_LIST=()
PROCESS_DIR=false
DIR_PATH=""

# Display usage information
show_usage() {
    echo "Usage: $0 [options] file1 file2 ... fileN"
    echo ""
    echo "Options:"
    echo "  -o, --output FILE     Specify output file (default: summary.txt)"
    echo "  -d, --directory DIR   Process all files in the specified directory"
    echo "  -h, --help            Display this help message"
    echo ""
    echo "Examples:"
    echo "  $0 file1.txt file2.txt -o summary.txt"
    echo "  $0 -d /path/to/files/ -o summary.txt"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -o|--output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        -d|--directory)
            PROCESS_DIR=true
            DIR_PATH="$2"
            shift 2
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        -*)
            echo "Error: Unknown option $1"
            show_usage
            exit 1
            ;;
        *)
            FILE_LIST+=("$1")
            shift
            ;;
    esac
done

# Check if we have files to process
if [[ ${#FILE_LIST[@]} -eq 0 && "$PROCESS_DIR" == false ]]; then
    echo "Error: No input files specified."
    show_usage
    exit 1
fi

# Process directory if specified
if [[ "$PROCESS_DIR" == true ]]; then
    if [[ ! -d "$DIR_PATH" ]]; then
        echo "Error: Directory '$DIR_PATH' does not exist."
        exit 1
    fi
    
    # Get all files in the directory
    for file in "$DIR_PATH"/*; do
        if [[ -f "$file" ]]; then
            FILE_LIST+=("$file")
        fi
    done
    
    if [[ ${#FILE_LIST[@]} -eq 0 ]]; then
        echo "Error: No files found in directory '$DIR_PATH'."
        exit 1
    fi
fi

# Create empty output file
> "$OUTPUT_FILE"

# Process each input file
for file in "${FILE_LIST[@]}"; do
    if [[ ! -f "$file" ]]; then
        echo "Warning: File '$file' does not exist. Skipping."
        continue
    fi
    
    echo -e "\n\n==== $(basename "$file") ====\n" >> "$OUTPUT_FILE"
    cat "$file" >> "$OUTPUT_FILE"
done

echo "Summary created successfully: $OUTPUT_FILE"
echo "Processed ${#FILE_LIST[@]} files."

exit 0
