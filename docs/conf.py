# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import re
import sys

sys.path.insert(0, os.path.abspath("../src"))


project = "Paramak"
copyright = "2024, J. Shimwell"
author = "J. Shimwell"

import paramak

version = paramak.__version__
release = paramak.__version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx_autodoc_typehints",
    "sphinx.ext.coverage",
    "sphinx.ext.napoleon",
    "sphinx.ext.doctest",
    "sphinx.ext.viewcode",
    "sphinxcadquery.sphinxcadquery",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]


# TODO add logo
# html_favicon = "favicon.ico"

# Version match must match the 'version' key in version_switcher.json
pattern = re.compile(r"^[0-9]+\.[0-9]+")
version_match = pattern.search(version)
if version_match:
    version_match = version_match.group()
elif "dev" in version:
    version_match = "dev"
else:
    version_match = version

html_theme_options = {
    "github_url": "https://github.com/fusion-energy/paramak2",
    "switcher": {
        "json_url": "https://raw.githubusercontent.com/fusion-energy/paramak2/main/docs/version_switcher.json",
        "version_match": version_match,
    },
    "navbar_start": ["version-switcher", "navbar-icon-links"],
}
