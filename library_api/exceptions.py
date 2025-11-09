"""
Custom exception handlers for Django REST Framework
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from django.db import DatabaseError
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
        
        # Check if it's a database error
        if isinstance(exc, DatabaseError):
            return Response({
                'error': 'Database error',
                'message': 'A database error occurred. Please check your database connection.',
                'details': str(exc) if context.get('request') and hasattr(context['request'], 'user') else None
            }, status=500)
        
        # Generic error handler
        return Response({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred.',
            'details': str(exc) if context.get('request') and hasattr(context['request'], 'user') else None
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

