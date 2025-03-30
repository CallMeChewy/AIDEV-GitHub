#!/usr/bin/env python3
# File: JekyllGenerator.py
# Path: AIDEV-GitHub/Core/JekyllGenerator.py
# Standard: AIDEV-PascalCase-1.6
# Created: 2025-03-29
# Last Modified: 2025-03-29  9:30PM
# Description: Module for generating Jekyll-compatible content from Project Himalaya documents

import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional

from Utils.LoggingManager import GetLogger

def GenerateJekyllFrontMatter(Metadata: Dict[str, Any]) -> str:
    """
    Generate Jekyll front matter from document metadata.
    
    Args:
        Metadata: Document metadata dictionary
    
    Returns:
        str: Jekyll front matter YAML block
    """
    Logger = GetLogger("JekyllGenerator")
    
    # Create front matter dictionary
    FrontMatter = {
        "layout": "document",
        "title": Metadata.get("title", "Untitled Document"),
        "doc_number": Metadata.get("doc_number", ""),
        "category": Metadata.get("category", ""),
    }
    
    # Add timestamps if available
    if "created_at" in Metadata:
        FrontMatter["created_at"] = Metadata["created_at"]
    
    if "modified_at" in Metadata:
        FrontMatter["modified_at"] = Metadata["modified_at"]
    
    # Add optional fields if present
    OptionalFields = ["context", "status", "version", "component", "priority"]
    for Field in OptionalFields:
        if Field in Metadata and Metadata[Field]:
            FrontMatter[Field] = Metadata[Field]
    
    # Generate YAML
    try:
        YamlString = yaml.dump(FrontMatter, default_flow_style=False, sort_keys=False)
        return f"---\n{YamlString}---\n\n"
    except Exception as Error:
        Logger.error(f"Error generating front matter: {str(Error)}")
        # Fallback to manual generation if YAML fails
        FrontMatterStr = "---\n"
        for Key, Value in FrontMatter.items():
            if Value is not None:
                FrontMatterStr += f"{Key}: {Value}\n"
        FrontMatterStr += "---\n\n"
        return FrontMatterStr

def GenerateCategoryPage(CategoryID: str, CategoryName: str) -> str:
    """
    Generate a category index page.
    
    Args:
        CategoryID: Category identifier (e.g., "10")
        CategoryName: Category name (e.g., "vision")
    
    Returns:
        str: Jekyll content for the category page
    """
    # Format category name for display
    DisplayName = CategoryName.title()
    
    # Create front matter
    FrontMatter = {
        "layout": "category",
        "title": f"{DisplayName} Documentation",
        "category_id": CategoryName,
        "description": f"Documents related to Project Himalaya's {CategoryName} category (series {CategoryID})."
    }
    
    YamlString = yaml.dump(FrontMatter, default_flow_style=False, sort_keys=False)
    
    # Create content
    Content = f"""---
{YamlString}---

This page lists all documents in the {DisplayName} category (series {CategoryID}).
"""
    
    return Content

def GenerateMainIndex(Categories: Dict[str, str], DocumentRegistry: Dict[str, Dict[str, Any]]) -> str:
    """
    Generate the main index page.
    
    Args:
        Categories: Dictionary mapping category IDs to names
        DocumentRegistry: Document registry dictionary
    
    Returns:
        str: Jekyll content for the main index page
    """
    # Create header with front matter
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
"""
    
    # Add feature cards
    Features = [
        {
            "title": "Documentation-Driven Development",
            "description": "Start with comprehensive documentation before implementation to ensure clear specifications and maintainable code."
        },
        {
            "title": "Modular Architecture",
            "description": "Highly modular design with clear separation of concerns, allowing for independent development and testing of components."
        },
        {
            "title": "Session Continuity",
            "description": "Maintain context across development sessions with comprehensive state tracking and knowledge persistence."
        },
        {
            "title": "Knowledge Management",
            "description": "Centralized knowledge management with powerful search and cross-referencing capabilities."
        },
        {
            "title": "Systematic Testing",
            "description": "Comprehensive testing approach integrated from the beginning, ensuring reliable and robust components."
        },
        {
            "title": "AIDEV-PascalCase Standard",
            "description": "Distinctive coding standard that prioritizes visual clarity, readability, and consistent naming conventions."
        }
    ]
    
    for Feature in Features:
        IndexContent += f"""
                <div class="card">
                    <h3>{Feature['title']}</h3>
                    <p>{Feature['description']}</p>
                </div>
