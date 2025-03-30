#!/bin/bash
# File: CodebaseSummary.sh
# Path: OllamaModelEditor/CodebaseSummary.sh
# Created: 2025-03-14
# Description: Generate a comprehensive codebase snapshot in a structured format

# Create timestamp for the output filename
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT_FILE="CodebaseSummary_${TIMESTAMP}.txt"

# Ensure script has execution permissions
if [[ ! -x "$0" ]]; then
    chmod +x "$0"
    echo "Added execute permissions to script"
fi

# Check if the tree command is available
if ! command -v tree &> /dev/null; then
    echo "Error: The 'tree' command is required but not found. Please install it first."
    exit 1
fi

# Start generating the file
echo "Generating codebase summary to ${OUTPUT_FILE}..."

# Create temp files for building the summary
TEMP_DIR=$(mktemp -d)
HEADER_FILE="${TEMP_DIR}/header.txt"
STRUCTURE_FILE="${TEMP_DIR}/structure.txt"
FILES_LIST="${TEMP_DIR}/files_list.txt"
FILES_CONTENT="${TEMP_DIR}/files_content.txt"

# Create the header
cat > "$HEADER_FILE" << 'EOF'
This file is a comprehensive codebase snapshot for the OllamaModelEditor project, generated to facilitate analysis and development.

================================================================
File Summary
================================================================

Purpose:
--------
This document provides a consolidated view of the project's source code, scripts,
HTML, and text files, excluding any files specified in the .gitignore file. 
It serves as a reference for developers, making it easier to understand the 
codebase structure and functionality in a single document.

File Format:
------------
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Multiple file entries, each consisting of:
5. List of Program files
6. List of Documents

EOF

# Generate directory structure using tree
echo "Generating directory structure..."
tree -f . > "$STRUCTURE_FILE"

# Create the files section header
echo "================================================================" > "$FILES_CONTENT"
echo "Files" >> "$FILES_CONTENT"
echo "================================================================" >> "$FILES_CONTENT"
echo "" >> "$FILES_CONTENT"

# Find relevant project files, respecting .gitignore patterns provided
echo "Finding relevant project files (.py, .sh, .md, .html, .txt)..."
find . \( -name "*.py" -o -name "*.sh" -o -name "*.md" -o -name "*.html" -o -name "*.txt" \) -type f \
    -not -path "./__pycache__/*" \
    -not -name "*.pyc" -not -name "*.pyo" -not -name "*.pyd" \
    -not -name "*.class" \
    -not -path "./.env" \
    -not -path "./.venv/*" \
    -not -name "*.log" \
    | sed 's|^\./||' | sort > "$FILES_LIST" # Remove leading ./ for cleaner paths

# Process each file found
echo "Processing files..."
while read -r FILE; do
    # Check if it's actually a file (find might list broken symlinks etc.)
    if [ -f "$FILE" ]; then
        echo "================" >> "$FILES_CONTENT"
        echo "File: ${FILE}" >> "$FILES_CONTENT" # Use the path from FILES_LIST
        echo "================" >> "$FILES_CONTENT"
        cat "$FILE" >> "$FILES_CONTENT"
        echo "" >> "$FILES_CONTENT"
    else
        echo "Warning: Skipping non-file item found: $FILE" >> "$OUTPUT_FILE" # Log skipped items
    fi
done < "$FILES_LIST"

# Combine all parts into the final file
cat "$HEADER_FILE" > "$OUTPUT_FILE"
echo "================================================================" >> "$OUTPUT_FILE"
echo "Directory Structure" >> "$OUTPUT_FILE"
echo "================================================================" >> "$OUTPUT_FILE"
cat "$STRUCTURE_FILE" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
cat "$FILES_CONTENT" >> "$OUTPUT_FILE"

echo "Codebase summary generated: ${OUTPUT_FILE}"

# Count total files included
NUM_TOTAL_FILES=$(wc -l < "$FILES_LIST")
echo "It contains ${NUM_TOTAL_FILES} files."

# List all included files
echo "" >> "$OUTPUT_FILE"
echo "================================================================" >> "$OUTPUT_FILE"
echo "List of Included Files" >> "$OUTPUT_FILE"
echo "================================================================" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "Files included:" >> "$OUTPUT_FILE"
cat "$FILES_LIST" >> "$OUTPUT_FILE"

echo "" >> "$OUTPUT_FILE"
echo "There are ${NUM_TOTAL_FILES} files included in the Files section of the CodebaseSummary document." >> "$OUTPUT_FILE"

# Clean up temporary files
rm -rf "$TEMP_DIR"
