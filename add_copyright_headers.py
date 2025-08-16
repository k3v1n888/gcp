#!/usr/bin/env python3
import os
import re
from pathlib import Path

# Copyright headers
COPYRIGHT_PYTHON = """# Author: Kevin Zachary
# Copyright: Sentient Spire

"""

COPYRIGHT_JS = """/*
 * Author: Kevin Zachary
 * Copyright: Sentient Spire
 */

"""

COPYRIGHT_BASH = """#!/bin/bash
# Author: Kevin Zachary
# Copyright: Sentient Spire

"""

def has_copyright(content):
    """Check if file already has copyright header"""
    return "Kevin Zachary" in content[:500] and "Sentient Spire" in content[:500]

def add_copyright_to_file(file_path):
    """Add copyright header to a file if it doesn't have one"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if has_copyright(content):
            return False  # Already has copyright
        
        # Determine file type and copyright header
        ext = Path(file_path).suffix.lower()
        header = ""
        
        if ext in ['.py']:
            header = COPYRIGHT_PYTHON
        elif ext in ['.js', '.jsx', '.ts', '.tsx']:
            header = COPYRIGHT_JS
        elif ext in ['.sh']:
            header = COPYRIGHT_BASH
            # Handle shebang
            if content.startswith('#!'):
                lines = content.split('\n', 1)
                if len(lines) > 1:
                    content = lines[0] + '\n' + COPYRIGHT_BASH + lines[1]
                else:
                    content = lines[0] + '\n' + COPYRIGHT_BASH
            else:
                content = COPYRIGHT_BASH + content
        else:
            return False  # Unsupported file type
        
        if ext != '.sh':
            content = header + content
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True  # Added copyright
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main function to add copyright headers to all relevant files"""
    extensions = {'.py', '.js', '.jsx', '.ts', '.tsx', '.sh'}
    exclude_dirs = {'node_modules', '.git', 'venv', '.venv', '__pycache__', '.next', 'build', 'dist'}
    
    files_processed = 0
    files_updated = 0
    
    for root, dirs, files in os.walk('.'):
        # Remove excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if Path(file).suffix.lower() in extensions:
                file_path = os.path.join(root, file)
                files_processed += 1
                
                if add_copyright_to_file(file_path):
                    files_updated += 1
                    print(f"Added copyright to: {file_path}")
    
    print(f"\nSummary:")
    print(f"Files processed: {files_processed}")
    print(f"Files updated: {files_updated}")

if __name__ == "__main__":
    main()
