"""Minimal test configuration to debug AutoAPI issues."""

import os
import sys

# Path setup
sys.path.insert(0, os.path.abspath("../../src"))

# Minimal configuration
project = 'haive-dataflow'
extensions = [
    'autoapi.extension',
]

# AutoAPI settings - CRITICAL
autoapi_type = 'python'
autoapi_dirs = ['../../src']
autoapi_own_page_level = 'module'  # KEY SETTING
autoapi_options = [
    'members',
    'undoc-members',
    'show-inheritance',
    'show-module-summary',  # IMPORTANT
]
autoapi_keep_files = True  # Keep generated RST files

# Basic HTML settings
html_theme = 'alabaster'  # Most basic theme