# AIDEV-GitHub

**Created: March 30, 2025**
**Last Modified: March 30, 2025**

[Context: Documentation_Tool]
[Status: Active]
[Version: 1.0]

A specialized tool to convert Project Himalaya documentation to GitHub Pages, preserving the rich metadata, cross-references, and document organization.

## 1. Overview

AIDEV-GitHub is designed to transform Project Himalaya's structured documentation into a comprehensive GitHub Pages website. The tool maintains the unique document structure, numbering system, and cross-references while providing a responsive, searchable interface for accessing the knowledge base.

### 1.1 Key Features

- Converts Project Himalaya Markdown documents to Jekyll-compatible format
- Preserves document metadata, context tags, and timestamps
- Maintains cross-references between documents
- Organizes documents by category based on document numbers
- Provides responsive design with light and dark themes
- Implements client-side search functionality
- Generates category index pages
- Supports SEO best practices
- Automates GitHub Pages deployment

## 2. Installation

### 2.1 Prerequisites

- Python 3.8+
- Git (for deployment)

### 2.2 Installation Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/CallMeChewy/AIDEV-GitHub.git
   cd AIDEV-GitHub
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 3. Usage

### 3.1 Basic Usage

Convert a Project Himalaya documentation directory to GitHub Pages:

```bash
python aidev_github.py /path/to/project-himalaya /path/to/output
```

### 3.2 Configuration

Generate a default configuration file:

```bash
python aidev_github.py /path/to/project-himalaya /path/to/output generate-config config.yml
```

Use a custom configuration file:

```bash
python aidev_github.py /path/to/project-himalaya /path/to/output --config config.yml
```

### 3.3 Deploy to GitHub Pages

```bash
python aidev_github.py /path/to/project-himalaya /path/to/output deploy --repository username/repo
```

### 3.4 Command Line Options

```
usage: aidev_github.py [-h] [--base-url BASE_URL] [--config CONFIG]
                      [--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                      [--log-file LOG_FILE]
                      input_dir output_dir {generate-config,deploy} ...

AIDEV-GitHub: Convert Project Himalaya documentation to GitHub Pages

positional arguments:
  input_dir             Source directory containing Project Himalaya documents
  output_dir            Target directory for Jekyll-compatible GitHub Pages site
  {generate-config,deploy}
                        Action to perform
    generate-config     Generate a configuration file with default settings
    deploy              Deploy the generated site to GitHub Pages

optional arguments:
  -h, --help            show this help message and exit
  --base-url BASE_URL   Base URL path for the GitHub Pages site (default: /ProjectHimalaya)
  --config CONFIG       Path to configuration file (JSON or YAML) (default: None)
  --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Set logging level (default: INFO)
  --log-file LOG_FILE   Log to the specified file (default: None)
```

## 4. Configuration Options

The configuration file (YAML or JSON) can include the following settings:

```yaml
categories:
  "00": "navigation"
  "10": "vision"
  "20": "standards"
  "30": "templates"
  "40": "knowledge"
  "50": "implementation"
  "60": "testing"
  "70": "documentation"
  "80": "archives"
  "90": "references"

templates:
  use_custom: false
  custom_path: null

search:
  enabled: true
  include_content: true

github:
  repository: "CallMeChewy/ProjectHimalaya"
  branch: "gh-pages"
  create_branch: true

paths:
  base_url: "/ProjectHimalaya"
  output_dir: "docs"

jekyll:
  title: "Project Himalaya"
  description: "A comprehensive framework for AI-human collaborative development"
  theme: "default"
```

## 5. Examples

### 5.1 Converting a Local Project

```bash
python aidev_github.py ~/Projects/ProjectHimalaya ~/Projects/ProjectHimalaya-Site
```

### 5.2 Using Custom Theme and Templates

```bash
python aidev_github.py ~/Projects/ProjectHimalaya ~/Projects/ProjectHimalaya-Site --config custom-config.yml
```

Where `custom-config.yml` contains:

```yaml
templates:
  use_custom: true
  custom_path: "./custom-templates"

jekyll:
  theme: "custom"
```

### 5.3 Deploying to GitHub Pages

```bash
python aidev_github.py ~/Projects/ProjectHimalaya ~/Projects/ProjectHimalaya-Site deploy --repository CallMeChewy/ProjectHimalaya
```

## 6. Project Structure

```
AIDEV-GitHub/
├── Core/
│   ├── ConverterCore.py         # Main conversion orchestration
│   ├── DocumentProcessor.py     # Document processing
│   ├── MetadataExtractor.py     # Metadata extraction
│   ├── JekyllGenerator.py       # Jekyll generation
│   └── CrossReferenceProcessor.py  # Cross-reference handling
├── Utils/
│   ├── FileUtils.py             # File operations
│   ├── PathManager.py           # Path handling
│   ├── ConfigManager.py         # Configuration management
│   └── LoggingManager.py        # Logging
├── CLI/
│   ├── CommandLineInterface.py  # CLI implementation
│   └── DeploymentManager.py     # Deployment management
├── Templates/
│   ├── LayoutTemplates.py       # Layout templates
│   ├── IncludeTemplates.py      # Include templates
│   └── StyleTemplates.py        # Style templates
├── Tests/
│   ├── test_converter.py        # Tests for converter
│   └── test_deployment.py       # Tests for deployment
└── aidev_github.py              # Main entry point
```

## 7. Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 8. License

This project is licensed under the MIT License - see the LICENSE file for details.

---

*"Code is not merely functional—it is a visual medium that developers interact with for extended periods. The choices made in these standards prioritize the axis of symmetry, character distinction, readability at scale, and visual hierarchy."*

— Herbert J. Bowers