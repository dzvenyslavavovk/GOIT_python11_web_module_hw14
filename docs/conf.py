import sys
import os

sys.path.append(os.path.abspath('..'))

project = 'Contacts'
copyright = '2023, dzvenyslavavovk'
author = 'dzvenyslavavovk'


extensions = ['sphinx.ext.autodoc']


templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'alabaster'
html_static_path = ['_static']
