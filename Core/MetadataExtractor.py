#!/usr/bin/env python3
# File: MetadataExtractor.py
# Path: AIDEV-GitHub/Core/MetadataExtractor.py
# Standard: AIDEV-PascalCase-1.6
# Created: 2025-03-29
# Last Modified: 2025-03-29  9:00PM
# Description: Module for extracting metadata from Project Himalaya documents

import re
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple

from Utils.LoggingManager import GetLogger

def ExtractMetadata(Content: str) -> Dict[str, Any]:
    """
    Extract metadata from document content.
    
    Extracts the following metadata:
    1. Title (from first heading)
    2. Creation date
    3. Last modification date
    4. Context attributes ([Key: Value] format)
    
    Args:
        Content: Document content as string
    
    Returns:
        Dict[str, Any]: Extracted metadata
    """
    Logger = GetLogger("MetadataExtractor")
    Metadata = {}
    
    # Process document header
    try:
        # Extract title (first heading)
        TitleMatch = re.search(r'^# (.+?)$', Content, re.MULTILINE)
        if TitleMatch:
            Metadata["title"] = TitleMatch.group(1).strip()
        
        # Extract creation date
        CreatedMatch = re.search(r'\*\*Created: (.+?)\*\*', Content)
        if CreatedMatch:
            Metadata["created_at"] = CreatedMatch.group(1).strip()
            
            # Try to parse date for sorting
            try:
                CreatedDate = ParseTimestamp(Metadata["created_at"])
                Metadata["created_date"] = CreatedDate.strftime("%Y-%m-%d")
            except:
                # If parsing fails, just use the string as is
                pass
        
        # Extract last modified date
        ModifiedMatch = re.search(r'\*\*Last Modified: (.+?)\*\*', Content)
        if ModifiedMatch:
            Metadata["modified_at"] = ModifiedMatch.group(1).strip()
            
            # Try to parse date for sorting
            try:
                ModifiedDate = ParseTimestamp(Metadata["modified_at"])
                Metadata["modified_date"] = ModifiedDate.strftime("%Y-%m-%d")
            except:
                # If parsing fails, just use the string as is
                pass
        
        # Extract context attributes [Key: Value]
        ContextPattern = r'\[([^:\]]+): ([^\]]+)\]'
        for Match in re.finditer(ContextPattern, Content):
            Key = Match.group(1).lower()
            Value = Match.group(2).strip()
            Metadata[Key] = Value
            
        # Extract document ID from filename or content
        DocIDMatch = re.search(r'(\d{2}-\d{2})', Content)
        if DocIDMatch:
            Metadata["doc_number"] = DocIDMatch.group(1)
    except Exception as Error:
        Logger.warning(f"Error extracting metadata: {str(Error)}")
    
    return Metadata

def ParseTimestamp(TimestampStr: str) -> datetime:
    """
    Parse a timestamp string from Project Himalaya document format.
    
    Supports formats:
    - "Month Day, Year Time AM/PM"
    - "YYYY-MM-DD HH:MM"
    
    Args:
        TimestampStr: Timestamp string to parse
    
    Returns:
        datetime: Parsed datetime object
    
    Raises:
        ValueError: If the timestamp string cannot be parsed
    """
    # Try different formats
    Formats = [
        "%B %d, %Y %I:%M %p",     # March 15, 2025 3:15 PM
        "%B %d, %Y  %I:%M%p",     # March 15, 2025  3:15PM (note double space)
        "%B %d, %Y  %I:%M %p",    # March 15, 2025  3:15 PM
        "%Y-%m-%d %H:%M",         # 2025-03-15 15:15
        "%Y-%m-%d"                # 2025-03-15
    ]
    
    for Format in Formats:
        try:
            return datetime.strptime(TimestampStr, Format)
        except ValueError:
            continue
    
    # If all formats fail, try a more flexible approach
    # This handles variations in spacing and punctuation
    Match = re.match(r'([A-Z][a-z]+)\s+(\d{1,2}),?\s+(\d{4})\s+(\d{1,2}):(\d{2})\s*([AP]M)?', TimestampStr)
    if Match:
        Month, Day, Year, Hour, Minute, AMPM = Match.groups()
        
        # Convert month name to number
        try:
            MonthNum = {
                'January': 1, 'February': 2, 'March': 3, 'April': 4,
                'May': 5, 'June': 6, 'July': 7, 'August': 8,
                'September': 9, 'October': 10, 'November': 11, 'December': 12
            }[Month]
        except KeyError:
            raise ValueError(f"Invalid month: {Month}")
        
        # Parse components
        try:
            Year = int(Year)
            Day = int(Day)
            Hour = int(Hour)
            Minute = int(Minute)
            
            # Handle AM/PM
            if AMPM and AMPM.upper() == 'PM' and Hour < 12:
                Hour += 12
            elif AMPM and AMPM.upper() == 'AM' and Hour == 12:
                Hour = 0
            
            return datetime(Year, MonthNum, Day, Hour, Minute)
        except (ValueError, TypeError) as Error:
            raise ValueError(f"Invalid timestamp components: {str(Error)}")
    
    raise ValueError(f"Could not parse timestamp: {TimestampStr}")

