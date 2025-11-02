#!/usr/bin/env python3
"""
Diagnose Dashboard Error Script
Check backend server, database connection and API endpoints
"""

import os
import sys
import requests

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_tracker_backend.settings')

print("=" * 60)
print("HealthTrack Dashboard Error Diagnosis")
print("=" * 60)
print()

# 1. Check Django settings
print("1. Checking Django configuration...")
try:
    import django
    django.setup()
    from django.conf import settings
    print(f"   OK: Django settings loaded")
    print(f"   - DEBUG: {settings.DEBUG}")
    print(f"   - Database engine: {settings.DATABASES['default']['ENGINE']}")
except Exception as e:
    print(f"   ERROR: Django settings error: {e}")
    sys.exit(1)

# 2. Check database connection
print("\n2. Checking database connection...")
try:
    from django.db import connection
    connection.ensure_connection()
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    print("   OK: Database connection successful")
except Exception as e:
    print(f"   ERROR: Database connection failed: {e}")
    print("   - Please check database configuration in .env file")
    print("   - Ensure PostgreSQL server is running")

# 3. Check backend server
print("\n3. Checking backend server (http://localhost:8000)...")
try:
    response = requests.get('http://localhost:8000/api/', timeout=2)
    print(f"   OK: Backend server is running (Status: {response.status_code})")
except requests.exceptions.ConnectionError:
    print("   ERROR: Backend server is not running or unreachable")
    print("   - Run: python manage.py runserver")
    print("   - Or use: start_backend.bat")
except requests.exceptions.Timeout:
    print("   ERROR: Connection timeout")
except Exception as e:
    print(f"   ERROR: {e}")

# 4. Check API endpoints
print("\n4. Checking API endpoints...")
endpoints = [
    ('/api/activities/stats/', 'GET'),
    ('/api/activities/recent/', 'GET'),
    ('/api/auth/login/', 'POST'),
]

for endpoint, method in endpoints:
    try:
        if method == 'GET':
            response = requests.get(f'http://localhost:8000{endpoint}', timeout=2)
        else:
            response = requests.options(f'http://localhost:8000{endpoint}', timeout=2)
        
        if response.status_code in [200, 401, 403, 405]:
            print(f"   OK: {endpoint} accessible (Status: {response.status_code})")
        else:
            print(f"   WARNING: {endpoint} returned status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"   ERROR: {endpoint} unreachable (backend server may not be running)")
    except Exception as e:
        print(f"   ERROR: {endpoint} error: {e}")

# 5. Check CORS configuration
print("\n5. Checking CORS configuration...")
cors_origins = settings.CORS_ALLOWED_ORIGINS
print(f"   CORS allowed origins:")
for origin in cors_origins:
    print(f"   - {origin}")
if 'http://localhost:3000' in cors_origins:
    print("   OK: localhost:3000 is configured")
else:
    print("   WARNING: localhost:3000 not in CORS list")

# 6. Check database migrations
print("\n6. Checking database migrations...")
try:
    from django.core.management import call_command
    from io import StringIO
    out = StringIO()
    call_command('showmigrations', '--list', stdout=out)
    migrations = out.getvalue()
    if '[ ]' in migrations:
        print("   WARNING: Unapplied migrations found")
        print("   - Run: python manage.py migrate")
    else:
        print("   OK: All migrations applied")
except Exception as e:
    print(f"   WARNING: Cannot check migrations: {e}")

print("\n" + "=" * 60)
print("Diagnosis Complete")
print("=" * 60)
print("\nRecommendations:")
print("1. Ensure backend server is running: python manage.py runserver")
print("2. Check database connection and .env file")
print("3. Run database migrations: python manage.py migrate")
print("4. Check browser console for errors (F12)")
print("5. Check backend server logs")

