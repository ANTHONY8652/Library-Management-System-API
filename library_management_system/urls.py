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

@api_view(['GET', 'POST'])
def test_email_connection(request):
    """Test email connection and configuration"""
    from django.conf import settings
    from django.core.mail import get_connection
    import socket
    import logging
    
    logger = logging.getLogger(__name__)
    
    # Get email configuration
    email_host = getattr(settings, 'EMAIL_HOST', 'NOT SET')
    email_port = getattr(settings, 'EMAIL_PORT', 'NOT SET')
    email_use_tls = getattr(settings, 'EMAIL_USE_TLS', False)
    email_use_ssl = getattr(settings, 'EMAIL_USE_SSL', False)
    email_host_user = getattr(settings, 'EMAIL_HOST_USER', 'NOT SET')
    email_host_password = "SET" if getattr(settings, 'EMAIL_HOST_PASSWORD', '') else "NOT SET"
    email_backend = getattr(settings, 'EMAIL_BACKEND', 'NOT SET')
    email_timeout = getattr(settings, 'EMAIL_TIMEOUT', 10)
    
    config_info = {
        'EMAIL_HOST': email_host,
        'EMAIL_PORT': email_port,
        'EMAIL_USE_TLS': email_use_tls,
        'EMAIL_USE_SSL': email_use_ssl,
        'EMAIL_HOST_USER': email_host_user,
        'EMAIL_HOST_PASSWORD': email_host_password,
        'EMAIL_BACKEND': email_backend,
        'EMAIL_TIMEOUT': email_timeout,
        'DEFAULT_FROM_EMAIL': getattr(settings, 'DEFAULT_FROM_EMAIL', 'NOT SET'),
    }
    
    # Test 1: Socket connection test
    socket_test = {
        'success': False,
        'message': '',
        'error': None
    }
    
    try:
        logger.info(f'Testing socket connection to {email_host}:{email_port}')
        sock = socket.create_connection((email_host, email_port), timeout=email_timeout)
        sock.close()
        socket_test['success'] = True
        socket_test['message'] = f'Successfully connected to {email_host}:{email_port}'
    except socket.timeout:
        socket_test['error'] = f'Connection timeout to {email_host}:{email_port}'
        socket_test['message'] = 'Timeout - port may be blocked by firewall'
    except socket.gaierror as e:
        socket_test['error'] = f'DNS resolution failed: {str(e)}'
        socket_test['message'] = 'Cannot resolve hostname - check EMAIL_HOST'
    except ConnectionRefusedError:
        socket_test['error'] = 'Connection refused'
        socket_test['message'] = 'Server refused connection - check port and host'
    except OSError as e:
        socket_test['error'] = f'Network error: {str(e)}'
        socket_test['message'] = 'Network error - may be blocked by hosting provider'
    except Exception as e:
        socket_test['error'] = f'Unexpected error: {str(e)}'
        socket_test['message'] = f'Unexpected error: {type(e).__name__}'
    
    # Test 2: SMTP connection test
    smtp_test = {
        'success': False,
        'message': '',
        'error': None
    }
    
    if socket_test['success']:
        try:
            logger.info('Testing SMTP connection')
            connection = get_connection(
                fail_silently=False,
                timeout=email_timeout,
            )
            connection.open()
            connection.close()
            smtp_test['success'] = True
            smtp_test['message'] = 'SMTP connection successful'
        except Exception as e:
            smtp_test['error'] = str(e)
            smtp_test['message'] = f'SMTP connection failed: {type(e).__name__}'
            logger.error(f'SMTP test error: {str(e)}')
    else:
        smtp_test['message'] = 'Skipped - socket connection failed'
    
    # Test 3: Send test email (optional - only if POST)
    send_test = {
        'success': False,
        'message': '',
        'error': None
    }
    
    if request.method == 'POST' and socket_test['success']:
        test_email = request.data.get('email', email_host_user if email_host_user != 'NOT SET' else None)
        if test_email:
            try:
                from django.core.mail import send_mail
                logger.info(f'Sending test email to {test_email}')
                result = send_mail(
                    'Test Email - Library Management System',
                    'This is a test email from the Library Management System.',
                    getattr(settings, 'DEFAULT_FROM_EMAIL', email_host_user),
                    [test_email],
                    fail_silently=False,
                )
                send_test['success'] = True
                send_test['message'] = f'Test email sent successfully to {test_email}'
            except Exception as e:
                send_test['error'] = str(e)
                send_test['message'] = f'Failed to send test email: {type(e).__name__}'
                logger.error(f'Test email error: {str(e)}')
        else:
            send_test['message'] = 'No email address provided for test'
    
    # Compile results
    all_tests_passed = socket_test['success'] and (smtp_test['success'] if socket_test['success'] else True)
    
    response_data = {
        'status': 'success' if all_tests_passed else 'error',
        'configuration': config_info,
        'tests': {
            'socket_connection': socket_test,
            'smtp_connection': smtp_test,
            'send_email': send_test if request.method == 'POST' else {'message': 'Use POST with {"email": "test@example.com"} to test sending'}
        },
        'recommendations': []
    }
    
    # Add recommendations based on test results
    if not socket_test['success']:
        if 'blocked' in socket_test['message'].lower() or 'refused' in socket_test['message'].lower():
            response_data['recommendations'].append({
                'issue': 'Port may be blocked by hosting provider',
                'solution': 'Use an email service API (SendGrid, Mailgun, AWS SES) instead of direct SMTP'
            })
        if email_host == 'smtp.gmail.com':
            response_data['recommendations'].append({
                'issue': 'Gmail SMTP may be blocked',
                'solution': 'Consider using SendGrid (free tier) or Mailgun (free tier) - see EMAIL_FIX_INSTRUCTIONS.md'
            })
    
    if not smtp_test['success'] and socket_test['success']:
        response_data['recommendations'].append({
            'issue': 'SMTP authentication may be failing',
            'solution': 'Check EMAIL_HOST_USER and EMAIL_HOST_PASSWORD. For Gmail, use App Password.'
        })
    
    status_code = 200 if all_tests_passed else 503
    return Response(response_data, status=status_code)

