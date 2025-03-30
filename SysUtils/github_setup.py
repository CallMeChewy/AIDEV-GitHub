#!/usr/bin/env python3
# File: github_setup.py
# Path: AIDEV-WEB/scripts/github_setup.py
# Standard: AIDEV-PascalCase-1.6
# Created: 2025-03-28
# Last Modified: 2025-03-28  5:15PM
# Description: Set up GitHub repository for Project Himalaya
# Author: Claude (Anthropic), as part of Project Himalaya
# Human Collaboration: Herbert J. Bowers

"""
GitHub Repository Setup Script

This script automates the process of initializing a local Git repository,
adding the remote origin, and pushing the initial commit to GitHub.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import Optional, Tuple, List

class GitHubSetup:
    """Handles the setup and initialization of a GitHub repository."""
    
    def __init__(self, ProjectDir: Optional[str] = None, 
                 RepoName: str = "ProjectHimalaya",
                 Username: str = "CallMeChewy"):
        """Initialize the GitHub setup tool.
        
        Args:
            ProjectDir: Path to the project directory (default: current directory)
            RepoName: GitHub repository name (default: "ProjectHimalaya")
            Username: GitHub username (default: "CallMeChewy")
        """
        self.ProjectDir = Path(ProjectDir).resolve() if ProjectDir else Path.cwd().resolve()
        self.RepoName = RepoName
        self.Username = Username
        self.GitDir = self.ProjectDir / ".git"
        
        # Check if directory exists
        if not self.ProjectDir.exists():
            raise ValueError(f"Project directory {self.ProjectDir} does not exist")
            
    def RunCommand(self, Command: List[str], Cwd: Optional[Path] = None) -> Tuple[int, str, str]:
        """Run a shell command and return the output.
        
        Args:
            Command: Command to run as list of strings
            Cwd: Directory to run command in (default: ProjectDir)
            
        Returns:
            Tuple of (return code, stdout, stderr)
        """
        try:
            Process = subprocess.Popen(
                Command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(Cwd or self.ProjectDir)
            )
            Stdout, Stderr = Process.communicate()
            return Process.returncode, Stdout.decode('utf-8'), Stderr.decode('utf-8')
        except Exception as Ex:
            return 1, "", str(Ex)
    
    def IsGitRepository(self) -> bool:
        """Check if the directory is already a Git repository.
        
        Returns:
            True if directory is a Git repository, False otherwise
        """
        return self.GitDir.exists() and self.GitDir.is_dir()
    
    def InitializeRepository(self) -> bool:
        """Initialize a new Git repository.
        
        Returns:
            True if successful, False otherwise
        """
        print(f"Initializing Git repository in {self.ProjectDir}...")
        
        if self.IsGitRepository():
            print("  Directory is already a Git repository")
            return True
        
        ReturnCode, Stdout, Stderr = self.RunCommand(["git", "init"])
        
        if ReturnCode != 0:
            print(f"  Error initializing repository: {Stderr}")
            return False
        
        print("  Repository initialized successfully")
        return True
    
    def ConfigureGit(self, Name: Optional[str] = None, Email: Optional[str] = None) -> bool:
        """Configure Git user name and email if provided.
        
        Args:
            Name: Git user name
            Email: Git user email
            
        Returns:
            True if successful, False otherwise
        """
        if Name:
            ReturnCode, Stdout, Stderr = self.RunCommand(["git", "config", "user.name", Name])
            if ReturnCode != 0:
                print(f"  Error setting user name: {Stderr}")
                return False
            print(f"  Set Git user name to: {Name}")
        
        if Email:
            ReturnCode, Stdout, Stderr = self.RunCommand(["git", "config", "user.email", Email])
            if ReturnCode != 0:
                print(f"  Error setting user email: {Stderr}")
                return False
            print(f"  Set Git user email to: {Email}")
        
        return True
    
    def CreateGitignore(self) -> bool:
        """Create a .gitignore file if it doesn't exist.
        
        Returns:
            True if successful, False otherwise
        """
        GitignorePath = self.ProjectDir / ".gitignore"
        
        if GitignorePath.exists():
            print("  .gitignore file already exists")
            return True
        
        print("Creating .gitignore file...")
        
        try:
            with open(GitignorePath, 'w') as f:
                f.write("""# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
