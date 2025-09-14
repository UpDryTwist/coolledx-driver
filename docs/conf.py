"""
Configuration file for the Sphinx documentation builder.

 For the full list of built-in configuration values, see the documentation:
 https://www.sphinx-doc.org/en/master/usage/configuration.html

 -- Project information -----------------------------------------------------
 https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
"""

import os
import sys

sys.path.append(os.path.abspath("../my_awesome_project"))
sys.path.append(os.path.abspath("./my_awesome_project"))
sys.path.append(os.path.abspath("."))
sys.path.append(os.path.abspath(".."))

project = "my_awesome_project"
copyright = ", UpDryTwist"  # noqa: A001
author = "UpDryTwist"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosummary",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
