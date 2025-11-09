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

@api_view(['GET'])
def db_health_check(request):
    """Database health check endpoint - tests PostgreSQL connection"""
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
        
        # Get database info
        db_name = connection.settings_dict.get('NAME', 'unknown')
        db_host = connection.settings_dict.get('HOST', 'unknown')
        db_port = connection.settings_dict.get('PORT', 'unknown')
        db_user = connection.settings_dict.get('USER', 'unknown')
        
        # Check if tables exist (migrations have been run)
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            tables = [row[0] for row in cursor.fetchall()]
        
        # Check for key tables
        key_tables = ['library_api_book', 'library_api_userprofile', 'library_api_transaction']
        missing_tables = [table for table in key_tables if table not in tables]
        
        return Response({
            'status': 'connected',
            'database': {
                'name': db_name,
                'host': db_host,
                'port': db_port,
                'user': db_user,
                'connection': 'successful'
            },
            'migrations': {
                'applied': len(tables) > 0,
                'total_tables': len(tables),
                'key_tables_present': len(missing_tables) == 0,
                'missing_tables': missing_tables if missing_tables else None,
                'all_tables': tables[:10]  # Show first 10 tables
            }
        }, status=200)
        
    except Exception as e:
        return Response({
            'status': 'error',
            'database': {
                'connection': 'failed',
                'error': str(e)
            }
        }, status=503)

@api_view(['GET'])
def root_view(request):
    """Root endpoint with API information"""
    return Response({
        'message': 'Library Management System API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/health/',
            'api': '/api/',
            'swagger': '/swagger/',
            'redoc': '/redoc/',
            'admin': '/admin/'
        }
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('library_api.urls')),
    path('health/', health_check, name='health-check'),
    path('health/db/', db_health_check, name='db-health-check'),
    path('', root_view, name='root'),  # Simple root endpoint that doesn't depend on Swagger
]

# Add Swagger/ReDoc URLs only if schema_view is available
if schema_view:
    urlpatterns += [
        path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc-with-ui'),
    ]
