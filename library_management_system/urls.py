"""
URL configuration for library_management_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import connection

try:
    schema_view = get_schema_view(
        openapi.Info(
            title='Library Management API',
            default_version = '1.0.0',
            description =(
                "This API provides comprehensive functionality for managing a library system, "
                "enabling users to interact with a digital library platform. It supports user "
                "authentication, book management, and user interactions, including borrowing and "
                "returning books, managing user accounts, and tracking book availability."
            ),
            terms_of_service="https://www.google.com/policies/terms/",
            contact = openapi.Contact(email='githinjianthony720@gmail.com'),
            license = openapi.License(name='BSD License'),
        ),
        public=True,
        permission_classes=(permissions.AllowAny,),
    )
except Exception as e:
    # Fallback if schema generation fails
    schema_view = None

@api_view(['GET'])
def health_check(request):
    """Simple health check endpoint"""
    return Response({
        'status': 'healthy',
        'service': 'Library Management API',
        'version': '1.0.0'
    })
health_check.permission_classes = [permissions.AllowAny]

@api_view(['GET'])
def db_health_check(request):
    """Database health check endpoint - tests PostgreSQL connection"""
    import os
    from django.db import connection
    
    # First, check environment variables
    env_vars = {
        'DB_NAME': os.getenv("DB_NAME", "NOT SET"),
        'DB_USER': os.getenv("DB_USER", "NOT SET"),
        'DB_PASSWORD': "***" if os.getenv("DB_PASSWORD") else "NOT SET",
        'DB_HOST': os.getenv("DB_HOST", "NOT SET"),
        'DB_PORT': os.getenv("DB_PORT", "NOT SET"),
    }
    
    # Check if any are missing
    missing_vars = [k for k, v in env_vars.items() if v == "NOT SET" and k != 'DB_PASSWORD']
    if missing_vars:
        return Response({
            'status': 'error',
            'message': 'Database environment variables not set',
            'missing_variables': missing_vars,
            'environment_variables': env_vars,
            'suggestion': 'Go to Render dashboard → Your Service → Environment → Add the missing variables'
        }, status=503)
    
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
        
        # Get database info from connection
        db_config = connection.settings_dict
        db_name = db_config.get('NAME', 'unknown')
        db_host = db_config.get('HOST', 'unknown')
        db_port = db_config.get('PORT', 'unknown')
        db_user = db_config.get('USER', 'unknown')
        
        # Check if tables exist (migrations have been run)
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """)
                tables = [row[0] for row in cursor.fetchall()]
        except Exception as table_error:
            tables = []
            # Log the error but continue
            import logging
            logging.getLogger(__name__).error(f"Error checking tables: {str(table_error)}")
        
        # Check for key tables
        key_tables = ['library_api_book', 'library_api_userprofile', 'library_api_transaction']
        missing_tables = [table for table in key_tables if table not in tables] if tables else key_tables
        
        response_data = {
            'status': 'connected',
            'database': {
                'name': db_name,
                'host': db_host,
                'port': str(db_port),
                'user': db_user,
                'connection': 'successful',
                'environment_variables_set': True
            },
            'migrations': {
                'applied': len(tables) > 0,
                'total_tables': len(tables),
                'key_tables_present': len(missing_tables) == 0,
                'missing_tables': missing_tables if missing_tables else None,
                'all_tables': tables[:20] if tables else []  # Show first 20 tables
            }
        }
        
        if not tables:
            response_data['migrations']['warning'] = 'No tables found. Run migrations: python manage.py migrate'
        
        return Response(response_data, status=200)
        
    except Exception as e:
        import traceback
        error_details = str(e)
        error_type = type(e).__name__
        traceback_str = traceback.format_exc()
        
        # Get database config (without password) for debugging
        try:
            db_config = connection.settings_dict
            config_info = {
                'name': db_config.get('NAME', 'unknown'),
                'host': db_config.get('HOST', 'unknown'),
                'port': str(db_config.get('PORT', 'unknown')),
                'user': db_config.get('USER', 'unknown'),
                'engine': db_config.get('ENGINE', 'unknown'),
            }
        except:
            config_info = {'error': 'Could not read database config'}
        
        return Response({
            'status': 'error',
            'database': {
                'connection': 'failed',
                'error_type': error_type,
                'error': error_details,
                'config': config_info,
                'environment_variables': env_vars,
            },
            'troubleshooting': {
                'step1': 'Check Render dashboard → Your Service → Environment → Verify DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT are set',
                'step2': 'Check Render dashboard → Databases → Verify library-db database exists and is running',
                'step3': 'Check build logs to see if migrations ran successfully',
                'step4': 'Verify database is in the same region as your service'
            },
            'traceback': traceback_str if settings.DEBUG else None
        }, status=503)
