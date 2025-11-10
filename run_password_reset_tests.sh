#!/bin/bash
# Run password reset tests only

echo "Running Password Reset Tests..."
echo "================================"

python manage.py test library_api.tests.PasswordResetSerializerTest library_api.tests.PasswordResetAPITest -v 2

echo ""
echo "Tests completed!"