test_email_connection.permission_classes = [permissions.AllowAny]

@api_view(['POST'])
def create_admin_user(request):
    """Create superuser - requires authenticated superuser (SECURED)"""
    # Require authentication and superuser status
    if not request.user.is_authenticated:
        return Response({
            'status': 'error',
            'message': 'Authentication required. You must be logged in as a superuser.',
            'hint': 'Use Django admin login or session authentication'
        }, status=401)
    
    if not request.user.is_superuser:
        return Response({
            'status': 'error',
            'message': 'Permission denied. Only superusers can create admin accounts.',
        }, status=403)
    
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
                'username': 'newadmin',
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
            'next_step': f'New admin can login at /admin/ with username: {username}'
        }, status=200)
        
    except Exception as e:
        import traceback
        return Response({
            'status': 'error',
            'message': 'Error creating superuser',
            'error': str(e),
            'traceback': traceback.format_exc() if settings.DEBUG else None
        }, status=500)
# Require authentication - only superusers can access
create_admin_user.permission_classes = [permissions.IsAuthenticated]

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
    path('test-email/', test_email_connection, name='test-email-connection'),
    # Admin creation endpoint - SECURED: Only authenticated superusers can access
    # To completely disable, set ENABLE_CREATE_ADMIN_ENDPOINT=false in environment
    # path('create-admin/', create_admin_user, name='create-admin'),  # DISABLED
    path('', root_view, name='root'),
]

# Add Swagger/ReDoc URLs only if schema_view is available
if schema_view:
    urlpatterns += [
        path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc-with-ui'),
    ]
