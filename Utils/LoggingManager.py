#!/usr/bin/env python3
# File: LoggingManager.py
# Path: AIDEV-GitHub/Utils/LoggingManager.py
# Standard: AIDEV-PascalCase-1.6
# Created: 2025-03-30
# Last Modified: 2025-03-30  12:00AM
# Description: Logging utility for AIDEV-GitHub

import os
import sys
import logging
from pathlib import Path
from typing import Optional, Dict, Any, Union

# Global logger dictionary
_LOGGERS = {}

# Global logging configuration
_LOGGING_CONFIG = {
    "level": logging.INFO,
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "date_format": "%Y-%m-%d %H:%M:%S",
    "log_to_file": False,
    "log_file": "aidev-github.log",
    "log_dir": "logs",
    "console_level": logging.INFO,
    "file_level": logging.DEBUG
}

def SetupLogging(
    Level: int = None,
    Format: str = None,
    DateFormat: str = None,
    LogToFile: bool = None,
    LogFile: str = None,
    LogDir: str = None,
    ConsoleLevel: int = None,
    FileLevel: int = None
) -> None:
    """
    Set up logging configuration.
    
    Args:
        Level: Global logging level
        Format: Log message format
        DateFormat: Date format in log messages
        LogToFile: Whether to log to a file
        LogFile: Name of the log file
        LogDir: Directory for log files
        ConsoleLevel: Logging level for console output
        FileLevel: Logging level for file output
    """
    global _LOGGING_CONFIG
    
    # Update configuration with provided values
    if Level is not None:
        _LOGGING_CONFIG["level"] = Level
    
    if Format is not None:
        _LOGGING_CONFIG["format"] = Format
    
    if DateFormat is not None:
        _LOGGING_CONFIG["date_format"] = DateFormat
    
    if LogToFile is not None:
        _LOGGING_CONFIG["log_to_file"] = LogToFile
    
    if LogFile is not None:
        _LOGGING_CONFIG["log_file"] = LogFile
    
    if LogDir is not None:
        _LOGGING_CONFIG["log_dir"] = LogDir
    
    if ConsoleLevel is not None:
        _LOGGING_CONFIG["console_level"] = ConsoleLevel
    
    if FileLevel is not None:
        _LOGGING_CONFIG["file_level"] = FileLevel
    
    # Set up root logger
    RootLogger = logging.getLogger()
    RootLogger.setLevel(_LOGGING_CONFIG["level"])
    
    # Remove existing handlers
    for Handler in RootLogger.handlers[:]:
        RootLogger.removeHandler(Handler)
    
    # Create formatters
    Formatter = logging.Formatter(
        fmt=_LOGGING_CONFIG["format"],
        datefmt=_LOGGING_CONFIG["date_format"]
    )
    
    # Add console handler
    ConsoleHandler = logging.StreamHandler(sys.stdout)
    ConsoleHandler.setLevel(_LOGGING_CONFIG["console_level"])
    ConsoleHandler.setFormatter(Formatter)
    RootLogger.addHandler(ConsoleHandler)
    
    # Add file handler if enabled
    if _LOGGING_CONFIG["log_to_file"]:
        LogDirPath = Path(_LOGGING_CONFIG["log_dir"])
        LogDirPath.mkdir(parents=True, exist_ok=True)
        
        LogFilePath = LogDirPath / _LOGGING_CONFIG["log_file"]
        FileHandler = logging.FileHandler(LogFilePath, encoding="utf-8")
        FileHandler.setLevel(_LOGGING_CONFIG["file_level"])
        FileHandler.setFormatter(Formatter)
        RootLogger.addHandler(FileHandler)

def GetLogger(Name: str) -> logging.Logger:
    """
    Get a logger with the given name.
    
    Creates a new logger if one with the given name doesn't exist.
    
    Args:
        Name: Logger name
    
    Returns:
        logging.Logger: Logger instance
    """
    global _LOGGERS
    
    if Name not in _LOGGERS:
        Logger = logging.getLogger(Name)
        Logger.setLevel(_LOGGING_CONFIG["level"])
        _LOGGERS[Name] = Logger
    
    return _LOGGERS[Name]

