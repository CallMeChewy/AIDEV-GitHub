#!/bin/bash
#
# File Summarizer Shell Script
# Combines all .md and .py files into a single summary file with timestamp
#
# Usage:
#   ./summarize_files.sh [options]
#

# Set default values
SEARCH_DIR="$(pwd)"
OUTPUT_DIR="$(pwd)"

# Display usage information
show_usage() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -d, --directory DIR   Search for files in specified directory (default: current directory)"
    echo "  -o, --output DIR      Specify output directory (default: current directory)"
    echo "  -h, --help            Display this help message"
    echo ""
    echo "This script will automatically find all .md and .py files in the specified directory"
    echo "and combine them into a summary file with a timestamp in the filename."
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -d|--directory)
            SEARCH_DIR="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            echo "Error: Unknown option $1"
            show_usage
            exit 1
            ;;
    esac
done

# Check if search directory exists
if [[ ! -d "$SEARCH_DIR" ]]; then
    echo "Error: Directory '$SEARCH_DIR' does not exist."
    exit 1
fi

# Check if output directory exists
if [[ ! -d "$OUTPUT_DIR" ]]; then
    echo "Error: Output directory '$OUTPUT_DIR' does not exist."
    exit 1
fi

# Get current timestamp in MM-DD-YY HH:MM AM/PM format
TIMESTAMP=$(date "+%m-%d-%y %I:%M %p")
OUTPUT_FILE="$OUTPUT_DIR/Summary $TIMESTAMP.txt"

# Find all .md and .py files in the search directory
MD_FILES=($(find "$SEARCH_DIR" -maxdepth 1 -type f -name "*.md" | sort))
PY_FILES=($(find "$SEARCH_DIR" -maxdepth 1 -type f -name "*.py" | sort))
ALL_FILES=("${MD_FILES[@]}" "${PY_FILES[@]}")

# Check if we found any files
if [[ ${#ALL_FILES[@]} -eq 0 ]]; then
    echo "No .md or .py files found in '$SEARCH_DIR'."
    exit 1
fi

# Create output file with header
echo "Summary created on $TIMESTAMP" > "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Process each input file
for file in "${ALL_FILES[@]}"; do
    echo -e "\n\n==== $(basename "$file") ====\n" >> "$OUTPUT_FILE"
    cat "$file" >> "$OUTPUT_FILE"
done

echo "Summary created successfully: $OUTPUT_FILE"
echo "Processed ${#ALL_FILES[@]} files (${#MD_FILES[@]} .md, ${#PY_FILES[@]} .py)"

exit 0
