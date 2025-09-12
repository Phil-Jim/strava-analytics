#!/usr/bin/env python3
import os
import sys
import subprocess

print("=== Django Deployment Debug Script ===")
print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")
print(f"Python path: {sys.path}")

# List files in current directory
print("\nFiles in current directory:")
for item in os.listdir('.'):
    print(f"  {item}")

# Check if Django project exists
if os.path.exists('strava_analytics'):
    print("\n✅ strava_analytics directory found")
    if os.path.exists('strava_analytics/wsgi.py'):
        print("✅ wsgi.py file found")
    else:
        print("❌ wsgi.py file NOT found")
else:
    print("❌ strava_analytics directory NOT found")

# Try to import the WSGI module
try:
    from strava_analytics.wsgi import application
    print("✅ WSGI application imported successfully")
except ImportError as e:
    print(f"❌ WSGI import failed: {e}")

# Start gunicorn
print("\nStarting gunicorn...")
cmd = [
    'python', '-m', 'gunicorn',
    'strava_analytics.wsgi:application',
    '--worker-tmp-dir', '/dev/shm',
    '--bind', f'0.0.0.0:{os.environ.get("PORT", "8080")}'
]
print(f"Running command: {' '.join(cmd)}")
subprocess.exec(cmd)