def SetLoggingLevel(Level: int, LoggerName: Optional[str] = None) -> None:
    """
    Set the logging level for a specific logger or all loggers.
    
    Args:
        Level: Logging level (e.g., logging.DEBUG, logging.INFO)
        LoggerName: Name of the logger to set level for, or None for all loggers
    """
    global _LOGGERS, _LOGGING_CONFIG
    
    if LoggerName is None:
        # Set level for all loggers
        _LOGGING_CONFIG["level"] = Level
        
        for Logger in _LOGGERS.values():
            Logger.setLevel(Level)
    else:
        # Set level for specific logger
        if LoggerName in _LOGGERS:
            _LOGGERS[LoggerName].setLevel(Level)

def EnableFileLogging(
    LogFile: Optional[str] = None,
    LogDir: Optional[str] = None,
    FileLevel: Optional[int] = None
) -> None:
    """
    Enable logging to a file.
    
    Args:
        LogFile: Name of the log file
        LogDir: Directory for log files
        FileLevel: Logging level for file output
    """
    global _LOGGING_CONFIG
    
    # Update configuration
    _LOGGING_CONFIG["log_to_file"] = True
    
    if LogFile is not None:
        _LOGGING_CONFIG["log_file"] = LogFile
    
    if LogDir is not None:
        _LOGGING_CONFIG["log_dir"] = LogDir
    
    if FileLevel is not None:
        _LOGGING_CONFIG["file_level"] = FileLevel
    
    # Create log directory
    LogDirPath = Path(_LOGGING_CONFIG["log_dir"])
    LogDirPath.mkdir(parents=True, exist_ok=True)
    
    # Create file handler
    LogFilePath = LogDirPath / _LOGGING_CONFIG["log_file"]
    
    # Add file handler to all loggers
    Formatter = logging.Formatter(
        fmt=_LOGGING_CONFIG["format"],
        datefmt=_LOGGING_CONFIG["date_format"]
    )
    
    FileHandler = logging.FileHandler(LogFilePath, encoding="utf-8")
    FileHandler.setLevel(_LOGGING_CONFIG["file_level"])
    FileHandler.setFormatter(Formatter)
    
    # Add to root logger
    RootLogger = logging.getLogger()
    
    # Remove existing file handlers
    for Handler in RootLogger.handlers[:]:
        if isinstance(Handler, logging.FileHandler):
            RootLogger.removeHandler(Handler)
    
    RootLogger.addHandler(FileHandler)

def DisableFileLogging() -> None:
    """Disable logging to a file."""
    global _LOGGING_CONFIG
    
    _LOGGING_CONFIG["log_to_file"] = False
    
    # Remove file handlers from all loggers
    RootLogger = logging.getLogger()
    
    for Handler in RootLogger.handlers[:]:
        if isinstance(Handler, logging.FileHandler):
            RootLogger.removeHandler(Handler)

def LogException(Exception: Exception, LoggerName: Optional[str] = None) -> None:
    """
    Log an exception with traceback.
    
    Args:
        Exception: Exception to log
        LoggerName: Name of the logger to use, or None for the root logger
    """
    Logger = GetLogger(LoggerName or "root")
    Logger.exception(f"Exception: {str(Exception)}")

def LogText(Text: str, Level: int = logging.INFO, LoggerName: Optional[str] = None) -> None:
    """
    Log a text message.
    
    Args:
        Text: Text to log
        Level: Logging level
        LoggerName: Name of the logger to use, or None for the root logger
    """
    Logger = GetLogger(LoggerName or "root")
    Logger.log(Level, Text)

def GetLoggingConfig() -> Dict[str, Any]:
    """
    Get the current logging configuration.
    
    Returns:
        Dict[str, Any]: Logging configuration dictionary
    """
    global _LOGGING_CONFIG
    return _LOGGING_CONFIG.copy()