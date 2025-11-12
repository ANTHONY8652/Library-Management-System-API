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
import os

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
            terms_of_service="https://yourdomain.com/terms/",
            contact = openapi.Contact(email=os.getenv('ADMIN_EMAIL', 'admin@yourdomain.com')),
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
    """Database health check endpoint - SECURED: Admin only"""
    from django.db import connection
    
    # Require authentication and superuser status
    if not request.user.is_authenticated or not request.user.is_superuser:
        return Response({
            'status': 'error',
            'message': 'Permission denied. Only superusers can access database health check.',
        }, status=403)
    
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        
        # Check if tables exist
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """)
                tables = [row[0] for row in cursor.fetchall()]
        except Exception:
            tables = []
        
        # Check for key tables
        key_tables = ['library_api_book', 'library_api_userprofile', 'library_api_transaction']
        missing_tables = [table for table in key_tables if table not in tables] if tables else key_tables
        
        response_data = {
            'status': 'connected',
            'database': {
                'connection': 'successful',
                'migrations_applied': len(tables) > 0,
            },
            'migrations': {
                'applied': len(tables) > 0,
                'total_tables': len(tables),
                'key_tables_present': len(missing_tables) == 0,
                'missing_tables': missing_tables if missing_tables else None,
            }
        }
        
        return Response(response_data, status=200)
        
    except Exception as e:
        return Response({
            'status': 'error',
            'database': {
                'connection': 'failed',
                'error': str(e) if settings.DEBUG else 'Database connection failed. Check server logs.',
            },
        }, status=503)
db_health_check.permission_classes = [permissions.IsAuthenticated]

@api_view(['GET', 'POST'])
def run_migrations(request):
    """Run database migrations - SECURED: Admin only"""
    from django.core.management import call_command
    from io import StringIO
    
    # Require authentication and superuser status
    if not request.user.is_authenticated or not request.user.is_superuser:
        return Response({
            'status': 'error',
            'message': 'Permission denied. Only superusers can run migrations.',
        }, status=403)
    
    try:
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
            'error': str(e) if settings.DEBUG else 'Migration failed. Check server logs.',
            'traceback': traceback.format_exc() if settings.DEBUG else None
        }, status=500)
run_migrations.permission_classes = [permissions.IsAuthenticated]

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
        'EMAIL_BACKEND': email_backend,
        'EMAIL_TIMEOUT': email_timeout,
        'DEFAULT_FROM_EMAIL': getattr(settings, 'DEFAULT_FROM_EMAIL', 'NOT SET'),
    }
    
    # Add SMTP config only if using SMTP backend
    if 'smtp' in email_backend.lower() and 'api' not in email_backend.lower():
        config_info.update({
            'EMAIL_HOST': email_host,
            'EMAIL_PORT': email_port,
            'EMAIL_USE_TLS': email_use_tls,
            'EMAIL_USE_SSL': email_use_ssl,
            'EMAIL_HOST_USER': email_host_user,
            'EMAIL_HOST_PASSWORD': email_host_password,
        })
    else:
        # Add API config for API backends
        brevo_api_key = getattr(settings, 'BREVO_API_KEY', None)
        config_info.update({
            'BREVO_API_KEY': 'SET' if brevo_api_key else 'NOT SET',
            'DEFAULT_FROM_NAME': getattr(settings, 'DEFAULT_FROM_NAME', 'NOT SET'),
        })
    
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
    
    # Test 2: Email backend test (SMTP or API)
    backend_test = {
        'success': False,
        'message': '',
        'error': None
    }
    
    # Check if using Brevo API backend
    if 'brevo' in email_backend.lower() or 'api' in email_backend.lower():
        # Test Brevo API connection
        brevo_api_key = getattr(settings, 'BREVO_API_KEY', None)
        if brevo_api_key:
            try:
                import requests
                # Simple API test - check if API key is valid
                test_url = 'https://api.brevo.com/v3/account'
                headers = {
                    'Accept': 'application/json',
                    'api-key': brevo_api_key,
                }
                response = requests.get(test_url, headers=headers, timeout=email_timeout)
                if response.status_code == 200:
                    backend_test['success'] = True
                    backend_test['message'] = 'Brevo API connection successful'
                else:
                    backend_test['error'] = f'API error: {response.status_code}'
                    backend_test['message'] = f'Brevo API test failed: {response.status_code}'
            except Exception as e:
                backend_test['error'] = str(e)
                backend_test['message'] = f'Brevo API test error: {type(e).__name__}'
                logger.error(f'Brevo API test error: {str(e)}')
        else:
            backend_test['message'] = 'BREVO_API_KEY not set'
    elif socket_test['success']:
        # Test SMTP connection (for SMTP backends)
        try:
            logger.info('Testing SMTP connection')
            connection = get_connection(
                fail_silently=False,
                timeout=email_timeout,
            )
            connection.open()
            connection.close()
            backend_test['success'] = True
            backend_test['message'] = 'SMTP connection successful'
        except Exception as e:
            backend_test['error'] = str(e)
            backend_test['message'] = f'SMTP connection failed: {type(e).__name__}'
            logger.error(f'SMTP test error: {str(e)}')
    else:
        backend_test['message'] = 'Skipped - socket connection failed'
    
    # Test 3: Send test email (optional - only if POST)
    send_test = {
        'success': False,
        'message': '',
        'error': None
    }
    
    # For API backends, we can test sending even if socket test fails
    # For SMTP backends, we need socket test to pass first
    can_test_sending = False
    if 'brevo' in email_backend.lower() or 'api' in email_backend.lower():
        can_test_sending = backend_test['success']
    else:
        can_test_sending = socket_test['success']
    
    if request.method == 'POST' and can_test_sending:
        test_email = request.data.get('email', getattr(settings, 'DEFAULT_FROM_EMAIL', None))
        if test_email:
            try:
                from django.core.mail import send_mail
                logger.info(f'Sending test email to {test_email}')
                result = send_mail(
                    'Test Email - Library Management System',
                    'This is a test email from the Library Management System.',
                    getattr(settings, 'DEFAULT_FROM_EMAIL', test_email),
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
    elif request.method == 'POST' and not can_test_sending:
        send_test['message'] = 'Cannot send test email - backend connection failed'
    
    # Compile results
    # For API backends, we don't need socket test to pass
    if 'brevo' in email_backend.lower() or 'api' in email_backend.lower():
        all_tests_passed = backend_test['success']
    else:
        all_tests_passed = socket_test['success'] and (backend_test['success'] if socket_test['success'] else True)
    
    response_data = {
        'status': 'success' if all_tests_passed else 'error',
        'configuration': config_info,
        'tests': {
            'socket_connection': socket_test,
            'email_backend': backend_test,
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
    
    if not backend_test['success'] and socket_test['success']:
        if 'brevo' in email_backend.lower() or 'api' in email_backend.lower():
            response_data['recommendations'].append({
                'issue': 'Brevo API authentication may be failing',
                'solution': 'Check BREVO_API_KEY is correct and has "Send emails" permission. Verify sender email in Brevo.'
            })
        else:
            response_data['recommendations'].append({
                'issue': 'SMTP authentication may be failing',
                'solution': 'Check EMAIL_HOST_USER and EMAIL_HOST_PASSWORD. For Gmail, use App Password.'
            })
    
    status_code = 200 if all_tests_passed else 503
    return Response(response_data, status=status_code)

# Require authentication for test-email endpoint
test_email_connection.permission_classes = [permissions.IsAuthenticated]

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
