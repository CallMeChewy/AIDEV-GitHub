#!/usr/bin/env python3
# File: DocumentProcessor.py
# Path: AIDEV-GitHub/Core/DocumentProcessor.py
# Standard: AIDEV-PascalCase-1.6
# Created: 2025-03-29
# Last Modified: 2025-03-29  8:30PM
# Description: Document processing module for loading and transforming Project Himalaya documents

import re
from pathlib import Path
from typing import Dict, List, Optional, Any

from Utils.LoggingManager import GetLogger

def LoadDocument(FilePath: Path) -> str:
    """
    Load document content from a file.
    
    Args:
        FilePath: Path to the document file
    
    Returns:
        str: Document content as string
    
    Raises:
        FileNotFoundError: If the file does not exist
        PermissionError: If the file cannot be read
        UnicodeDecodeError: If the file encoding is invalid
    """
    Logger = GetLogger("DocumentProcessor")
    Logger.debug(f"Loading document: {FilePath}")
    
    try:
        with open(FilePath, 'r', encoding='utf-8') as File:
            Content = File.read()
        return Content
    except UnicodeDecodeError:
        # Try with different encodings if UTF-8 fails
        Logger.warning(f"UTF-8 decoding failed for {FilePath}, trying alternative encodings")
        try:
            with open(FilePath, 'r', encoding='latin-1') as File:
                Content = File.read()
            return Content
        except Exception as Error:
            Logger.error(f"Failed to load document {FilePath}: {str(Error)}")
            raise

def ProcessDocument(Content: str) -> str:
    """
    Process document content for Jekyll compatibility.
    
    This function handles:
    1. Removing the original metadata header
    2. Preprocessing content for Jekyll compatibility
    3. Handling special formatting cases
    
    Args:
        Content: Document content as string
    
    Returns:
        str: Processed document content
    """
    Logger = GetLogger("DocumentProcessor")
    
    # Remove original metadata header
    Content = RemoveMetadataHeader(Content)
    
    # Process Jekyll-incompatible content
    Content = ProcessJekyllIncompatibleContent(Content)
    
    # Handle special syntax
    Content = ProcessSpecialSyntax(Content)
    
    return Content

def RemoveMetadataHeader(Content: str) -> str:
    """
    Remove the original metadata header from the document.
    
    The header format is:
    # Title
    **Created: Date**
    **Last Modified: Date**
    
    [Context: Value]
    [Other: Value]
    
    Args:
        Content: Document content as string
    
    Returns:
        str: Document content without metadata header
    """
    # Split content into lines
    Lines = Content.split('\n')
    
    # Skip title line (will be added by Jekyll)
    StartIndex = 0
    if Lines and Lines[0].startswith('# '):
        StartIndex = 1
    
    # Skip Created and Last Modified timestamps
    while StartIndex < len(Lines) and (
        Lines[StartIndex].startswith('**Created:') or 
        Lines[StartIndex].startswith('**Last Modified:') or
        Lines[StartIndex].strip() == ''
    ):
        StartIndex += 1
    
    # Skip metadata tags [Key: Value]
    while StartIndex < len(Lines) and (
        (Lines[StartIndex].startswith('[') and ']' in Lines[StartIndex]) or
        Lines[StartIndex].strip() == ''
    ):
        StartIndex += 1
    
    # Join remaining lines
    return '\n'.join(Lines[StartIndex:])

def ProcessJekyllIncompatibleContent(Content: str) -> str:
    """
    Process Jekyll-incompatible content.
    
    Handles:
    1. Jekyll Liquid template conflicts
    2. Triple curly braces
    3. Other Jekyll-specific issues
    
    Args:
        Content: Document content as string
    
    Returns:
        str: Processed document content
    """
    # Escape Jekyll Liquid templates
    Content = Content.replace('{% ', '{{ "{% " }}')
    Content = Content.replace('{{ ', '{{ "{{ " }}')
    Content = Content.replace(' }}', ' {{ "}}" }}')
    Content = Content.replace(' %}', ' {{ "%}" }}')
    
    # Handle triple curly braces used in some documents
    Content = Content.replace('{{{', '&#123;&#123;&#123;')
    Content = Content.replace('}}}', '&#125;&#125;&#125;')
    
    return Content

