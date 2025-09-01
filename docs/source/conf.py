"""
Sphinx configuration for haive-dataflow.
"""

import os
import sys
from datetime import datetime

# -- Path setup --------------------------------------------------------------
sys.path.insert(0, os.path.abspath("../../src"))
sys.path.insert(0, os.path.abspath("../.."))

# -- Project information -----------------------------------------------------
project = "haive-dataflow"
copyright = f"{datetime.now().year}, Haive AI"
author = "Haive AI Team"
release = "0.1.0"
version = "0.1.0"

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.githubpages",
    "sphinx_copybutton",
    "sphinx_design",
    "myst_parser",
]

templates_path = ["_templates"]
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
html_theme = "furo"
html_title = "Haive Dataflow Documentation"
html_static_path = []

# -- Extension configuration -------------------------------------------------

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True

# Intersphinx configuration
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
}

# MyST configuration
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "tasklist",
    "html_image",
]

# Autodoc configuration
autodoc_typehints = "description"
autodoc_member_order = "bysource"
autoclass_content = "both"

# -- Custom setup ------------------------------------------------------------
def setup(app):
    """Sphinx setup hook."""
    app.add_css_file("custom.css", priority=600)