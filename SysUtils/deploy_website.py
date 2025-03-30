#!/usr/bin/env python3
# File: deploy_website.py
# Standard: AIDEV-PascalCase-1.6
# Created: 2025-03-26
# Last Modified: 2025-03-26  12:45PM
# Description: Script to prepare and deploy Project Himalaya website

import os
import shutil
import ftplib
import argparse
from datetime import datetime

class WebsiteDeployer:
    """Handles the preparation and deployment of website files."""
    
    def __init__(self, SourceDir: str, DeployDir: str, FtpConfig: dict = None):
        """Initialize with source and deployment directories."""
        self.SourceDir = SourceDir
        self.DeployDir = DeployDir
        self.FtpConfig = FtpConfig
        
    def PrepareDeploymentFiles(self) -> bool:
        """
        Prepare files for deployment by copying them to deployment directory
        and ensuring correct directory structure.
        
        Returns:
            bool: True if preparation was successful
        """
        try:
            print(f"Preparing deployment files from {self.SourceDir} to {self.DeployDir}...")
            
            # Create deployment directory if it doesn't exist
            os.makedirs(self.DeployDir, exist_ok=True)
            
            # Create Resources/Images directory structure
            ImagesDir = os.path.join(self.DeployDir, "Resources", "Images")
            os.makedirs(ImagesDir, exist_ok=True)
            
            # Copy HTML file
            HtmlSourcePath = os.path.join(self.SourceDir, "Source/ProjectHimalaya.html")
            HtmlDestPath = os.path.join(self.DeployDir, "index.html")
            
            if os.path.exists(HtmlSourcePath):
                shutil.copy2(HtmlSourcePath, HtmlDestPath)
                
                # Update image path in HTML file
                self._UpdateImagePath(HtmlDestPath)
                
                print(f"HTML file copied to {HtmlDestPath}")
            else:
                print(f"Warning: HTML file not found at {HtmlSourcePath}")
            
            # Copy banner image
            BannerSourcePath = os.path.join(self.SourceDir, "Resources", "Images", "ProjectHimalayaBanner.png")
            BannerDestPath = os.path.join(ImagesDir, "ProjectHimalayaBanner.png")
            
            if os.path.exists(BannerSourcePath):
                shutil.copy2(BannerSourcePath, BannerDestPath)
                print(f"Banner image copied to {BannerDestPath}")
            else:
                print(f"Warning: Banner image not found at {BannerSourcePath}")
                
                # Try alternative path
                AltBannerPath = os.path.join(self.SourceDir, "ProjectHimalayaBanner.png")
                if os.path.exists(AltBannerPath):
                    shutil.copy2(AltBannerPath, BannerDestPath)
                    print(f"Banner image copied from alternative path to {BannerDestPath}")
                else:
                    print(f"Error: Banner image not found at alternative path {AltBannerPath}")
                    return False
            
            print("Deployment files prepared successfully!")
            return True
            
        except Exception as Error:
            print(f"Error preparing deployment files: {str(Error)}")
            return False
    
    def _UpdateImagePath(self, HtmlFilePath: str) -> None:
        """
        Update image path in HTML file to use correct relative path.
        
        Args:
            HtmlFilePath: Path to HTML file to update
        """
        try:
            with open(HtmlFilePath, 'r', encoding='utf-8') as File:
                Content = File.read()
            
            # Replace relative path with correct one for web server
            UpdatedContent = Content.replace(
                "../Resources/Images/ProjectHimalayaBanner2.png", 
                "Resources/Images/ProjectHimalayaBanner2.png"
            )
            
            with open(HtmlFilePath, 'w', encoding='utf-8') as File:
                File.write(UpdatedContent)
                
            print("Image path updated in HTML file")
                
        except Exception as Error:
            print(f"Error updating image path: {str(Error)}")
    
    def DeployToFtp(self) -> bool:
        """
        Deploy prepared files to FTP server.
        
        Returns:
            bool: True if deployment was successful
        """
        if not self.FtpConfig:
            print("FTP configuration not provided. Skipping FTP deployment.")
            return False
            
        try:
            print(f"Connecting to FTP server {self.FtpConfig['host']}...")
            
            # Connect to FTP server
            Ftp = ftplib.FTP()
            Ftp.connect(self.FtpConfig['host'], self.FtpConfig.get('port', 21))
            Ftp.login(self.FtpConfig['username'], self.FtpConfig['password'])
            
            # Change to target directory if specified
            if 'directory' in self.FtpConfig:
                Ftp.cwd(self.FtpConfig['directory'])
                
            print(f"Connected to FTP server. Current directory: {Ftp.pwd()}")
            
            # Upload HTML file
            HtmlFilePath = os.path.join(self.DeployDir, "index.html")
            with open(HtmlFilePath, 'rb') as File:
                Ftp.storbinary(f"STOR index.html", File)
            print("Uploaded index.html")
            
            # Create Resources/Images directories if they don't exist
            try:
                Ftp.mkd("Resources")
            except ftplib.error_perm:
                pass  # Directory already exists
                
            try:
                Ftp.cwd("Resources")
                Ftp.mkd("Images")
            except ftplib.error_perm:
                pass  # Directory already exists
                
            Ftp.cwd("Images")
            
            # Upload banner image
            BannerPath = os.path.join(self.DeployDir, "Resources", "Images", "ProjectHimalayaBanner.png")
            with open(BannerPath, 'rb') as File:
                Ftp.storbinary(f"STOR ProjectHimalayaBanner2.png", File)
            print("Uploaded ProjectHimalayaBanner2.png")
            
            # Close FTP connection
            Ftp.quit()
            
            print("Files successfully deployed to FTP server!")
            return True
            
        except Exception as Error:
            print(f"Error deploying to FTP server: {str(Error)}")
            return False
            
    def DeployLocally(self) -> bool:
        """
        Keep the prepared deployment directory for local use.
        
        Returns:
            bool: True (always succeeds if preparation was successful)
        """
        print(f"Files have been prepared for deployment in: {self.DeployDir}")
        print("To deploy to your web server manually:")
        print(f"1. Upload all contents of {self.DeployDir} to your web server")
        print("2. Ensure the directory structure is preserved")
        print("3. Make sure index.html is in the root directory")
        return True