db_health_check.permission_classes = [permissions.AllowAny]

@api_view(['GET', 'POST'])
def run_migrations(request):
    """Run database migrations"""
    from django.core.management import call_command
    from io import StringIO
    import sys
    
    try:
        # Capture migration output
        out = StringIO()
        err = StringIO()
        call_command('migrate', '--noinput', verbosity=2, stdout=out, stderr=err)
        output = out.getvalue()
        errors = err.getvalue()
        
        return Response({
            'status': 'success',
            'message': 'Migrations completed',
            'output': output,
            'errors': errors if errors else None
        }, status=200)
    except Exception as e:
        import traceback
        return Response({
            'status': 'error',
            'message': 'Migration failed',
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)
run_migrations.permission_classes = [permissions.AllowAny]

@api_view(['POST'])
def create_admin_user(request):
    """Create superuser - accepts username, email, password in request body"""
    import os
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    # Get credentials from request body
    username = request.data.get('username') or request.POST.get('username')
    email = request.data.get('email') or request.POST.get('email', '')
    password = request.data.get('password') or request.POST.get('password')
    
    # Validate required fields
    if not username or not password:
        return Response({
            'status': 'error',
            'message': 'username and password are required',
            'example': {
                'username': 'admin',
                'email': 'admin@example.com',
                'password': 'your-secure-password'
            }
        }, status=400)
    
    try:
        # Check if user already exists
        user, created = User.objects.get_or_create(username=username)
        
        if created:
            # New user - create as superuser
            user.is_superuser = True
            user.is_staff = True
            user.email = email
            user.set_password(password)
            user.save()
            message = f'Successfully created superuser "{username}"'
        else:
            # Existing user - update to superuser
            user.is_superuser = True
            user.is_staff = True
            if email:
                user.email = email
            user.set_password(password)
            user.save()
            message = f'Successfully updated user "{username}" to superuser'
        
        return Response({
            'status': 'success',
            'message': message,
            'username': username,
            'email': email,
            'is_superuser': user.is_superuser,
            'is_staff': user.is_staff,
            'next_step': f'Go to /admin/ and login with username: {username}'
        }, status=200)
        
    except Exception as e:
        import traceback
        return Response({
            'status': 'error',
            'message': 'Error creating superuser',
            'error': str(e),
            'traceback': traceback.format_exc() if settings.DEBUG else None
        }, status=500)
create_admin_user.permission_classes = [permissions.AllowAny]

def root_view(request):
    """Root endpoint - redirects to Swagger UI"""
    if schema_view:
        return redirect('/swagger/')
    else:
        # Fallback if Swagger is not available
        from rest_framework.response import Response
        return Response({
            'message': 'Library Management System API',
            'version': '1.0.0',
            'documentation': '/swagger/',
            'api': '/api/'
        })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('library_api.urls')),
    path('health/', health_check, name='health-check'),
    path('health/db/', db_health_check, name='db-health-check'),
    path('migrate/', run_migrations, name='run-migrations'),
    path('create-admin/', create_admin_user, name='create-admin'),
    path('', root_view, name='root'),
]

# Add Swagger/ReDoc URLs only if schema_view is available
if schema_view:
    urlpatterns += [
        path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc-with-ui'),
    ]
