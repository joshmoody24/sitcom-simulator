# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import tomllib
import os
import sys
sys.path.insert(0, os.path.abspath('..')) # enable importing sitcom_simulator

with open('../pyproject.toml', 'rb') as pyproject:
    pyproject = tomllib.load(pyproject)

project = pyproject['project']['name']
author = pyproject['project']['authors'][0]['name']
copyright = f'2024, {author}'
version = pyproject['project']['version']
release = version

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx_autodoc_typehints',
    ]

autosummary_generate = True
autodoc_typehints = "description" # description, signature, none
autodoc_typehints_format = "short"
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__',
    # make function params alphabetical
}


templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo' # 'alabaster'
html_static_path = ['_static']

html_logo = "sitcom-simulator-logo.png"
html_theme_options = {
    "light_css_variables": {
        "color-brand-primary": "green",
        "color-brand-content": "green",
        "color-admonition-background": "green",
    },
    "dark_css_variables": {
        "color-brand-primary": "springgreen",
        "color-brand-content": "springgreen",
        "color-admonition-background": "green",
    },
}