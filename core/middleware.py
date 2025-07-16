import json
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework.response import Response
from django.conf import settings

class ConsistentResponseMiddleware(MiddlewareMixin):
    """
    Middleware to ensure consistent JSON responses across all endpoints.
    Standardizes response format and HTTP status codes.
    """
    
    def process_response(self, request, response):
        # Skip for admin and static files
        if request.path.startswith('/admin/') or request.path.startswith('/static/'):
            return response
        
        # If it's already a JsonResponse, ensure consistent structure
        if isinstance(response, JsonResponse):
            data = response.content.decode('utf-8')
            try:
                json_data = json.loads(data)
                if 'status' not in json_data:
                    json_data['status'] = 'success' if response.status_code < 400 else 'error'
                    response.content = json.dumps(json_data).encode('utf-8')
            except json.JSONDecodeError:
                pass
        
        # For DRF responses, ensure consistent structure
        elif isinstance(response, Response):
            if hasattr(response, 'data'):
                if isinstance(response.data, dict):
                    if 'status' not in response.data:
                        response.data['status'] = 'success' if response.status_code < 400 else 'error'
        
        return response
    
    def process_exception(self, request, exception):
        """Handle unhandled exceptions and return consistent error response"""
        return JsonResponse({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred',
            'status': 'error',
            'details': str(exception) if settings.DEBUG else None
        }, status=500) 