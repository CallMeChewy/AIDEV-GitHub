#!/usr/bin/env python3
# File: FileUtils.py
# Path: AIDEV-GitHub/Utils/FileUtils.py
# Standard: AIDEV-PascalCase-1.6
# Created: 2025-03-29
# Last Modified: 2025-03-29  10:30PM
# Description: File system utility functions for AIDEV-GitHub

import os
import shutil
from pathlib import Path
from typing import Union, Optional, BinaryIO, TextIO, List, Dict, Any

from Utils.LoggingManager import GetLogger

def EnsureDirectoryExists(DirPath: Union[str, Path]) -> Path:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        DirPath: Path to the directory
    
    Returns:
        Path: Path object for the directory
    
    Raises:
        PermissionError: If directory creation fails due to permissions
        OSError: If directory creation fails for other reasons
    """
    Logger = GetLogger("FileUtils")
    DirPathObj = Path(DirPath)
    
    try:
        DirPathObj.mkdir(parents=True, exist_ok=True)
        Logger.debug(f"Ensured directory exists: {DirPathObj}")
        return DirPathObj
    except Exception as Error:
        Logger.error(f"Failed to create directory {DirPathObj}: {str(Error)}")
        raise

def WriteTextFile(FilePath: Union[str, Path], Content: str, Encoding: str = 'utf-8') -> bool:
    """
    Write content to a text file.
    
    Args:
        FilePath: Path to the file
        Content: Content to write
        Encoding: File encoding (default: utf-8)
    
    Returns:
        bool: True if successful, False otherwise
    
    Raises:
        PermissionError: If file writing fails due to permissions
        OSError: If file writing fails for other reasons
    """
    Logger = GetLogger("FileUtils")
    FilePathObj = Path(FilePath)
    
    try:
        # Ensure parent directory exists
        EnsureDirectoryExists(FilePathObj.parent)
        
        # Write file
        with open(FilePathObj, 'w', encoding=Encoding) as File:
            File.write(Content)
            
        Logger.debug(f"Wrote text file: {FilePathObj}")
        return True
    except Exception as Error:
        Logger.error(f"Failed to write file {FilePathObj}: {str(Error)}")
        raise

def ReadTextFile(FilePath: Union[str, Path], Encoding: str = 'utf-8') -> str:
    """
    Read content from a text file.
    
    Args:
        FilePath: Path to the file
        Encoding: File encoding (default: utf-8)
    
    Returns:
        str: File content
    
    Raises:
        FileNotFoundError: If the file does not exist
        PermissionError: If file reading fails due to permissions
        UnicodeDecodeError: If file encoding is invalid
        OSError: If file reading fails for other reasons
    """
    Logger = GetLogger("FileUtils")
    FilePathObj = Path(FilePath)
    
    try:
        with open(FilePathObj, 'r', encoding=Encoding) as File:
            Content = File.read()
            
        Logger.debug(f"Read text file: {FilePathObj}")
        return Content
    except UnicodeDecodeError:
        # Try with different encodings if UTF-8 fails
        Logger.warning(f"UTF-8 decoding failed for {FilePathObj}, trying alternative encodings")
        try:
            with open(FilePathObj, 'r', encoding='latin-1') as File:
                Content = File.read()
            return Content
        except Exception as Error:
            Logger.error(f"Failed to read file {FilePathObj}: {str(Error)}")
            raise
    except Exception as Error:
        Logger.error(f"Failed to read file {FilePathObj}: {str(Error)}")
        raise

def CopyFile(SourcePath: Union[str, Path], DestPath: Union[str, Path]) -> bool:
    """
    Copy a file from source to destination.
    
    Args:
        SourcePath: Path to the source file
        DestPath: Path to the destination file
    
    Returns:
        bool: True if successful, False otherwise
    
    Raises:
        FileNotFoundError: If the source file does not exist
        PermissionError: If file copying fails due to permissions
        OSError: If file copying fails for other reasons
    """
    Logger = GetLogger("FileUtils")
    SourcePathObj = Path(SourcePath)
    DestPathObj = Path(DestPath)
    
    try:
        # Ensure parent directory exists
        EnsureDirectoryExists(DestPathObj.parent)
        
        # Copy file
        shutil.copy2(SourcePathObj, DestPathObj)
        
        Logger.debug(f"Copied file: {SourcePathObj} -> {DestPathObj}")
        return True
    except Exception as Error:
        Logger.error(f"Failed to copy file {SourcePathObj} to {DestPathObj}: {str(Error)}")
        raise

def ListFiles(DirPath: Union[str, Path], Pattern: str = "*", Recursive: bool = False) -> List[Path]:
    """
    List files in a directory matching a pattern.
    
    Args:
        DirPath: Path to the directory
        Pattern: Glob pattern for file matching (default: "*")
        Recursive: Whether to search recursively (default: False)
    
    Returns:
        List[Path]: List of matching file paths
    
    Raises:
        FileNotFoundError: If the directory does not exist
        PermissionError: If directory listing fails due to permissions
        OSError: If directory listing fails for other reasons
    """
    Logger = GetLogger("FileUtils")
    DirPathObj = Path(DirPath)
    
    try:
        if Recursive:
            Files = list(DirPathObj.glob(f"**/{Pattern}"))
        else:
            Files = list(DirPathObj.glob(Pattern))
            
        Logger.debug(f"Listed {len(Files)} files in {DirPathObj} with pattern '{Pattern}'")
        return [File for File in Files if File.is_file()]
    except Exception as Error:
        Logger.error(f"Failed to list files in {DirPathObj}: {str(Error)}")
        raise

def DeleteFile(FilePath: Union[str, Path]) -> bool:
    """
    Delete a file.
    
    Args:
        FilePath: Path to the file
    
    Returns:
        bool: True if successful, False otherwise
    
    Raises:
        FileNotFoundError: If the file does not exist
        PermissionError: If file deletion fails due to permissions
        OSError: If file deletion fails for other reasons
    """
    Logger = GetLogger("FileUtils")
    FilePathObj = Path(FilePath)
    
    try:
        FilePathObj.unlink()
        Logger.debug(f"Deleted file: {FilePathObj}")
        return True
    except Exception as Error:
        Logger.error(f"Failed to delete file {FilePathObj}: {str(Error)}")
        raise

def FileExists(FilePath: Union[str, Path]) -> bool:
    """
    Check if a file exists.
    
    Args:
        FilePath: Path to the file
    
    Returns:
        bool: True if the file exists, False otherwise
    """
    Logger = GetLogger("FileUtils")
    FilePathObj = Path(FilePath)
    
    Exists = FilePathObj.is_file()
    Logger.debug(f"File existence check: {FilePathObj} - {'Exists' if Exists else 'Does not exist'}")
    return Exists

def DirectoryExists(DirPath: Union[str, Path]) -> bool:
    """
    Check if a directory exists.
    
    Args:
        DirPath: Path to the directory
    
    Returns:
        bool: True if the directory exists, False otherwise
    """
    Logger = GetLogger("FileUtils")
    DirPathObj = Path(DirPath)
    
    Exists = DirPathObj.is_dir()
    Logger.debug(f"Directory existence check: {DirPathObj} - {'Exists' if Exists else 'Does not exist'}")
    return Exists

def GetFileSize(FilePath: Union[str, Path]) -> int:
    """
    Get the size of a file in bytes.
    
    Args:
        FilePath: Path to the file
    
    Returns:
        int: File size in bytes
    
    Raises:
        FileNotFoundError: If the file does not exist
        PermissionError: If file access fails due to permissions
        OSError: If file access fails for other reasons
    """
    Logger = GetLogger("FileUtils")
    FilePathObj = Path(FilePath)
    
    try:
        Size = FilePathObj.stat().st_size
        Logger.debug(f"File size: {FilePathObj} - {Size} bytes")
        return Size
    except Exception as Error:
        Logger.error(f"Failed to get file size for {FilePathObj}: {str(Error)}")
        raise

def WriteYamlFile(FilePath: Union[str, Path], Data: Dict[str, Any]) -> bool:
    """
    Write data to a YAML file.
    
    Args:
        FilePath: Path to the file
        Data: Data to write
    
    Returns:
        bool: True if successful, False otherwise
    
    Raises:
        ImportError: If PyYAML is not installed
        PermissionError: If file writing fails due to permissions
        OSError: If file writing fails for other reasons
    """
    Logger = GetLogger("FileUtils")
    
    try:
        import yaml
    except ImportError:
        Logger.error("PyYAML is not installed. Install with: pip install pyyaml")
        raise ImportError("PyYAML is required but not installed")
    
    try:
        Content = yaml.dump(Data, default_flow_style=False, sort_keys=False)
        return WriteTextFile(FilePath, Content)
    except Exception as Error:
        Logger.error(f"Failed to write YAML file {FilePath}: {str(Error)}")
        raise