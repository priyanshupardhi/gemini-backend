import json
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model

User = get_user_model()

class JWTAuthenticationMiddleware(MiddlewareMixin):
    """
    Middleware for JWT token validation and error handling.
    Provides consistent JSON responses for authentication errors.
    """
    
    def process_request(self, request):
        # Skip authentication for certain paths
        if self._should_skip_auth(request.path):
            return None
        
        # Get token from Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header.startswith('Bearer '):
            return self._unauthorized_response('Authorization header missing or invalid')
        
        token = auth_header.split(' ')[1]
        
        try:
            # Validate token
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            
            # Get user
            try:
                user = User.objects.get(id=user_id)
                request.user = user
            except User.DoesNotExist:
                return self._unauthorized_response('User not found')
                
        except (InvalidToken, TokenError, KeyError) as e:
            return self._unauthorized_response('Invalid or expired token')
        
        return None
    
    def _should_skip_auth(self, path):
        """Paths that don't require authentication"""
        skip_paths = [
            '/auth/signup',
            '/auth/send-otp',
            '/auth/verify-otp',
            '/auth/forgot-password',
            '/webhook/stripe',
            '/admin/',
        ]
        return any(path.startswith(skip_path) for skip_path in skip_paths)
    
    def _unauthorized_response(self, message):
        """Return consistent unauthorized response"""
        return JsonResponse({
            'error': 'Authentication failed',
            'message': message,
            'status': 'error'
        }, status=401)
    
    def process_exception(self, request, exception):
        """Handle exceptions and return consistent JSON responses"""
        return JsonResponse({
            'error': 'Internal server error',
            'message': str(exception),
            'status': 'error'
        }, status=500) 