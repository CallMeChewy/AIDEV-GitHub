#!/usr/bin/env python3
# File: PathManager.py
# Path: AIDEV-GitHub/Utils/PathManager.py
# Standard: AIDEV-PascalCase-1.6
# Created: 2025-03-29
# Last Modified: 2025-03-29  11:00PM
# Description: Path management utility functions for AIDEV-GitHub

import os
import re
from pathlib import Path
from typing import Dict, Union, Optional, List

from Utils.LoggingManager import GetLogger

def GetDocumentID(Filename: str) -> str:
    """
    Extract document ID from filename.
    
    Supports formats:
    - XX-XX-DocumentName.md
    - XX-XX DocumentName.md
    - DocumentName-XX-XX.md
    
    Args:
        Filename: Document filename
    
    Returns:
        str: Document ID (e.g., "10-20") or empty string if not found
    """
    Logger = GetLogger("PathManager")
    
    # Try different patterns
    Patterns = [
        r'^(\d{2}-\d{2})[- _]',  # XX-XX-DocumentName or XX-XX DocumentName
        r'^(\d{2}-\d{2})\.md$',  # XX-XX.md
        r'-(\d{2}-\d{2})\.md$'   # DocumentName-XX-XX.md
    ]
    
    for Pattern in Patterns:
        Match = re.search(Pattern, Filename)
        if Match:
            DocID = Match.group(1)
            Logger.debug(f"Extracted document ID {DocID} from filename {Filename}")
            return DocID
    
    Logger.debug(f"No document ID found in filename {Filename}")
    return ""

def GetCategory(DocID: str, CategoryMappings: Dict[str, str]) -> str:
    """
    Determine document category from document ID.
    
    Args:
        DocID: Document ID (e.g., "10-20")
        CategoryMappings: Dictionary mapping category prefixes to category names
    
    Returns:
        str: Category name or empty string if not determined
    """
    Logger = GetLogger("PathManager")
    
    if not DocID:
        Logger.debug("Empty document ID provided")
        return ""
    
    # Extract prefix (first two digits)
    Prefix = DocID.split('-')[0] if '-' in DocID else DocID[:2]
    
    if Prefix in CategoryMappings:
        CategoryName = CategoryMappings[Prefix]
        Logger.debug(f"Determined category {CategoryName} for document ID {DocID}")
        return CategoryName
    
    Logger.debug(f"No category mapping found for document ID {DocID}")
    return ""

def GenerateOutputPath(RelativePath: Path, Category: str, OutputDir: Path) -> Path:
    """
    Generate output path for processed document.
    
    Args:
        RelativePath: Relative path from input directory
        Category: Document category
        OutputDir: Base output directory
    
    Returns:
        Path: Generated output path
    """
    Logger = GetLogger("PathManager")
    
    # Get document ID from filename
    DocID = GetDocumentID(RelativePath.name)
    
    if Category and DocID:
        # Use category-based path
        OutputPath = OutputDir / "docs" / Category / f"{DocID}.md"
    else:
        # Preserve original path structure
        OutputPath = OutputDir / "docs" / RelativePath.with_suffix('.md')
    
    Logger.debug(f"Generated output path: {OutputPath}")
    return OutputPath

def NormalizePath(Path: Union[str, Path]) -> Path:
    """
    Normalize a file path.
    
    Args:
        Path: Path to normalize
    
    Returns:
        Path: Normalized path
    """
    Logger = GetLogger("PathManager")
    
    NormalizedPath = Path(Path).expanduser().resolve()
    Logger.debug(f"Normalized path: {Path} -> {NormalizedPath}")
    return NormalizedPath

def IsInDirectory(FilePath: Union[str, Path], DirectoryPath: Union[str, Path]) -> bool:
    """
    Check if a file is in a directory (or its subdirectories).
    
    Args:
        FilePath: Path to the file
        DirectoryPath: Path to the directory
    
    Returns:
        bool: True if the file is in the directory, False otherwise
    """
    Logger = GetLogger("PathManager")
    
    FilePath = NormalizePath(FilePath)
    DirectoryPath = NormalizePath(DirectoryPath)
    
    try:
        # Use relative_to to check if FilePath is inside DirectoryPath
        FilePath.relative_to(DirectoryPath)
        Logger.debug(f"File {FilePath} is in directory {DirectoryPath}")
        return True
    except ValueError:
        Logger.debug(f"File {FilePath} is not in directory {DirectoryPath}")
        return False

def GetRelativePath(Path: Union[str, Path], BasePath: Union[str, Path]) -> Optional[Path]:
    """
    Get the relative path from base path.
    
    Args:
        Path: Path to get relative path for
        BasePath: Base path
    
    Returns:
        Optional[Path]: Relative path, or None if Path is not in BasePath
    """
    Logger = GetLogger("PathManager")
    
    Path = NormalizePath(Path)
    BasePath = NormalizePath(BasePath)
    
    try:
        RelPath = Path.relative_to(BasePath)
        Logger.debug(f"Relative path: {Path} -> {RelPath} (from {BasePath})")
        return RelPath
    except ValueError:
        Logger.debug(f"Path {Path} is not relative to {BasePath}")
        return None

def GetCommonBase(Paths: List[Union[str, Path]]) -> Optional[Path]:
    """
    Get the common base path for a list of paths.
    
    Args:
        Paths: List of paths
    
    Returns:
        Optional[Path]: Common base path, or None if no common base
    """
    Logger = GetLogger("PathManager")
    
    if not Paths:
        Logger.debug("Empty paths list provided")
        return None
    
    # Normalize all paths
    NormalizedPaths = [NormalizePath(Path) for Path in Paths]
    
    # Find the common parts
    Parts = [Path.parts for Path in NormalizedPaths]
    CommonParts = []
    
    for i in range(min(len(p) for p in Parts)):
        if all(p[i] == Parts[0][i] for p in Parts):
            CommonParts.append(Parts[0][i])
        else:
            break
    
    if not CommonParts:
        Logger.debug("No common base path found")
        return None
    
    CommonBase = Path(*CommonParts)
    Logger.debug(f"Common base path: {CommonBase}")
    return CommonBase

def IsAbsolutePath(Path: Union[str, Path]) -> bool:
    """
    Check if a path is absolute.
    
    Args:
        Path: Path to check
    
    Returns:
        bool: True if the path is absolute, False otherwise
    """
    Logger = GetLogger("PathManager")
    
    IsAbsolute = Path(Path).is_absolute()
    Logger.debug(f"Path {Path} is {'absolute' if IsAbsolute else 'relative'}")
    return IsAbsolute

def JoinPaths(*Paths: Union[str, Path]) -> Path:
    """
    Join multiple path components.
    
    Args:
        *Paths: Path components to join
    
    Returns:
        Path: Joined path
    """
    Logger = GetLogger("PathManager")
    
    JoinedPath = Path(Paths[0])
    for PathComponent in Paths[1:]:
        JoinedPath = JoinedPath / PathComponent
    
    Logger.debug(f"Joined paths: {JoinedPath}")
    return JoinedPath

def GetParentPath(Path: Union[str, Path], Levels: int = 1) -> Path:
    """
    Get the parent path, optionally multiple levels up.
    
    Args:
        Path: Path to get parent for
        Levels: Number of parent levels to go up (default: 1)
    
    Returns:
        Path: Parent path
    """
    Logger = GetLogger("PathManager")
    
    Result = Path(Path)
    for _ in range(Levels):
        Result = Result.parent
    
    Logger.debug(f"Parent path ({Levels} levels up): {Path} -> {Result}")
    return Result