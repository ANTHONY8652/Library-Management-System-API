#!/usr/bin/env python
"""
Test runner script for Library Management System
Run all tests or specific test modules
"""
import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_management_system.settings')
    django.setup()
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, interactive=False, keepdb=False)
    
    # Get test pattern from command line or run all tests
    test_pattern = sys.argv[1] if len(sys.argv) > 1 else 'library_api.tests'
    
    failures = test_runner.run_tests([test_pattern])
    
    if failures:
        sys.exit(bool(failures))