def Main():
    """Main entry point of the script."""
    # Parse command line arguments
    Parser = argparse.ArgumentParser(description="Deploy Project Himalaya website")
    Parser.add_argument("--source", default=".", help="Source directory containing website files")
    Parser.add_argument("--deploy", default="./deploy", help="Directory to prepare files for deployment")
    Parser.add_argument("--ftp", action="store_true", help="Deploy to FTP server")
    Parser.add_argument("--host", help="FTP server hostname")
    Parser.add_argument("--user", help="FTP username")
    Parser.add_argument("--password", help="FTP password")
    Parser.add_argument("--port", type=int, default=21, help="FTP server port")
    Parser.add_argument("--directory", help="Target directory on FTP server")
    
    Args = Parser.parse_args()
    
    # Configure FTP if requested
    FtpConfig = None
    if Args.ftp:
        if not Args.host or not Args.user or not Args.password:
            print("Error: FTP deployment requires --host, --user, and --password arguments")
            return
            
        FtpConfig = {
            "host": Args.host,
            "username": Args.user,
            "password": Args.password,
            "port": Args.port
        }
        
        if Args.directory:
            FtpConfig["directory"] = Args.directory
    
    # Create deployer
    Deployer = WebsiteDeployer(Args.source, Args.deploy, FtpConfig)
    
    # Prepare files
    if not Deployer.PrepareDeploymentFiles():
        print("Error: Failed to prepare deployment files")
        return
    
    # Deploy files
    if FtpConfig:
        Deployer.DeployToFtp()
    else:
        Deployer.DeployLocally()

if __name__ == "__main__":
    print(f"Project Himalaya Website Deployment - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    Main()
    print("-" * 60)
    print("Deployment process completed")
