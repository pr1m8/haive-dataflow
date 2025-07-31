#!/usr/bin/env python3
"""Fix malformed print statements with extra characters at the end."""
import glob
import re


def fix_print_statements(filename):
    """Fix malformed print statements in a file."""
    with open(filename) as f:
        content = f.read()

    # Pattern to match print statements with extra characters after the closing quote
    # e.g., print("text"x") -> print("text")
    pattern = r'print\("([^"]+)"[a-z]+"\)'

    # Replace with just the correct print statement
    fixed_content = re.sub(pattern, r'print("\1")', content)

    # Also fix print statements that end with "..")
    fixed_content = re.sub(r'print\("([^"]+)"\.\."\)', r'print("\1...")', fixed_content)

    if content != fixed_content:
        with open(filename, "w") as f:
            f.write(fixed_content)
        return True
    return False


# Fix all Python files in scripts and migration directories
files_to_fix = glob.glob("*.py") + glob.glob("migration/*.py")

fixed_count = 0
for file in files_to_fix:
    if fix_print_statements(file):
        fixed_count += 1
