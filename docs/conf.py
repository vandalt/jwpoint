"""Configuration for the jwpoint Sphinx documentation."""

import sys
from pathlib import Path

DOCS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(DOCS_DIR.parent / "src"))

project = "jwpoint"
copyright = "2026, Thomas Vandal"
author = "Thomas Vandal"

extensions = [
    "myst_nb",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx_autodoc_typehints",
]

intersphinx_mapping = {
    "scipy": ("https://docs.scipy.org/doc/scipy", None),
    "jwst": ("https://jwst-pipeline.readthedocs.io/en/latest", None),
}

source_suffix = {
    ".md": "myst-nb",
    ".ipynb": "myst-nb",
}

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
nb_execution_mode = "off"

html_theme = "sphinx_book_theme"
html_title = "jwpoint"
html_theme_options = {
    "repository_url": "https://github.com/vandalt/jwpoint",
    "use_repository_button": True,
}

autodoc_typehints = "description"
