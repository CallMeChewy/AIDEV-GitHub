#!/usr/bin/env python3
# File: CommandLineInterface.py
# Path: AIDEV-GitHub/CLI/CommandLineInterface.py
# Standard: AIDEV-PascalCase-1.6
# Created: 2025-03-30
# Last Modified: 2025-03-30  12:30AM
# Description: Command line interface for AIDEV-GitHub

import os
import sys
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import AIDEV-GitHub components
from Core.ConverterCore import ConvertDocuments
from Utils.ConfigManager import LoadConfiguration, SaveConfiguration, GetDefaultConfig, ValidateConfiguration
from Utils.LoggingManager import SetupLogging, EnableFileLogging, GetLogger

def ParseArguments() -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    Parser = argparse.ArgumentParser(
        description="AIDEV-GitHub: Convert Project Himalaya documentation to GitHub Pages",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Main arguments
    Parser.add_argument(
        "input_dir",
        help="Source directory containing Project Himalaya documents"
    )
    
    Parser.add_argument(
        "output_dir",
        help="Target directory for Jekyll-compatible GitHub Pages site"
    )
    
    # Optional arguments
    Parser.add_argument(
        "--base-url",
        default="/ProjectHimalaya",
        help="Base URL path for the GitHub Pages site"
    )
    
    Parser.add_argument(
        "--config",
        help="Path to configuration file (JSON or YAML)"
    )
    
    # Logging options
    Parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set logging level"
    )
    
    Parser.add_argument(
        "--log-file",
        help="Log to the specified file"
    )
    
    # Action options
    SubParsers = Parser.add_subparsers(dest="action", help="Action to perform")
    
    # Generate config action
    ConfigParser = SubParsers.add_parser(
        "generate-config",
        help="Generate a configuration file with default settings"
    )
    
    ConfigParser.add_argument(
        "config_path",
        help="Path to save the configuration file"
    )
    
    # Deploy action
    DeployParser = SubParsers.add_parser(
        "deploy",
        help="Deploy the generated site to GitHub Pages"
    )
    
    DeployParser.add_argument(
        "--repository",
        help="GitHub repository name (e.g., username/repo)"
    )
    
    DeployParser.add_argument(
        "--branch",
        default="gh-pages",
        help="GitHub Pages branch name"
    )
    
    DeployParser.add_argument(
        "--token",
        help="GitHub personal access token"
    )
    
    return Parser.parse_args()

def SetupLoggingFromArgs(Args: argparse.Namespace) -> None:
    """
    Set up logging from command line arguments.
    
    Args:
        Args: Parsed command line arguments
    """
    # Convert string level to int
    LogLevelMap = {
        "DEBUG": 10,
        "INFO": 20,
        "WARNING": 30,
        "ERROR": 40,
        "CRITICAL": 50
    }
    
    LogLevel = LogLevelMap.get(Args.log_level, 20)  # Default to INFO
    
    # Set up basic logging
    SetupLogging(Level=LogLevel)
    
    # Enable file logging if specified
    if Args.log_file:
        EnableFileLogging(LogFile=Args.log_file)

def GenerateDefaultConfig(ConfigPath: str) -> bool:
    """
    Generate a default configuration file.
    
    Args:
        ConfigPath: Path to save the configuration file
    
    Returns:
        bool: True if successful, False otherwise
    """
    Logger = GetLogger("CLI")
    
    try:
        # Get default configuration
        DefaultConfig = GetDefaultConfig()
        
        # Save configuration
        from Utils.FileUtils import WriteTextFile
        
        ConfigPathObj = Path(ConfigPath)
        Suffix = ConfigPathObj.suffix.lower()
        
        if Suffix == '.json':
            import json
            Content = json.dumps(DefaultConfig, indent=2)
        elif Suffix in ['.yml', '.yaml']:
            import yaml
            Content = yaml.dump(DefaultConfig, default_flow_style=False, sort_keys=False)
        else:
            Logger.error(f"Unsupported configuration file format: {Suffix}")
            return False
        
        WriteTextFile(ConfigPathObj, Content)
        
        Logger.info(f"Generated default configuration file: {ConfigPathObj}")
        return True
    
    except Exception as Error:
        Logger.error(f"Failed to generate configuration file: {str(Error)}")
        return False

