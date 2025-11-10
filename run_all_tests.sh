#!/bin/bash
# Run all tests for Library Management System

echo "Running All Tests..."
echo "===================="

python manage.py test library_api -v 2

echo ""
echo "All tests completed!"

