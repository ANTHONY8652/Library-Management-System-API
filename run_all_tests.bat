@echo off
REM Run all tests for Library Management System (Windows)

echo Running All Tests...
echo ====================

python manage.py test library_api -v 2

echo.
echo All tests completed!
pause

