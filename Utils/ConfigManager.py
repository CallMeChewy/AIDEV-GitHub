#!/usr/bin/env python3
# File: ConfigManager.py
# Path: AIDEV-GitHub/Utils/ConfigManager.py
# Standard: AIDEV-PascalCase-1.6
# Created: 2025-03-29
# Last Modified: 2025-03-29  11:30PM
# Description: Configuration management utility for AIDEV-GitHub

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Union, Optional, List

from Utils.LoggingManager import GetLogger

DEFAULT_CONFIG = {
    "categories": {
        "00": "navigation",
        "10": "vision",
        "20": "standards",
        "30": "templates",
        "40": "knowledge",
        "50": "implementation",
        "60": "testing",
        "70": "documentation",
        "80": "archives",
        "90": "references"
    },
    "templates": {
        "use_custom": False,
        "custom_path": None
    },
    "search": {
        "enabled": True,
        "include_content": True
    },
    "github": {
        "repository": "CallMeChewy/ProjectHimalaya",
        "branch": "gh-pages",
        "create_branch": True
    },
    "paths": {
        "base_url": "/ProjectHimalaya",
        "output_dir": "docs"
    },
    "jekyll": {
        "title": "Project Himalaya",
        "description": "A comprehensive framework for AI-human collaborative development",
        "theme": "default"
    }
}

def LoadConfiguration(ConfigPath: Union[str, Path]) -> Dict[str, Any]:
    """
    Load configuration from a file.
    
    Supports JSON and YAML formats.
    
    Args:
        ConfigPath: Path to the configuration file
    
    Returns:
        Dict[str, Any]: Configuration dictionary
    
    Raises:
        FileNotFoundError: If the configuration file does not exist
        ValueError: If the configuration file has an invalid format
    """
    Logger = GetLogger("ConfigManager")
    ConfigPathObj = Path(ConfigPath)
    
    if not ConfigPathObj.exists():
        Logger.error(f"Configuration file does not exist: {ConfigPathObj}")
        raise FileNotFoundError(f"Configuration file not found: {ConfigPathObj}")
    
    try:
        Suffix = ConfigPathObj.suffix.lower()
        
        if Suffix == '.json':
            with open(ConfigPathObj, 'r', encoding='utf-8') as File:
                Config = json.load(File)
        elif Suffix in ['.yml', '.yaml']:
            with open(ConfigPathObj, 'r', encoding='utf-8') as File:
                Config = yaml.safe_load(File)
        else:
            Logger.error(f"Unsupported configuration file format: {Suffix}")
            raise ValueError(f"Unsupported configuration file format: {Suffix}")
        
        # Merge with default config
        MergedConfig = MergeConfigs(DEFAULT_CONFIG, Config)
        
        Logger.info(f"Loaded configuration from {ConfigPathObj}")
        return MergedConfig
    
    except Exception as Error:
        Logger.error(f"Failed to load configuration from {ConfigPathObj}: {str(Error)}")
        raise

def SaveConfiguration(Config: Dict[str, Any], ConfigPath: Union[str, Path]) -> bool:
    """
    Save configuration to a file.
    
    Format is determined by file extension.
    
    Args:
        Config: Configuration dictionary
        ConfigPath: Path to the configuration file
    
    Returns:
        bool: True if successful, False otherwise
    
    Raises:
        ValueError: If the configuration file has an invalid format
    """
    Logger = GetLogger("ConfigManager")
    ConfigPathObj = Path(ConfigPath)
    
    try:
        # Create parent directory if it doesn't exist
        ConfigPathObj.parent.mkdir(parents=True, exist_ok=True)
        
        Suffix = ConfigPathObj.suffix.lower()
        
        if Suffix == '.json':
            with open(ConfigPathObj, 'w', encoding='utf-8') as File:
                json.dump(Config, File, indent=2)
        elif Suffix in ['.yml', '.yaml']:
            with open(ConfigPathObj, 'w', encoding='utf-8') as File:
                yaml.dump(Config, File, default_flow_style=False, sort_keys=False)
        else:
            Logger.error(f"Unsupported configuration file format: {Suffix}")
            raise ValueError(f"Unsupported configuration file format: {Suffix}")
        
        Logger.info(f"Saved configuration to {ConfigPathObj}")
        return True
    
    except Exception as Error:
        Logger.error(f"Failed to save configuration to {ConfigPathObj}: {str(Error)}")
        raise

def GetDefaultConfig() -> Dict[str, Any]:
    """
    Get the default configuration.
    
    Returns:
        Dict[str, Any]: Default configuration dictionary
    """
    return DEFAULT_CONFIG.copy()

