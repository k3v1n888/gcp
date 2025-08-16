#!/usr/bin/env python3
"""
Comprehensive Copyright Header Addition Script
Adds copyright headers to all code files in the project
"""

import os
import re
from pathlib import Path

# Copyright headers for different file types
COPYRIGHT_HEADERS = {
    'python': '''"""
Copyright (c) 2025 Kevin Zachary
All rights reserved.

This software and associated documentation files (the "Software") are the 
exclusive property of Kevin Zachary. Unauthorized copying, distribution, 
modification, or use of this software is strictly prohibited.

For licensing inquiries, contact: kevin@zachary.com
"""

''',
    'javascript': '''/*
 * Copyright (c) 2025 Kevin Zachary
 * All rights reserved.
 *
 * This software and associated documentation files (the "Software") are the 
 * exclusive property of Kevin Zachary. Unauthorized copying, distribution, 
 * modification, or use of this software is strictly prohibited.
 *
 * For licensing inquiries, contact: kevin@zachary.com
 */

''',
    'shell': '''#!/bin/bash
# Copyright (c) 2025 Kevin Zachary
# All rights reserved.
#
# This software and associated documentation files (the "Software") are the 
# exclusive property of Kevin Zachary. Unauthorized copying, distribution, 
# modification, or use of this software is strictly prohibited.
#
# For licensing inquiries, contact: kevin@zachary.com

''',
    'html': '''<!--
Copyright (c) 2025 Kevin Zachary
All rights reserved.

This software and associated documentation files (the "Software") are the 
exclusive property of Kevin Zachary. Unauthorized copying, distribution, 
modification, or use of this software is strictly prohibited.

For licensing inquiries, contact: kevin@zachary.com
-->

''',
    'css': '''/*
 * Copyright (c) 2025 Kevin Zachary
 * All rights reserved.
 *
 * This software and associated documentation files (the "Software") are the 
 * exclusive property of Kevin Zachary. Unauthorized copying, distribution, 
 * modification, or use of this software is strictly prohibited.
 *
 * For licensing inquiries, contact: kevin@zachary.com
 */

''',
    'dockerfile': '''# Copyright (c) 2025 Kevin Zachary
# All rights reserved.
#
# This software and associated documentation files (the "Software") are the 
# exclusive property of Kevin Zachary. Unauthorized copying, distribution, 
# modification, or use of this software is strictly prohibited.
#
# For licensing inquiries, contact: kevin@zachary.com

''',
    'yaml': '''# Copyright (c) 2025 Kevin Zachary
# All rights reserved.
#
# This software and associated documentation files (the "Software") are the 
# exclusive property of Kevin Zachary. Unauthorized copying, distribution, 
# modification, or use of this software is strictly prohibited.
#
# For licensing inquiries, contact: kevin@zachary.com

''',
}

def has_copyright(content):
    """Check if file already has a copyright notice"""
    copyright_patterns = [
        r'copyright.*kevin.*zachary',
        r'all rights reserved',
        r'kevin@zachary\.com',
        r'exclusive property of kevin zachary'
    ]
    
    content_lower = content.lower()
    return any(re.search(pattern, content_lower) for pattern in copyright_patterns)

def get_file_type(file_path):
    """Determine file type based on extension and content"""
    path = Path(file_path)
    
    # Check extension
    ext = path.suffix.lower()
    
    if ext in ['.py']:
        return 'python'
    elif ext in ['.js', '.jsx', '.ts', '.tsx']:
        return 'javascript'
    elif ext in ['.sh']:
        return 'shell'
    elif ext in ['.html', '.htm']:
        return 'html'
    elif ext in ['.css', '.scss', '.sass']:
        return 'css'
    elif ext in ['.yml', '.yaml']:
        return 'yaml'
    elif path.name.lower() in ['dockerfile', 'dockerfile.dev', 'dockerfile.prod']:
        return 'dockerfile'
    elif ext in ['.txt'] and 'requirements' in path.name.lower():
        return 'python'  # Requirements files use # comments
    
    # Check if it's a shell script without extension
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            first_line = f.readline().strip()
            if first_line.startswith('#!') and ('bash' in first_line or 'sh' in first_line):
                return 'shell'
    except:
        pass
    
    return None

def add_copyright_to_file(file_path):
    """Add copyright header to a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Skip if already has copyright
        if has_copyright(content):
            print(f"✓ {file_path} - already has copyright")
            return True
        
        file_type = get_file_type(file_path)
        if not file_type:
            print(f"⚠ {file_path} - unknown file type, skipping")
            return False
        
        header = COPYRIGHT_HEADERS[file_type]
        
        # Handle special cases
        if file_type == 'python' and content.startswith('#!/usr/bin/env python'):
            # Preserve shebang line
            lines = content.split('\n')
            shebang = lines[0] + '\n'
            rest_content = '\n'.join(lines[1:])
            new_content = shebang + header + rest_content
        elif file_type == 'shell' and content.startswith('#!'):
            # Replace with our shebang + copyright
            lines = content.split('\n')
            rest_content = '\n'.join(lines[1:])
            new_content = header + rest_content
        else:
            new_content = header + content
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✓ {file_path} - copyright added")
        return True
        
    except Exception as e:
        print(f"✗ {file_path} - error: {e}")
        return False

def find_code_files(root_dir):
    """Find all code files that need copyright headers"""
    code_files = []
    
    # File patterns to include
    include_patterns = [
        '*.py', '*.js', '*.jsx', '*.ts', '*.tsx',
        '*.sh', '*.html', '*.htm', '*.css', '*.scss',
        '*.yml', '*.yaml', '*requirements*.txt'
    ]
    
    # Directories to exclude
    exclude_dirs = {
        '.git', '__pycache__', 'node_modules', '.next',
        'dist', 'build', '.pytest_cache', '.mypy_cache',
        'coverage', '.coverage', 'venv', '.venv', 'env'
    }
    
    # Files to exclude
    exclude_files = {
        'package-lock.json', 'yarn.lock', '.gitignore',
        '.env', '.env.example', 'LICENSE', 'README.md'
    }
    
    root_path = Path(root_dir)
    
    for file_path in root_path.rglob('*'):
        if file_path.is_file():
            # Skip if in excluded directory
            if any(excluded in file_path.parts for excluded in exclude_dirs):
                continue
            
            # Skip if excluded file
            if file_path.name in exclude_files:
                continue
            
            # Check if it matches our patterns or is a Dockerfile
            if (any(file_path.match(pattern) for pattern in include_patterns) or
                file_path.name.lower().startswith('dockerfile')):
                code_files.append(str(file_path))
    
    return sorted(code_files)

def main():
    """Main function"""
    root_dir = Path(__file__).parent
    print(f"🔍 Searching for code files in: {root_dir}")
    
    code_files = find_code_files(root_dir)
    print(f"📁 Found {len(code_files)} code files")
    
    success_count = 0
    for file_path in code_files:
        if add_copyright_to_file(file_path):
            success_count += 1
    
    print(f"\n🎉 Summary:")
    print(f"   Total files: {len(code_files)}")
    print(f"   Successfully processed: {success_count}")
    print(f"   Skipped/Failed: {len(code_files) - success_count}")

if __name__ == "__main__":
    main()
