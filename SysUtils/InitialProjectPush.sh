#!/bin/bash

# Script to prepare and push a project to GitHub
# For user: CallMeChewy

# Get the current directory name to use as repo name
REPO_NAME=$(basename "$PWD")
echo "Preparing to push to repository: $REPO_NAME"

# Initialize git if it's not already initialized
if [ ! -d ".git" ]; then
  echo "Initializing git repository..."
  git init
else
  echo "Git repository already initialized."
fi

# Create a .gitignore file if it doesn't exist
if [ ! -f ".gitignore" ]; then
  echo "Creating a basic .gitignore file..."
  cat > .gitignore << EOF
# Dependencies
node_modules/
vendor/
package-lock.json
composer.lock

# Environment files
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Build files
/build
/dist
/out

# Debug logs
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# IDE files
.idea/
.vscode/
*.sublime-project
*.sublime-workspace

# OS files
.DS_Store
Thumbs.db
EOF
  echo ".gitignore file created."
else
  echo ".gitignore file already exists. Keeping existing file."
fi

# Create a README.md file if it doesn't exist
if [ ! -f "README.md" ]; then
  echo "Creating a basic README.md file..."
  cat > README.md << EOF
# $REPO_NAME

## Description
A brief description of your project.

## Installation
Installation instructions here.

## Usage
Usage instructions here.

## License
License information here.
EOF
  echo "README.md file created. Please update it with your project details."
else
  echo "README.md file already exists. Keeping existing file."
fi

# Stage all files
echo "Staging all files..."
git add .

# Commit changes
echo "Committing changes..."
git commit -m "Initial commit"

# Add remote repository if it doesn't exist
if ! git remote | grep -q "origin"; then
  echo "Adding remote repository..."
  
  # Try to use SSH first (if key exists)
  if [ -f ~/.ssh/id_rsa.pub ] || [ -f ~/.ssh/id_ed25519.pub ]; then
    git remote add origin "git@github.com:CallMeChewy/$REPO_NAME.git"
    echo "Added SSH remote URL."
  else
    # If no SSH key, try to use PAT from .env file
    if [ -f .env ] && grep -q "GITHUB_PAT" .env; then
      # Extract PAT from .env file
      GITHUB_PAT=$(grep GITHUB_PAT .env | cut -d= -f2)
      git remote add origin "https://$GITHUB_PAT@github.com/CallMeChewy/$REPO_NAME.git"
      echo "Added HTTPS remote URL with PAT."
    else
      # Fallback to regular HTTPS
      git remote add origin "https://github.com/CallMeChewy/$REPO_NAME.git"
      echo "Added HTTPS remote URL."
    fi
  fi
else
  echo "Remote repository already exists. Updating URL..."
  
  # Check for SSH key or PAT and update accordingly
  if [ -f ~/.ssh/id_rsa.pub ] || [ -f ~/.ssh/id_ed25519.pub ]; then
    git remote set-url origin "git@github.com:CallMeChewy/$REPO_NAME.git"
    echo "Updated to SSH remote URL."
  else
    # If no SSH key, try to use PAT from .env file
    if [ -f .env ] && grep -q "GITHUB_PAT" .env; then
      # Extract PAT from .env file
      GITHUB_PAT=$(grep GITHUB_PAT .env | cut -d= -f2)
      git remote set-url origin "https://$GITHUB_PAT@github.com/CallMeChewy/$REPO_NAME.git"
      echo "Updated to HTTPS remote URL with PAT."
    fi
  fi
fi

# Push to GitHub
echo "Pushing to GitHub..."
git push -u origin main || git push -u origin master

echo "Project successfully pushed to GitHub repository: $REPO_NAME"
echo "Repository URL: https://github.com/CallMeChewy/$REPO_NAME"