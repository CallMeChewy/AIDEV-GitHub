#!/usr/bin/env python3
# File: github_setup.py
# Path: AIDEV-WEB/scripts/github_setup.py
# Standard: AIDEV-PascalCase-1.6
# Created: 2025-03-28
# Last Modified: 2025-03-29
# Description: Set up GitHub repository for Project Himalaya
# Author: Claude (Anthropic), as part of Project Himalaya
# Human Collaboration: Herbert J. Bowers

"""
GitHub Repository Setup Script

This script automates the process of initializing a local Git repository,
adding the remote origin, and pushing the initial commit to GitHub.
Includes an option to reset (delete) the local repository history.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import Optional, Tuple, List
import shutil # For directory removal

class GitHubSetup:
    """Handles the setup and initialization of a GitHub repository."""
    
    def __init__(self, ProjectDir: Optional[str] = None, 
                 RepoName: Optional[str] = None,
                 Username: str = "CallMeChewy"):
        """Initialize the GitHub setup tool.
        
        Args:
            ProjectDir: Path to the project directory (default: current directory)
            RepoName: GitHub repository name (default: base name of ProjectDir)
            Username: GitHub username (default: "CallMeChewy")
        """
        self.ProjectDir = Path(ProjectDir).resolve() if ProjectDir else Path.cwd().resolve()
        # Default RepoName to the base name of the project directory if not provided
        self.RepoName = RepoName if RepoName else self.ProjectDir.name
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
    
    def InitializeRepository(self) -> Tuple[bool, bool]:
        """Initialize a new Git repository if one doesn't exist.
        
        Returns:
            Tuple[bool, bool]: (success, was_initialized_now)
            - success: True if operation succeeded or repo already existed. False on error.
            - was_initialized_now: True if `git init` was run successfully in this call.
        """
        print(f"Initializing Git repository in {self.ProjectDir}...")
        
        if self.IsGitRepository():
            print("  Directory is already a Git repository.")
            return True, False # Success, but did not initialize now
        
        # Proceed with git init only if it wasn't a repo initially
        ReturnCode, Stdout, Stderr = self.RunCommand(["git", "init"])
        
        if ReturnCode != 0:
            print(f"  Error initializing repository: {Stderr}")
            return False, False # Failed to initialize
        
        print("  Repository initialized successfully")
        return True, True # Success, and was initialized now
    
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
        
        CommitMessage = "Initial commit" # Changed message slightly
        ReturnCode, Stdout, Stderr = self.RunCommand(["git", "commit", "-m", CommitMessage])
        
        if ReturnCode != 0:
            # Handle case where nothing was staged (e.g., only .gitignore added)
            if "nothing to commit" in Stderr or "nothing added to commit" in Stderr:
                 print("  No changes to commit (or only .gitignore added).")
                 return True
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
        
        # Determine current branch name
        BranchReturnCode, CurrentBranch, BranchStderr = self.RunCommand(["git", "rev-parse", "--abbrev-ref", "HEAD"])
        CurrentBranch = CurrentBranch.strip()
        if BranchReturnCode != 0 or not CurrentBranch:
            print(f"  Error determining current branch: {BranchStderr}")
            # Default to main if detection fails, but warn
            print("  Warning: Could not detect current branch, attempting to push to 'main'.")
            CurrentBranch = "main" 
            # Attempt to create main if it doesn't exist
            BranchCheckCode, _, _ = self.RunCommand(["git", "show-ref", "--verify", "--quiet", f"refs/heads/{CurrentBranch}"])
            if BranchCheckCode != 0:
                 print(f"  Branch '{CurrentBranch}' not found locally, attempting to create it.")
                 CreateCode, _, CreateErr = self.RunCommand(["git", "checkout", "-b", CurrentBranch])
                 if CreateCode != 0:
                      print(f"  Error creating branch '{CurrentBranch}': {CreateErr}")
                      return False

        Command = ["git", "push", "-u", "origin", CurrentBranch]
        if Force:
            Command.insert(2, "--force")
        
        ReturnCode, Stdout, Stderr = self.RunCommand(Command)
        
        if ReturnCode != 0:
            print(f"  Error pushing to GitHub: {Stderr}")
            print("\nPossible issues:")
            print("1. GitHub repository doesn't exist - create it first at https://github.com/new")
            print("2. SSH key not set up - check your SSH configuration")
            print(f"3. Branch naming mismatch (local: '{CurrentBranch}') - check remote repository")
            return False
        
        print("  Successfully pushed to GitHub")
        print(f"\nRepository available at: https://github.com/{self.Username}/{self.RepoName}")
        return True

    def _reset_repository(self) -> bool:
        """Handles the process of resetting (deleting) the existing repository."""
        if not self.IsGitRepository():
            print("No existing Git repository found to reset.")
            return False # Nothing to do

        Confirm = input(f"WARNING: You chose to reset. This will DELETE the existing Git repository and all its history at {self.GitDir}.\n"
                        f"This action cannot be undone.\n"
                        f"Are you absolutely sure? (Type YES to confirm): ")
        
        if Confirm == 'YES':
            print(f"  Deleting existing .git directory: {self.GitDir}")
            try:
                shutil.rmtree(self.GitDir)
                print("  Repository history successfully deleted.")
                print("  Please run the script again to initialize a fresh repository.")
                return True # Indicate reset was performed
            except Exception as Ex:
                print(f"  Error deleting .git directory: {str(Ex)}")
                return False # Indicate error during reset
        else:
            print("  Repository reset cancelled.")
            return False # Indicate reset was cancelled

    def Setup(self, Force: bool = False, GitConfig: Optional[dict] = None) -> bool:
        """Run the complete GitHub setup process.
        
        Args:
            Force: Force push to GitHub (skips push/reset prompt)
            GitConfig: Dictionary with 'name' and 'email' for Git configuration
            
        Returns:
            True if successful (including skipped push), False otherwise (error or reset performed).
        """
        print(f"Setting up GitHub repository for {self.ProjectDir}")

        # Initialize repository if needed
        init_success, was_initialized_now = self.InitializeRepository()
        if not init_success:
             print("Setup aborted due to repository initialization failure.")
             return False

        # Configure Git if requested (can be done even on existing repo)
        if GitConfig:
            if not self.ConfigureGit(GitConfig.get('name'), GitConfig.get('email')):
                 return False # Config failed

        # --- Steps only for newly initialized repositories ---
        if was_initialized_now:
            print("\nPerforming setup steps for newly initialized repository...")
            # Create .gitignore
            if not self.CreateGitignore():
                return False
            
            # Stage files
            if not self.StageFiles():
                return False
            
            # Create initial commit
            if not self.CreateInitialCommit():
                return False
            print("Initial setup steps complete.")
        else:
            print("\nSkipping initial setup steps (commit, .gitignore) for existing repository.")
        # --- End steps for newly initialized ---

        # Setup remote (always try to ensure remote is configured)
        if not self.SetupRemote():
            return False
        
        # Ask for confirmation before pushing to GitHub or resetting
        push_decision = 'push' # Default action is to push if Force=True or user selects 'y'
        if not Force:
            while True: # Loop until valid input (y, n, or reset)
                Response = input(f"\nPush to GitHub repository '{self.Username}/{self.RepoName}'? (y/n/reset): ")
                ResponseLower = Response.lower()

                if ResponseLower == 'y':
                    push_decision = 'push'
                    break 
                elif ResponseLower == 'n':
                    push_decision = 'skip'
                    break
                elif ResponseLower == 'reset':
                    push_decision = 'reset'
                    break
                else:
                    print("Invalid input. Please enter 'y', 'n', or 'reset'.")

        # --- Handle user's decision ---
        if push_decision == 'skip':
            print("Push to GitHub skipped.")
            print("\nGitHub repository setup complete (push skipped).")
            print(f"Repository URL: https://github.com/{self.Username}/{self.RepoName}")
            return True # Considered successful setup

        elif push_decision == 'reset':
                    # Attempt to reset the repository
                    reset_performed = self._reset_repository()
                    # Whether reset succeeded, failed, or was cancelled, we stop the current setup flow.
                    # If successful, user needs to re-run. If failed/cancelled, setup is aborted.
                    return False # Indicate setup did not complete normally (reset occurred or was cancelled)
        
        # --- Push to GitHub (only reached if push_decision == 'push') ---
        # Force push if the --force flag was used OR if the repo was just initialized
        should_force_push = Force or was_initialized_now 
        if not self.PushToGitHub(Force=should_force_push):
            if was_initialized_now and not Force:
                 # Specific hint if auto-force push failed after initialization
                 print("\nHint: The automatic force push after initialization failed.")
                 print("      You might need to check remote repository state or manually run:")
                 print(f"      git push --force origin <branch_name>")
            return False # Push failed
        
        # --- Final success message (only reached if push succeeds or was skipped) ---
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
    # Determine default repo name from the current directory's base name
    DefaultRepoName = Path.cwd().resolve().name
    
    Parser = argparse.ArgumentParser(description=f"Set up GitHub repository (default: {DefaultRepoName})")
    Parser.add_argument("--dir", dest="ProjectDir", default=".", help="Project directory")
    Parser.add_argument("--repo", dest="RepoName", default=DefaultRepoName, help="GitHub repository name")
    Parser.add_argument("--user", dest="Username", default="CallMeChewy", help="GitHub username")
    Parser.add_argument("--name", dest="GitName", help="Git user name")
    Parser.add_argument("--email", dest="GitEmail", help="Git user email")
    # Removed --reinitialize flag
    Parser.add_argument("--force", dest="Force", action="store_true", help="Force push to GitHub (skips push/reset prompt)") 
    
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
        
        # Removed Reinitialize argument from Setup call
        Success = Setup.Setup(Args.Force, GitConfig) 
        # Exit code 0 for success (including skipped push), 1 for error or reset action
        return 0 if Success else 1 
    
    except Exception as Ex:
        print(f"Error: {str(Ex)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
