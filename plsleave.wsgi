import sys
import os
import logging

# Add BOTH paths to Python path
sys.path.insert(0, '/var/www/plsleave/plsleave')
sys.path.insert(0, '/var/www/plsleave')

# Set environment variables from Apache
# (Apache should set these via SetEnv directives)
def get_env_var(name, default=None):
    return os.environ.get(name, default)

# Configure logging
logging.basicConfig(stream=sys.stderr)

# Try to import the app
try:
    from plsleave import app as application
    print("Successfully imported plsleave module", file=sys.stderr)
except ImportError as e:
    print(f"ImportError: {e}", file=sys.stderr)
    print(f"Python path: {sys.path}", file=sys.stderr)
    print(f"Current directory: {os.getcwd()}", file=sys.stderr)
    # Create a simple app for debugging
    from flask import Flask
    application = Flask(__name__)
    @application.route('/')
    def debug():
        return f"Debug: Import failed. Path: {sys.path}"
    raise