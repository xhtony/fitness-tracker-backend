from .settings import *
import os
import sys

# Test mode
TESTING = True

# Use the standard test runner
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# Use SQLite database for testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'test_db.sqlite3'),
    }
}

# Disable password hashing for faster tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable logging during tests
LOGGING = {}

# Disable CORS for testing
CORS_ALLOW_ALL_ORIGINS = True

# Disable migrations during tests
MIGRATION_MODULES = {}
for app in INSTALLED_APPS:
    MIGRATION_MODULES[app] = None

# Disable migrations completely for tests
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Use faster password hasher for testing
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable cache for tests
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Disable any problematic middleware for tests
MIDDLEWARE = [
    middleware for middleware in MIDDLEWARE
    if middleware != 'corsheaders.middleware.CorsMiddleware'
]

# Add CORS middleware back but with test settings
MIDDLEWARE.append('corsheaders.middleware.CorsMiddleware')

# Disable cache during testing
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Disable CSRF for testing
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

# Disable throttling for tests
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication'
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_THROTTLE_CLASSES': [],
    'DEFAULT_THROTTLE_RATES': {
        'user': None,
        'anon': None,
    },
    'TEST_REQUEST_DEFAULT_FORMAT': 'json'
}

# Disable any background tasks during testing
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Disable password validation during testing
AUTH_PASSWORD_VALIDATORS = []