def MergeConfigs(Base: Dict[str, Any], Override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two configuration dictionaries.
    
    Values in Override take precedence over values in Base.
    
    Args:
        Base: Base configuration dictionary
        Override: Override configuration dictionary
    
    Returns:
        Dict[str, Any]: Merged configuration dictionary
    """
    Result = Base.copy()
    
    for Key, Value in Override.items():
        if Key in Result and isinstance(Result[Key], dict) and isinstance(Value, dict):
            Result[Key] = MergeConfigs(Result[Key], Value)
        else:
            Result[Key] = Value
    
    return Result

def ValidateConfiguration(Config: Dict[str, Any]) -> List[str]:
    """
    Validate configuration.
    
    Args:
        Config: Configuration dictionary
    
    Returns:
        List[str]: List of validation error messages
    """
    Logger = GetLogger("ConfigManager")
    Errors = []
    
    # Check required fields
    RequiredFields = ["categories", "paths"]
    for Field in RequiredFields:
        if Field not in Config:
            Errors.append(f"Missing required configuration field: {Field}")
    
    # Check paths
    if "paths" in Config:
        PathsConfig = Config["paths"]
        
        if "base_url" not in PathsConfig:
            Errors.append("Missing required configuration field: paths.base_url")
        
        if "output_dir" not in PathsConfig:
            Errors.append("Missing required configuration field: paths.output_dir")
    
    # Check categories
    if "categories" in Config:
        CategoriesConfig = Config["categories"]
        
        if not isinstance(CategoriesConfig, dict):
            Errors.append("Categories configuration must be a dictionary")
        elif not CategoriesConfig:
            Errors.append("Categories configuration cannot be empty")
    
    # Check GitHub configuration
    if "github" in Config:
        GitHubConfig = Config["github"]
        
        if "repository" in GitHubConfig and not isinstance(GitHubConfig["repository"], str):
            Errors.append("GitHub repository must be a string")
        
        if "branch" in GitHubConfig and not isinstance(GitHubConfig["branch"], str):
            Errors.append("GitHub branch must be a string")
    
    # Check Jekyll configuration
    if "jekyll" in Config:
        JekyllConfig = Config["jekyll"]
        
        if "title" in JekyllConfig and not isinstance(JekyllConfig["title"], str):
            Errors.append("Jekyll title must be a string")
        
        if "description" in JekyllConfig and not isinstance(JekyllConfig["description"], str):
            Errors.append("Jekyll description must be a string")
    
    if Errors:
        Logger.warning(f"Configuration validation failed with {len(Errors)} errors")
        for Error in Errors:
            Logger.warning(f"  - {Error}")
    else:
        Logger.info("Configuration validation successful")
    
    return Errors

def GetConfigValue(Config: Dict[str, Any], Path: str, Default: Any = None) -> Any:
    """
    Get a value from the configuration by path.
    
    Path is a dot-separated string, e.g., "paths.base_url".
    
    Args:
        Config: Configuration dictionary
        Path: Path to the value
        Default: Default value if not found
    
    Returns:
        Any: The value or the default if not found
    """
    Logger = GetLogger("ConfigManager")
    
    try:
        Parts = Path.split('.')
        Value = Config
        
        for Part in Parts:
            if not isinstance(Value, dict) or Part not in Value:
                Logger.debug(f"Configuration path not found: {Path}")
                return Default
            
            Value = Value[Part]
        
        Logger.debug(f"Configuration value for {Path}: {Value}")
        return Value
    except Exception as Error:
        Logger.error(f"Error getting configuration value for {Path}: {str(Error)}")
        return Default

def SetConfigValue(Config: Dict[str, Any], Path: str, Value: Any) -> Dict[str, Any]:
    """
    Set a value in the configuration by path.
    
    Path is a dot-separated string, e.g., "paths.base_url".
    
    Args:
        Config: Configuration dictionary
        Path: Path to the value
        Value: Value to set
    
    Returns:
        Dict[str, Any]: Updated configuration dictionary
    """
    Logger = GetLogger("ConfigManager")
    
    try:
        Parts = Path.split('.')
        Target = Config
        
        # Navigate to the parent of the target key
        for Part in Parts[:-1]:
            if Part not in Target:
                Target[Part] = {}
            
            Target = Target[Part]
        
        # Set the value
        Target[Parts[-1]] = Value
        
        Logger.debug(f"Set configuration value for {Path}: {Value}")
        return Config
    except Exception as Error:
        Logger.error(f"Error setting configuration value for {Path}: {str(Error)}")
        return Config