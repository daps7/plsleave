import sys
import site
import os

# Add virtualenv
site.addsitedir('/var/www/plsleave/plsleave/venv/lib/python3.12/site-packages')
sys.path.insert(0, '/var/www/plsleave')

# Import Flask app
from plsleave import app as application
