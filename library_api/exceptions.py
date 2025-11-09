"""
Custom exception handlers for Django REST Framework
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from django.db import DatabaseError, ProgrammingError
import logging

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    """
    Custom exception handler that returns JSON responses for all errors
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    # If no response from DRF, handle it ourselves
    if response is None:
        # Log the exception
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        
        # Check if it's a database table missing error
        error_str = str(exc)
        if isinstance(exc, (DatabaseError, ProgrammingError)):
            if 'does not exist' in error_str or 'relation' in error_str.lower():
                return Response({
                    'error': 'Database tables not found',
                    'message': 'Database migrations have not been run. Tables do not exist.',
                    'details': error_str,
                    'solution': {
                        'step1': 'Run migrations using: POST /migrate/ with your DJANGO_SECRET_KEY',
                        'step2': 'Or trigger a manual rebuild in Render dashboard',
                        'step3': 'Check /health/db/ to verify migrations status'
                    }
                }, status=503)
            
            return Response({
                'error': 'Database error',
                'message': 'A database error occurred. Please check your database connection.',
                'details': error_str
            }, status=500)
        
        # Generic error handler
        return Response({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred.',
            'details': str(exc)
        }, status=500)
    
    # Customize the response data
    custom_response_data = {
        'error': 'An error occurred',
        'message': 'Please check your request and try again.',
    }
    
    # Add details if available
    if hasattr(response, 'data'):
        if isinstance(response.data, dict):
            custom_response_data.update(response.data)
        else:
            custom_response_data['details'] = response.data
    
    response.data = custom_response_data
    return response