"""
    
    # Close features section and add architecture section
    IndexContent += """
            </div>
        </div>
    </section>

    <div class="section-divider">
        <div class="divider-overlay">
            <h2>Collaborative Development Reimagined</h2>
        </div>
    </div>

    <section class="section section-alt" id="architecture">
        <div class="container">
            <div class="section-heading text-center">
                <h2>Layered Architecture</h2>
                <p>Project Himalaya follows a bottom-up layered architecture with clear separation of concerns</p>
            </div>
            
            <div class="architecture-diagram">
                <div class="architecture-layers">
                    <div class="architecture-layer">
                        <h4>Layer 4: Applications</h4>
                        <div class="architecture-components">
                            <div class="architecture-component">OllamaModelEditor</div>
                            <div class="architecture-component">AIDEV-Deploy</div>
                        </div>
                    </div>
                    
                    <div class="architecture-layer">
                        <h4>Layer 3: Development Tools</h4>
                        <div class="architecture-components">
                            <div class="architecture-component">CodeGenerator</div>
                            <div class="architecture-component">TestFramework</div>
                            <div class="architecture-component">DocumentationGenerator</div>
                        </div>
                    </div>
                    
                    <div class="architecture-layer">
                        <h4>Layer 2: Communication Framework</h4>
                        <div class="architecture-components">
                            <div class="architecture-component">TaskManager</div>
                            <div class="architecture-component">AIInterface</div>
                            <div class="architecture-component">KnowledgeTransfer</div>
                        </div>
                    </div>
                    
                    <div class="architecture-layer">
                        <h4>Layer 1: Core Infrastructure</h4>
                        <div class="architecture-components">
                            <div class="architecture-component">DocumentManager</div>
                            <div class="architecture-component">StateManager</div>
                            <div class="architecture-component">StandardsValidator</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="text-center">
                <a href="{{ site.baseurl }}/docs/" class="btn">View Detailed Architecture</a>
            </div>
        </div>
    </section>

    <section class="documentation">
        <div class="container">
            <div class="section-heading text-center">
                <h2>Comprehensive Documentation</h2>
                <p>Explore our extensive documentation to get started with Project Himalaya</p>
            </div>
            
            <div class="features-grid">
"""
    
    # Add category cards
    for CategoryID, CategoryName in Categories.items():
        DisplayName = CategoryName.title()
        IndexContent += f"""
                <div class="card">
                    <h3>{DisplayName}</h3>
                    <p>Documents related to Project Himalaya's {CategoryName} category.</p>
                    <a href="{{{{ site.baseurl }}}}/docs/{CategoryName}/">View Documentation →</a>
                </div>
"""
    
    # Close documentation section and page
    IndexContent += """
            </div>
        </div>
    </section>
</div>
"""
    
    return IndexContent

def GenerateSearchPage() -> str:
    """
    Generate the search page.
    
    Returns:
        str: Jekyll content for the search page
    """
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
    return SearchPage

def GenerateSearchIndexPlugin() -> str:
    """
    Generate the Jekyll plugin for search index generation.
    
    Returns:
        str: Ruby code for the search index generator plugin
    """
    PluginCode = """require 'json'

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
    return PluginCode

def GenerateJekyllConfig(BaseURL: str = "/ProjectHimalaya") -> Dict[str, Any]:
    """
    Generate Jekyll configuration (_config.yml).
    
    Args:
        BaseURL: Base URL path for the GitHub Pages site
    
    Returns:
        Dict[str, Any]: Jekyll configuration dictionary
    """
    Config = {
        "title": "Project Himalaya",
        "description": "A comprehensive framework for AI-human collaborative development",
        "baseurl": BaseURL,
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
    
    return Config