#!/usr/bin/env python3
"""Test WSGI import for debugging Railway deployment"""

import os
import sys
import django
from django.core.wsgi import get_wsgi_application

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'strava_analytics.settings')
print("Setting up Django...")

try:
    django.setup()
    print("✅ Django setup successful")
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    sys.exit(1)

try:
    application = get_wsgi_application()
    print("✅ WSGI application created successfully")
    print(f"Application type: {type(application)}")
except Exception as e:
    print(f"❌ WSGI application creation failed: {e}")
    sys.exit(1)

print("✅ All tests passed - WSGI is ready")