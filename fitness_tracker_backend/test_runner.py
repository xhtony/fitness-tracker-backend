"""
Custom test runner that uses SQLite in-memory database for testing.
"""
import os
import sys
import time
from unittest import TestSuite
from django.test.runner import DiscoverRunner
from django.conf import settings
from django.db import connections, DEFAULT_DB_ALIAS
from django.db.backends.base.base import BaseDatabaseWrapper
from django.db.backends.signals import connection_created

class FastTestRunner(DiscoverRunner):
    """A test runner that uses SQLite in-memory database for faster testing."""

    def __init__(self, *args, **kwargs):
        # Keep __init__ small; real forcing happens in setup_databases before Django creates test DBs
        super().__init__(*args, **kwargs)

    def _force_sqlite_settings(self):
        """Modify settings and existing connection objects to use SQLite in-memory DB.
        This must be done before Django creates test databases (i.e. before calling
        super().setup_databases()).
        """
        # Force debug to False to prevent debug-specific behavior
        settings.DEBUG = False
        # Disable logging during tests
        settings.LOGGING = {}

        # Ensure we're using SQLite for testing (shared in-memory DB)
        sqlite_conf = {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'file:testdb?mode=memory&cache=shared',
            'TEST': {
                'NAME': 'file:testdb?mode=memory&cache=shared',
                'MIRROR': False,
            }
        }
        settings.DATABASES = {'default': sqlite_conf}

        # Update any already-created connection objects so they pick up the SQLite config
        for alias in list(connections):
            try:
                conn = connections[alias]
                conn.settings_dict.update(sqlite_conf)
            except Exception:
                # ignore any connection that isn't ready yet
                pass

        # Set test mode flag
        settings.TESTING = True

        # Register signal to ensure SQLite PRAGMA for foreign keys
        def _enable_foreign_keys(connection, **kwargs):
            if getattr(connection, 'vendor', None) == 'sqlite':
                try:
                    cursor = connection.cursor()
                    cursor.execute('PRAGMA foreign_keys = ON;')
                except Exception:
                    pass

        connection_created.connect(_enable_foreign_keys)

        # Disable migrations by patching MigrationExecutor.migration_plan
        try:
            from django.db.migrations.executor import MigrationExecutor
            def no_migrations(self, plan, *args, **kwargs):
                # Return an empty plan so Django thinks there is nothing to migrate
                return []
            MigrationExecutor.migration_plan = no_migrations
        except Exception:
            # If migrations API differs, ignore and let migrations run
            pass

    def setup_databases(self, **kwargs):
        """Set up the test databases using in-memory SQLite for speed."""
        # Make sure settings and connection objects are configured for SQLite before Django creates test DBs
        self._force_sqlite_settings()

        try:
            old_config = super().setup_databases(**kwargs)
            return old_config
        except Exception as e:
            # If setup failed, try a safe teardown and re-raise
            try:
                self.teardown_databases({})
            except Exception:
                pass
            raise

    def run_tests(self, test_labels=None, extra_tests=None, **kwargs):
        """Run tests with optimized settings and proper cleanup."""
        # Setup test environment
        self.setup_test_environment()

        # Default to running app tests if none specified
        if test_labels is None:
            test_labels = ['activities', 'authentication']

        old_config = None
        try:
            # Setup databases (this will use our forced SQLite settings)
            old_config = self.setup_databases()

            # Build test suite
            suite = self.build_suite(test_labels, extra_tests)

            # Run the test suite
            result = self.run_suite(suite)

            # Return number of failures (Django expects an int)
            return self.suite_result(suite, result)

        except Exception as e:
            import traceback
            traceback.print_exc()
            raise

        finally:
            # Ensure cleanup happens even if tests fail
            try:
                if old_config is not None:
                    self.teardown_databases(old_config)
                self.teardown_test_environment()
            except Exception as e:
                print("Error during test teardown:", str(e))

    def build_suite(self, test_labels=None, extra_tests=None, **kwargs):
        """Build and sort the test suite."""
        # Get the test suite from the parent class
        suite = super().build_suite(test_labels, extra_tests, **kwargs)

        # If suite is already a TestSuite, try to flatten it
        test_cases = {}
        for test in suite:
            if hasattr(test, 'id'):
                test_class = test.__class__
                test_cases.setdefault(test_class, []).append(test)

        # Create a new test suite with sorted tests
        new_suite = TestSuite()
        for test_class in sorted(test_cases.keys(), key=lambda x: x.__name__):
            tests = sorted(test_cases[test_class], key=lambda x: x._testMethodName)
            for test in tests:
                new_suite.addTest(test)

        # If no reordering happened, return original suite
        return new_suite if len(new_suite) > 0 else suite


