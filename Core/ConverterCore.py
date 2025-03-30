#!/usr/bin/env python3
# File: ConverterCore.py
# Path: AIDEV-GitHub/Core/ConverterCore.py
# Standard: AIDEV-PascalCase-1.6
# Created: 2025-03-29
# Last Modified: 2025-03-29  8:00PM
# Description: Core module for converting Project Himalaya documents to Jekyll-compatible GitHub Pages

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

# Import Core components
from Core.DocumentProcessor import ProcessDocument, LoadDocument
from Core.MetadataExtractor import ExtractMetadata
from Core.JekyllGenerator import GenerateJekyllFrontMatter, GenerateCategoryPage
from Core.CrossReferenceProcessor import ProcessCrossReferences

# Import Utils
from Utils.FileUtils import EnsureDirectoryExists, WriteTextFile, CopyFile
from Utils.PathManager import GenerateOutputPath, GetDocumentID, GetCategory
from Utils.ConfigManager import LoadConfiguration, ValidateConfiguration
from Utils.LoggingManager import SetupLogging, GetLogger

class ConverterCore:
    """
    Core converter for transforming Project Himalaya documents to Jekyll-compatible GitHub Pages.
    
    This class orchestrates the entire conversion process, managing document processing,
    metadata extraction, Jekyll generation, and file output.
    """
    
    def __init__(self, InputDir: str, OutputDir: str, BaseURL: str = "/ProjectHimalaya", ConfigPath: Optional[str] = None):
        """
        Initialize the converter with input/output directories and options.
        
        Args:
            InputDir: Source directory containing Project Himalaya documents
            OutputDir: Target directory for Jekyll-compatible GitHub Pages site
            BaseURL: Base URL path for the GitHub Pages site
            ConfigPath: Optional path to configuration file
        """
        self.InputDir = Path(InputDir)
        self.OutputDir = Path(OutputDir)
        self.BaseURL = BaseURL
        self.ConfigPath = ConfigPath
        
        # Initialize logger
        self.Logger = GetLogger("ConverterCore")
        
        # Load configuration
        self.Config = self._LoadConfig()
        
        # Document registry for cross-referencing
        self.DocumentRegistry = {}
        
        # Category mappings for document organization
        self.CategoryMappings = self.Config.get("categories", {
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
        })
        
        # Jekyll directory structure
        self.JekyllDirs = [
            "_layouts",
            "_includes",
            "assets/css",
            "assets/js",
            "assets/images",
            "_sass",
            "docs",
            "_data"
        ]
    
    def Run(self) -> bool:
        """
        Execute the full conversion process.
        
        Returns:
            bool: True if conversion was successful, False otherwise
        """
        try:
            self.Logger.info(f"Starting conversion from {self.InputDir} to {self.OutputDir}")
            
            # Ensure output directory exists
            EnsureDirectoryExists(self.OutputDir)
            
            # Create Jekyll directories
            self._CreateJekyllStructure()
            
            # Scan for Markdown files
            MarkdownFiles = self._FindMarkdownFiles()
            self.Logger.info(f"Found {len(MarkdownFiles)} Markdown files to process")
            
            # First pass: Build document registry
            self._BuildDocumentRegistry(MarkdownFiles)
            self.Logger.info(f"Built document registry with {len(self.DocumentRegistry)} entries")
            
            # Second pass: Process documents and generate Jekyll output
            self._ProcessDocuments(MarkdownFiles)
            
            # Generate category pages
            self._GenerateCategoryPages()
            
            # Create main index page
            self._CreateMainIndex()
            
            # Create search index
            self._CreateSearchIndex()
            
            # Copy assets (banner image, etc.)
            self._CopyAssets()
            
            self.Logger.info("Conversion completed successfully")
            return True
            
        except Exception as Error:
            self.Logger.error(f"Conversion failed: {str(Error)}", exc_info=True)
            return False
    
    def _LoadConfig(self) -> Dict[str, Any]:
        """
        Load and validate configuration.
        
        Returns:
            Dict[str, Any]: Configuration dictionary
        """
        if self.ConfigPath:
            return LoadConfiguration(self.ConfigPath)
        
        # Default configuration
        DefaultConfig = {
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
                "use_custom": True,
                "custom_path": None
            },
            "search": {
                "enabled": True,
                "include_content": True
            }
        }
        
        return DefaultConfig
    
    def _CreateJekyllStructure(self) -> None:
        """Create the required directories for Jekyll site."""
        for DirPath in self.JekyllDirs:
            EnsureDirectoryExists(self.OutputDir / DirPath)
        
        # Create _config.yml
        Config = {
            "title": "Project Himalaya",
            "description": "A comprehensive framework for AI-human collaborative development",
            "baseurl": self.BaseURL,
            "url": "https://callmechewy.github.io",
            "markdown": "kramdown",
            "kramdown": {
                "input": "GFM",
                "syntax_highlighter": "rouge",
                "toc_levels": "2..3"
            },
            "permalink": "/:categories/:title/",
            "defaults": [
                {
                    "scope": {
                        "path": ""
                    },
                    "values": {
                        "layout": "default"
                    }
                },
                {
                    "scope": {
                        "path": "docs"
                    },
                    "values": {
                        "layout": "document"
                    }
                }
            ],
            "exclude": [
                "Gemfile",
                "Gemfile.lock",
                "node_modules",
                "vendor",
                "README.md"
            ]
        }
        
        import yaml
        ConfigPath = self.OutputDir / "_config.yml"
        with open(ConfigPath, "w", encoding="utf-8") as f:
            yaml.dump(Config, f, default_flow_style=False)
            
        self.Logger.info(f"Created Jekyll configuration at {ConfigPath}")
    
    def _FindMarkdownFiles(self) -> List[Path]:
        """
        Find all Markdown files in the input directory.
        
        Returns:
            List[Path]: List of paths to Markdown files
        """
        MarkdownFiles = list(self.InputDir.glob("**/*.md"))
        return [File for File in MarkdownFiles if File.is_file()]
    
    def _BuildDocumentRegistry(self, MarkdownFiles: List[Path]) -> None:
        """
        Build a registry of all documents and their metadata.
        
        This registry is used for cross-referencing between documents.
        
        Args:
            MarkdownFiles: List of paths to Markdown files
        """
        for FilePath in MarkdownFiles:
            try:
                # Get document content
                Content = LoadDocument(FilePath)
                
                # Extract metadata
                Metadata = ExtractMetadata(Content)
                
                # Get document ID and category
                DocID = GetDocumentID(FilePath.name)
                if not DocID:
                    # Skip files without proper document ID
                    continue
                    
                Category = GetCategory(DocID, self.CategoryMappings)
                
                # Generate output path
                RelPath = FilePath.relative_to(self.InputDir)
                OutputPath = GenerateOutputPath(RelPath, Category, self.OutputDir)
                
                # Register document
                self.DocumentRegistry[DocID] = {
                    "title": Metadata.get("title", FilePath.stem),
                    "path": str(OutputPath),
                    "category": Category,
                    "metadata": Metadata,
                    "url": f"{self.BaseURL}/docs/{Category}/{DocID}/"
                }
                
            except Exception as Error:
                self.Logger.warning(f"Error registering document {FilePath}: {str(Error)}")
    
    def _ProcessDocuments(self, MarkdownFiles: List[Path]) -> None:
        """
        Process all Markdown files and generate Jekyll output.
        
        Args:
            MarkdownFiles: List of paths to Markdown files
        """
        for FilePath in MarkdownFiles:
            try:
                # Get document content
                Content = LoadDocument(FilePath)
                
                # Extract metadata
                Metadata = ExtractMetadata(Content)
                
                # Get document ID and category
                DocID = GetDocumentID(FilePath.name)
                if not DocID:
                    # Skip files without proper document ID
                    continue
                    
                Category = GetCategory(DocID, self.CategoryMappings)
                
                # Add additional metadata
                Metadata["doc_number"] = DocID
                Metadata["category"] = Category
                
                # Process document content
                ProcessedContent = ProcessDocument(Content)
                
                # Process cross-references
                ProcessedContent = ProcessCrossReferences(ProcessedContent, self.DocumentRegistry)
                
                # Generate Jekyll front matter
                FrontMatter = GenerateJekyllFrontMatter(Metadata)
                
                # Combine front matter and content
                JekyllContent = f"{FrontMatter}\n{ProcessedContent}"
                
                # Generate output path
                RelPath = FilePath.relative_to(self.InputDir)
                OutputPath = GenerateOutputPath(RelPath, Category, self.OutputDir)
                
                # Ensure parent directory exists
                EnsureDirectoryExists(OutputPath.parent)
                
                # Write output file
                WriteTextFile(OutputPath, JekyllContent)
                
                self.Logger.info(f"Processed document: {FilePath.name} -> {OutputPath}")
                
            except Exception as Error:
                self.Logger.warning(f"Error processing document {FilePath}: {str(Error)}")
    
    def _GenerateCategoryPages(self) -> None:
        """Generate index pages for each category."""
        for CategoryID, CategoryName in self.CategoryMappings.items():
            OutputPath = self.OutputDir / "docs" / CategoryName / "index.md"
            
            # Skip if no documents in this category
            if not any(Doc["category"] == CategoryName for Doc in self.DocumentRegistry.values()):
                continue
                
            # Generate category page
            PageContent = GenerateCategoryPage(CategoryID, CategoryName)
            
            # Ensure parent directory exists
            EnsureDirectoryExists(OutputPath.parent)
            
            # Write output file
            WriteTextFile(OutputPath, PageContent)
            
            self.Logger.info(f"Generated category page: {CategoryName}")
    
    def _CreateMainIndex(self) -> None:
        """Create the main index page for the website."""
        # This would typically load a template and fill in content
        # For now, we'll implement a basic version
        IndexContent = """---
layout: default
title: Project Himalaya
---

<div class="home-page">
    <section class="hero">
        <div class="hero-overlay"></div>
        <div class="container">
            <div class="hero-content">
                <h1>Project Himalaya</h1>
                <p class="lead">A comprehensive framework demonstrating optimal AI-human collaboration, manifested through the development of practical applications that themselves leverage AI capabilities.</p>
                <div class="hero-buttons">
                    <a href="{{ '/docs/' | relative_url }}" class="btn btn-primary">View Documentation</a>
                    <a href="https://github.com/CallMeChewy/ProjectHimalaya" class="btn btn-secondary">GitHub Repository</a>
                </div>
            </div>
        </div>
    </section>

    <section class="features">
        <div class="container">
            <div class="section-heading text-center">
                <h2>Key Features</h2>
                <p>Project Himalaya combines powerful capabilities to enable seamless AI-human collaborative development</p>
            </div>
            
            <div class="features-grid">
                <div class="card">
                    <h3>Documentation-Driven Development</h3>
                    <p>Start with comprehensive documentation before implementation to ensure clear specifications and maintainable code.</p>
                </div>
                
                <div class="card">
                    <h3>Modular Architecture</h3>
                    <p>Highly modular design with clear separation of concerns, allowing for independent development and testing of components.</p>
                </div>
                
                <div class="card">
                    <h3>Session Continuity</h3>
                    <p>Maintain context across development sessions with comprehensive state tracking and knowledge persistence.</p>
                </div>
            </div>
        </div>
    </section>
</div>
"""
        IndexPath = self.OutputDir / "index.md"
        WriteTextFile(IndexPath, IndexContent)
        
        # Create docs index page
        DocsIndexContent = """---
layout: default
title: Project Himalaya Documentation
---

<div class="documentation-header">
    <div class="documentation-overlay">
        <div class="container">
            <h1>Project Himalaya Documentation</h1>
        </div>
    </div>
</div>

<div class="container">
    <div class="docs-home">
        <p>Welcome to the Project Himalaya documentation. This website contains all the documentation for the Project Himalaya framework, organized by category.</p>
        
        <h2>Documentation Categories</h2>
        
        <div class="features-grid">
            {% for category in site.data.categories %}
                <div class="card">
                    <h3>{{ category.name }}</h3>
                    <p>{{ category.description }}</p>
                    <a href="{{ site.baseurl }}/docs/{{ category.id }}/" class="btn">View Category</a>
                </div>
            {% endfor %}
        </div>
        
        <h2>Key Documents</h2>
        
        <ul class="key-documents">
            <li><a href="{{ site.baseurl }}/docs/vision/10-10/">Project Vision</a></li>
            <li><a href="{{ site.baseurl }}/docs/standards/20-10/">AIDEV-PascalCase Standards</a></li>
            <li><a href="{{ site.baseurl }}/docs/knowledge/40-20/">Knowledge Database Structure</a></li>
            <li><a href="{{ site.baseurl }}/docs/implementation/50-10/">DocumentManager Implementation</a></li>
        </ul>
    </div>
</div>
"""
        DocsIndexPath = self.OutputDir / "docs/index.md"
        WriteTextFile(DocsIndexPath, DocsIndexContent)
        
        # Create categories data file
        CategoriesData = []
        for CategoryID, CategoryName in self.CategoryMappings.items():
            CategoriesData.append({
                "id": CategoryName,
                "name": CategoryName.title(),
                "description": f"{CategoryName.title()} documentation (series {CategoryID}).",
                "url": f"/docs/{CategoryName}/"
            })
        
        import yaml
        DataDir = self.OutputDir / "_data"
        EnsureDirectoryExists(DataDir)
        with open(DataDir / "categories.yml", "w") as f:
            yaml.dump(CategoriesData, f, default_flow_style=False)
            
        self.Logger.info("Created main index pages")
    
    def _CreateSearchIndex(self) -> None:
        """Create search functionality and index."""
        if not self.Config.get("search", {}).get("enabled", True):
            self.Logger.info("Search functionality disabled in configuration. Skipping.")
            return
            
        # Create search page
        SearchPage = """---
layout: default
title: Search
custom_js: search
---

<div class="documentation-header">
    <div class="documentation-overlay">
        <div class="container">
            <h1>Search Documentation</h1>
        </div>
    </div>
</div>

<div class="container">
    <div class="search-page">
        <p>Search for documentation across all Project Himalaya components and categories.</p>
        
        <div class="search-container">
            <input type="text" id="search-input" class="search-input" placeholder="Search for documentation...">
            <button id="search-button" class="search-button" type="button">Search</button>
        </div>
        
        <div class="search-filters">
            <div class="filter-group">
                <label>Categories:</label>
                <div class="checkbox-group">
                    {% for category in site.data.categories %}
                    <label>
                        <input type="checkbox" class="category-filter" value="{{ category.id }}" checked> 
                        {{ category.name }}
                    </label>
                    {% endfor %}
                </div>
            </div>
        </div>
        
        <div id="search-results" class="search-results">
            <p class="search-instructions">Enter a search term to find documents.</p>
        </div>
    </div>
</div>

<!-- Include lunr.js for search functionality -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/lunr.js/2.3.9/lunr.min.js"></script>
"""
        SearchDir = self.OutputDir / "search"
        EnsureDirectoryExists(SearchDir)
        WriteTextFile(SearchDir / "index.md", SearchPage)
        
        # Create a placeholder for the search index
        # This would be generated during the Jekyll build
        SearchIndexPlaceholder = """[]"""
        JSDir = self.OutputDir / "assets/js"
        EnsureDirectoryExists(JSDir)
        WriteTextFile(JSDir / "search-index.json", SearchIndexPlaceholder)
            
        # Create the Jekyll plugin to generate the search index
        PluginsDir = self.OutputDir / "_plugins"
        EnsureDirectoryExists(PluginsDir)
        SearchIndexPlugin = """require 'json'

module Jekyll
  class SearchIndexGenerator < Jekyll::Generator
    safe true
    priority :low

    def generate(site)
      # Initialize an array to store the search index
      index = []

      # Loop through all pages in the site
      site.pages.each do |page|
        # Skip pages that don't have a title or content
        next if page.data['title'].nil? || page.content.nil?
        
        # Skip search and index pages
        next if page.name == 'index.md' || page.name == 'search.md'
        
        # Extract content without front matter
        content = page.content.strip
        
        # Create snippet (first 200 characters of content)
        snippet = content.gsub(/\\s+/, ' ').strip.slice(0, 200) + '...'
        
        # Add page to index
        index << {
          'id' => page.path,
          'title' => page.data['title'],
          'url' => page.url,
          'content' => content,
          'snippet' => snippet,
          'category' => page.data['category'] || '',
          'tags' => page.data['tags'] || []
        }
      end

      # Write the index to a JSON file
      File.open(File.join(site.dest, 'assets', 'js', 'search-index.json'), 'w') do |file|
        file.write(index.to_json)
      end
      
      # Also copy the file to the source directory for development
      File.open(File.join(site.source, 'assets', 'js', 'search-index.json'), 'w') do |file|
        file.write(index.to_json)
      end
    end
  end
end
"""
        WriteTextFile(PluginsDir / "search_index_generator.rb", SearchIndexPlugin)
            
        self.Logger.info("Created search functionality")
    
    def _CopyAssets(self) -> None:
        """Copy static assets to the output directory."""
        # Copy the banner image if it exists
        BannerPath = self.InputDir / "project-himalaya-banner.jpg"
        if BannerPath.exists():
            DestPath = self.OutputDir / "assets/images/project-himalaya-banner.jpg"
            CopyFile(BannerPath, DestPath)
            self.Logger.info(f"Copied banner image: {BannerPath} -> {DestPath}")
        else:
            self.Logger.warning(f"Banner image not found at {BannerPath}")
            
            # Try alternative locations
            AltPaths = [
                self.InputDir / "Resources/Images/project-himalaya-banner.jpg",
                self.InputDir / "assets/images/project-himalaya-banner.jpg",
                self.InputDir / "docs/assets/images/project-himalaya-banner.jpg",
                self.InputDir / "project-himalaya-banner.png",
                self.InputDir / "Resources/Images/project-himalaya-banner.png"
            ]
            
            for AltPath in AltPaths:
                if AltPath.exists():
                    DestPath = self.OutputDir / "assets/images/project-himalaya-banner.jpg"
                    CopyFile(AltPath, DestPath)
                    self.Logger.info(f"Copied banner image from alternative path: {AltPath} -> {DestPath}")
                    break
            else:
                self.Logger.warning("Banner image not found. The site will use placeholder images.")

# Main function for direct script execution
def ConvertDocuments(InputDir: str, OutputDir: str, BaseURL: str = "/ProjectHimalaya", ConfigPath: Optional[str] = None) -> bool:
    """
    Convert Project Himalaya documents to Jekyll-compatible GitHub Pages.
    
    Args:
        InputDir: Source directory containing Project Himalaya documents
        OutputDir: Target directory for Jekyll-compatible GitHub Pages site
        BaseURL: Base URL path for the GitHub Pages site
        ConfigPath: Optional path to configuration file
    
    Returns:
        bool: True if conversion was successful, False otherwise
    """
    # Setup logging
    SetupLogging()
    
    # Initialize converter
    Converter = ConverterCore(InputDir, OutputDir, BaseURL, ConfigPath)
    
    # Run conversion
    return Converter.Run()