def DeployToGitHubPages(
    OutputDir: str,
    Repository: Optional[str] = None,
    Branch: str = "gh-pages",
    Token: Optional[str] = None
) -> bool:
    """
    Deploy the site to GitHub Pages.
    
    Args:
        OutputDir: Directory containing the built site
        Repository: GitHub repository name (e.g., username/repo)
        Branch: Branch name for GitHub Pages
        Token: GitHub personal access token
    
    Returns:
        bool: True if successful, False otherwise
    """
    Logger = GetLogger("CLI")
    Logger.info("Deploying to GitHub Pages...")
    
    try:
        # Check if git is installed
        import subprocess
        
        try:
            subprocess.run(["git", "--version"], check=True, capture_output=True)
        except (subprocess.SubprocessError, FileNotFoundError):
            Logger.error("Git is not installed or not found in PATH")
            return False
        
        # Change to output directory
        OriginalDir = os.getcwd()
        os.chdir(OutputDir)
        
        try:
            # Initialize git repository if not already
            if not os.path.isdir(".git"):
                subprocess.run(["git", "init"], check=True, capture_output=True)
            
            # Configure repository if specified
            if Repository:
                GitHubUrl = f"https://github.com/{Repository}.git"
                
                if Token:
                    # Use token for authentication
                    TokenUrl = f"https://{Token}@github.com/{Repository}.git"
                    subprocess.run(["git", "remote", "remove", "origin"], capture_output=True)
                    subprocess.run(["git", "remote", "add", "origin", TokenUrl], check=True, capture_output=True)
                else:
                    # Use standard URL
                    subprocess.run(["git", "remote", "remove", "origin"], capture_output=True)
                    subprocess.run(["git", "remote", "add", "origin", GitHubUrl], check=True, capture_output=True)
            
            # Create necessary files for GitHub Pages
            # Create .nojekyll to bypass GitHub Pages Jekyll processing
            with open(".nojekyll", "w") as File:
                pass
            
            # Add all files
            subprocess.run(["git", "add", "."], check=True, capture_output=True)
            
            # Commit
            subprocess.run(
                ["git", "commit", "-m", "Deploy to GitHub Pages"],
                check=True,
                capture_output=True
            )
            
            # Create or switch to branch
            try:
                subprocess.run(
                    ["git", "branch", "-M", Branch],
                    check=True,
                    capture_output=True
                )
            except subprocess.CalledProcessError:
                subprocess.run(
                    ["git", "checkout", "-b", Branch],
                    check=True,
                    capture_output=True
                )
            
            # Push to GitHub
            PushCommand = ["git", "push", "-f", "origin", Branch]
            PushResult = subprocess.run(PushCommand, capture_output=True)
            
            if PushResult.returncode != 0:
                Logger.error(f"Failed to push to GitHub: {PushResult.stderr.decode()}")
                return False
            
            Logger.info(f"Successfully deployed to GitHub Pages (branch: {Branch})")
            return True
        
        finally:
            # Return to original directory
            os.chdir(OriginalDir)
    
    except Exception as Error:
        Logger.error(f"Failed to deploy to GitHub Pages: {str(Error)}")
        return False

def Main() -> int:
    """
    Main function.
    
    Returns:
        int: Exit code (0 for success, non-zero for failure)
    """
    # Parse arguments
    Args = ParseArguments()
    
    # Set up logging
    SetupLoggingFromArgs(Args)
    Logger = GetLogger("CLI")
    
    # Generate config action
    if Args.action == "generate-config":
        Success = GenerateDefaultConfig(Args.config_path)
        return 0 if Success else 1
    
    # Deploy action
    if Args.action == "deploy":
        Success = DeployToGitHubPages(
            OutputDir=Args.output_dir,
            Repository=Args.repository,
            Branch=Args.branch,
            Token=Args.token
        )
        return 0 if Success else 1
    
    # Default action: convert documents
    try:
        Logger.info(f"Converting documents from {Args.input_dir} to {Args.output_dir}")
        
        # Convert documents
        Success = ConvertDocuments(
            InputDir=Args.input_dir,
            OutputDir=Args.output_dir,
            BaseURL=Args.base_url,
            ConfigPath=Args.config
        )
        
        if Success:
            Logger.info("Conversion completed successfully")
            return 0
        else:
            Logger.error("Conversion failed")
            return 1
    
    except Exception as Error:
        Logger.exception(f"Conversion failed: {str(Error)}")
        return 1

if __name__ == "__main__":
    sys.exit(Main())