def ProcessSpecialSyntax(Content: str) -> str:
    """
    Process special syntax in the document.
    
    Handles:
    1. Tables
    2. Code blocks
    3. Special formatting
    
    Args:
        Content: Document content as string
    
    Returns:
        str: Processed document content
    """
    # Process code blocks with language specifiers
    CodeBlockPattern = r'```([a-zA-Z0-9_+-]+)\n(.*?)```'
    
    def CodeBlockReplacer(Match):
        Language = Match.group(1)
        Code = Match.group(2)
        return f'```{Language}\n{Code}```'
    
    Content = re.sub(CodeBlockPattern, CodeBlockReplacer, Content, flags=re.DOTALL)
    
    # Process task lists (GitHub-style)
    TaskListPattern = r'- \[ \] (.*?)$'
    Content = re.sub(TaskListPattern, r'- <input type="checkbox" disabled> \1', Content, flags=re.MULTILINE)
    
    TaskListCheckedPattern = r'- \[x\] (.*?)$'
    Content = re.sub(TaskListCheckedPattern, r'- <input type="checkbox" checked disabled> \1', Content, flags=re.MULTILINE)
    
    return Content

def ExtractCodeBlocks(Content: str) -> List[Dict[str, Any]]:
    """
    Extract code blocks from document content.
    
    Args:
        Content: Document content as string
    
    Returns:
        List[Dict[str, Any]]: List of dictionaries containing code block information
            Each dictionary has keys: 'language', 'code', 'start_line', 'end_line'
    """
    CodeBlocks = []
    
    # Match code blocks with language specifiers
    Pattern = r'```([a-zA-Z0-9_+-]+)\n(.*?)```'
    
    for Match in re.finditer(Pattern, Content, re.DOTALL):
        Language = Match.group(1)
        Code = Match.group(2)
        StartLine = Content[:Match.start()].count('\n')
        EndLine = StartLine + Code.count('\n') + 2  # +2 for the opening and closing marks
        
        CodeBlocks.append({
            'language': Language,
            'code': Code,
            'start_line': StartLine,
            'end_line': EndLine
        })
    
    return CodeBlocks

def ExtractTables(Content: str) -> List[Dict[str, Any]]:
    """
    Extract tables from document content.
    
    Args:
        Content: Document content as string
    
    Returns:
        List[Dict[str, Any]]: List of dictionaries containing table information
            Each dictionary has keys: 'header', 'rows', 'start_line', 'end_line'
    """
    Tables = []
    
    # Split content into lines
    Lines = Content.split('\n')
    
    # Find table markers
    TableStartLine = None
    
    for i, Line in enumerate(Lines):
        if Line.startswith('|') and Line.endswith('|'):
            if TableStartLine is None:
                TableStartLine = i
            
            # Check if the next line is a separator
            if i + 1 < len(Lines) and re.match(r'^\|[\s\-:]*\|$', Lines[i + 1]):
                # Found a table header
                HeaderRow = Line
                SeparatorRow = Lines[i + 1]
                
                # Find the end of the table
                TableEndLine = i + 1
                for j in range(i + 2, len(Lines)):
                    if Lines[j].startswith('|') and Lines[j].endswith('|'):
                        TableEndLine = j
                    else:
                        break
                
                # Extract table data
                Header = _ParseTableRow(HeaderRow)
                
                Rows = []
                for j in range(i + 2, TableEndLine + 1):
                    Row = _ParseTableRow(Lines[j])
                    if Row:
                        Rows.append(Row)
                
                Tables.append({
                    'header': Header,
                    'rows': Rows,
                    'start_line': TableStartLine,
                    'end_line': TableEndLine
                })
                
                # Reset for the next table
                TableStartLine = None
                i = TableEndLine + 1
    
    return Tables

def _ParseTableRow(Row: str) -> List[str]:
    """
    Parse a table row string into columns.
    
    Args:
        Row: Table row string with pipe separators
    
    Returns:
        List[str]: List of column values
    """
    # Remove leading and trailing pipes
    Row = Row.strip('|')
    
    # Split by pipes
    Columns = [Col.strip() for Col in Row.split('|')]
    
    return Columns