def ValidateMetadata(Metadata: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate metadata for completeness and correctness.
    
    Args:
        Metadata: Document metadata dictionary
    
    Returns:
        Tuple[bool, List[str]]: 
            bool: True if metadata is valid, False otherwise
            List[str]: List of validation error messages
    """
    Errors = []
    
    # Check required fields
    RequiredFields = ["title"]
    for Field in RequiredFields:
        if Field not in Metadata or not Metadata[Field]:
            Errors.append(f"Missing required metadata field: {Field}")
    
    # Validate dates if present
    for DateField in ["created_at", "modified_at"]:
        if DateField in Metadata and Metadata[DateField]:
            try:
                ParseTimestamp(Metadata[DateField])
            except ValueError as Error:
                Errors.append(f"Invalid {DateField} format: {str(Error)}")
    
    # Validate version format if present
    if "version" in Metadata and Metadata["version"]:
        VersionPattern = r'^\d+\.\d+$'  # X.Y format
        if not re.match(VersionPattern, Metadata["version"]):
            Errors.append(f"Invalid version format: {Metadata['version']} (should be X.Y)")
    
    return len(Errors) == 0, Errors

def EnrichMetadata(Metadata: Dict[str, Any], FilePath: Optional[str] = None) -> Dict[str, Any]:
    """
    Enrich metadata with additional information.
    
    Args:
        Metadata: Document metadata dictionary
        FilePath: Optional file path to extract additional information
    
    Returns:
        Dict[str, Any]: Enriched metadata
    """
    EnrichedMetadata = Metadata.copy()
    
    # Add current processing timestamp
    EnrichedMetadata["processed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Add file information if available
    if FilePath:
        import os
        EnrichedMetadata["file_path"] = FilePath
        EnrichedMetadata["file_name"] = os.path.basename(FilePath)
        EnrichedMetadata["file_directory"] = os.path.dirname(FilePath)
        
        # Try to get file stats
        try:
            Stats = os.stat(FilePath)
            EnrichedMetadata["file_size"] = Stats.st_size
            EnrichedMetadata["file_modified"] = datetime.fromtimestamp(Stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        except:
            pass
    
    # Generate excerpt if content is available
    if "content" in EnrichedMetadata:
        Content = EnrichedMetadata["content"]
        EnrichedMetadata["excerpt"] = GenerateExcerpt(Content)
    
    return EnrichedMetadata

def GenerateExcerpt(Content: str, MaxLength: int = 200) -> str:
    """
    Generate an excerpt from document content.
    
    Args:
        Content: Document content
        MaxLength: Maximum length of excerpt in characters
    
    Returns:
        str: Document excerpt
    """
    # Remove metadata header
    Lines = Content.split('\n')
    StartLine = 0
    
    # Skip title
    if Lines and Lines[0].startswith('# '):
        StartLine += 1
    
    # Skip metadata
    while StartLine < len(Lines) and (
        Lines[StartLine].startswith('**') or 
        Lines[StartLine].startswith('[') or
        not Lines[StartLine].strip()
    ):
        StartLine += 1
    
    # Get content after metadata
    ContentText = '\n'.join(Lines[StartLine:])
    
    # Remove Markdown formatting
    ContentText = re.sub(r'[#*`_\[\]()]', '', ContentText)
    
    # Normalize whitespace
    ContentText = re.sub(r'\s+', ' ', ContentText).strip()
    
    # Truncate to max length
    if len(ContentText) <= MaxLength:
        return ContentText
    
    # Try to break at the end of a sentence
    Excerpt = ContentText[:MaxLength]
    SentenceBreak = Excerpt.rfind('.')
    
    if SentenceBreak > MaxLength * 0.7:  # If we found a good break point
        return Excerpt[:SentenceBreak + 1]
    
    # Otherwise break at a word boundary
    WordBreak = Excerpt.rfind(' ')
    if WordBreak > 0:
        return Excerpt[:WordBreak] + '...'
    
    # Last resort: just truncate
    return Excerpt + '...'

def ExtractRelatedDocuments(Content: str) -> List[str]:
    """
    Extract references to related documents from content.
    
    Args:
        Content: Document content
    
    Returns:
        List[str]: List of document IDs referenced in the content
    """
    RelatedDocs = []
    
    # Match document references in format [XX-XX]
    Pattern = r'\[(\d{2}-\d{2})\]'
    
    for Match in re.finditer(Pattern, Content):
        DocID = Match.group(1)
        if DocID not in RelatedDocs:
            RelatedDocs.append(DocID)
    
    # Match section references in format [XX-XX §X.X]
    SectionPattern = r'\[(\d{2}-\d{2}) §\d+\.\d+\]'
    
    for Match in re.finditer(SectionPattern, Content):
        DocID = Match.group(1)
        if DocID not in RelatedDocs:
            RelatedDocs.append(DocID)
    
    return RelatedDocs