.env
.venv
env/
venv/
ENV/

# Jekyll
_site/
.sass-cache/
.jekyll-cache/
.jekyll-metadata
docs/.bundle/
docs/vendor/

# IDE and editors
.idea/
.vscode/
*.swp
*.swo
*~
.project
.classpath
.settings/

# OS specific
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Project specific
temp/
logs/
*.log
""")
            print("  .gitignore file created")
            return True
        except Exception as Ex:
            print(f"  Error creating .gitignore file: {str(Ex)}")
            return False
    
    def StageFiles(self) -> bool:
        """Stage all files for commit.
        
        Returns:
            True if successful, False otherwise
        """
        print("Staging files...")
        
        ReturnCode, Stdout, Stderr = self.RunCommand(["git", "add", "."])
        
        if ReturnCode != 0:
            print(f"  Error staging files: {Stderr}")
            return False
        
        print("  Files staged successfully")
        return True
    
    def CreateInitialCommit(self) -> bool:
        """Create initial commit.
        
        Returns:
            True if successful, False otherwise
        """
        print("Creating initial commit...")
        
        CommitMessage = "Initial commit for Project Himalaya"
        ReturnCode, Stdout, Stderr = self.RunCommand(["git", "commit", "-m", CommitMessage])
        
        if ReturnCode != 0:
            print(f"  Error creating commit: {Stderr}")
            return False
        
        print("  Initial commit created successfully")
        return True
    
    def SetupRemote(self) -> bool:
        """Set up remote origin for GitHub repository.
        
        Returns:
            True if successful, False otherwise
        """
        print("Setting up remote origin...")
        
        # Check if remote exists
        ReturnCode, Stdout, Stderr = self.RunCommand(["git", "remote"])
        
        RemoteUrl = f"git@github.com:{self.Username}/{self.RepoName}.git"
        
        if "origin" in Stdout:
            print("  Remote 'origin' already exists, updating URL")
            ReturnCode, Stdout, Stderr = self.RunCommand(["git", "remote", "set-url", "origin", RemoteUrl])
        else:
            ReturnCode, Stdout, Stderr = self.RunCommand(["git", "remote", "add", "origin", RemoteUrl])
        
        if ReturnCode != 0:
            print(f"  Error setting up remote: {Stderr}")
            return False
        
        print(f"  Remote origin set to: {RemoteUrl}")
        return True
    
    def PushToGitHub(self, Force: bool = False) -> bool:
        """Push to GitHub repository.
        
        Args:
            Force: Force push (overwrite remote history)
            
        Returns:
            True if successful, False otherwise
        """
        print("Pushing to GitHub...")
        
        Command = ["git", "push", "-u", "origin", "main"]
        if Force:
            Command.insert(2, "--force")
        
        ReturnCode, Stdout, Stderr = self.RunCommand(Command)
        
        if ReturnCode != 0:
            # Check if main branch exists
            BranchReturnCode, BranchStdout, BranchStderr = self.RunCommand(["git", "branch"])
            
            if "main" not in BranchStdout:
                print("  Branch 'main' not found, checking for 'master'...")
                
                if "master" in BranchStdout:
                    print("  Found 'master' branch, pushing to 'master'...")
                    Command = ["git", "push", "-u", "origin", "master"]
                    if Force:
                        Command.insert(2, "--force")
                    
                    ReturnCode, Stdout, Stderr = self.RunCommand(Command)
                else:
                    # Create main branch
                    print("  Creating 'main' branch...")
                    BranchReturnCode, BranchStdout, BranchStderr = self.RunCommand(["git", "checkout", "-b", "main"])
                    
                    if BranchReturnCode != 0:
                        print(f"  Error creating 'main' branch: {BranchStderr}")
                        return False
                    
                    # Try push again
                    Command = ["git", "push", "-u", "origin", "main"]
                    if Force:
                        Command.insert(2, "--force")
                    
                    ReturnCode, Stdout, Stderr = self.RunCommand(Command)
        
        if ReturnCode != 0:
            print(f"  Error pushing to GitHub: {Stderr}")
            print("\nPossible issues:")
            print("1. GitHub repository doesn't exist - create it first at https://github.com/new")
            print("2. SSH key not set up - check your SSH configuration")
            print("3. Branch naming issue - try pushing to 'master' instead of 'main'")
            return False
        
        print("  Successfully pushed to GitHub")
        print(f"\nRepository available at: https://github.com/{self.Username}/{self.RepoName}")
        return True
    
    def Setup(self, Force: bool = False, GitConfig: Optional[dict] = None) -> bool:
        """Run the complete GitHub setup process.
        
        Args:
            Force: Force push to GitHub (overwrite remote history)
            GitConfig: Dictionary with 'name' and 'email' for Git configuration
            
        Returns:
            True if successful, False otherwise
        """
        print(f"Setting up GitHub repository for {self.ProjectDir}")
        
        # Initialize repository
        if not self.InitializeRepository():
            return False
        
        # Configure Git if requested
        if GitConfig:
            if not self.ConfigureGit(GitConfig.get('name'), GitConfig.get('email')):
                return False
        
        # Create .gitignore
        if not self.CreateGitignore():
            return False
        
        # Stage files
        if not self.StageFiles():
            return False
        
        # Create initial commit
        if not self.CreateInitialCommit():
            return False
        
        # Setup remote
        if not self.SetupRemote():
            return False
        
        # Ask for confirmation before pushing to GitHub
        if not Force:
            Response = input(f"\nPush to GitHub repository '{self.Username}/{self.RepoName}'? (y/n): ")
            if Response.lower() != 'y':
                print("Push to GitHub skipped")
                return True
        
        # Push to GitHub
        if not self.PushToGitHub(Force):
            return False
        
        print("\nGitHub repository setup complete!")
        print(f"Repository URL: https://github.com/{self.Username}/{self.RepoName}")
        print("\nNext steps:")
        print("1. Configure GitHub Pages in repository settings")
        print("2. Wait for GitHub Actions to build and deploy the website")
        print("3. Website will be available at:")
        print(f"   https://{self.Username}.github.io/{self.RepoName}/")
        print("   (or at your custom domain if configured)")
        
        return True

def main():
    """Main entry point for the script."""
    Parser = argparse.ArgumentParser(description="Set up GitHub repository for Project Himalaya")
    Parser.add_argument("--dir", dest="ProjectDir", default=".", help="Project directory")
    Parser.add_argument("--repo", dest="RepoName", default="ProjectHimalaya", help="GitHub repository name")
    Parser.add_argument("--user", dest="Username", default="CallMeChewy", help="GitHub username")
    Parser.add_argument("--name", dest="GitName", help="Git user name")
    Parser.add_argument("--email", dest="GitEmail", help="Git user email")
    Parser.add_argument("--force", dest="Force", action="store_true", help="Force push to GitHub")
    
    Args = Parser.parse_args()
    
    GitConfig = None
    if Args.GitName or Args.GitEmail:
        GitConfig = {
            'name': Args.GitName,
            'email': Args.GitEmail
        }
    
    try:
        Setup = GitHubSetup(
            ProjectDir=Args.ProjectDir,
            RepoName=Args.RepoName,
            Username=Args.Username
        )
        
        Success = Setup.Setup(Args.Force, GitConfig)
        return 0 if Success else 1
    
    except Exception as Ex:
        print(f"Error: {str(Ex)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
