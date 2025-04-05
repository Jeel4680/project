# wsgi.py

from app import app

server = app.server  # Expose the underlying Flask server for gunicorn
