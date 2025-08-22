"""
WSGI config for personal_site project for Liara.ir deployment.
"""

import os
import sys
from pathlib import Path

# Add the project directory to the Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Set the Django settings module for production
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'personal_site.settings_prod')

# Import Django and configure logging
import django
from django.core.wsgi import get_wsgi_application

# Configure Django
django.setup()

# Get the WSGI application
application = get_wsgi_application()

# Optional: Add any additional WSGI middleware here
# from whitenoise import WhiteNoise
# application = WhiteNoise(application, root='staticfiles/')
# application.add_files('staticfiles/', prefix='static/')
