import json
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from django.core.cache import cache
from .models import Usage

class RateLimitMiddleware(MiddlewareMixin):
    """
    Rate limiting middleware for Basic tier users.
    Enforces daily message limits and provides consistent error responses.
    """
    
    def process_request(self, request):
        # Only apply to message sending endpoints
        if not self._is_message_endpoint(request.path):
            return None
        
        # Skip if user is not authenticated
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return None
        
        # Check if user has subscription
        if not hasattr(request.user, 'subscription'):
            return self._rate_limit_response('Subscription not found')
        
        subscription = request.user.subscription
        
        # Pro users have unlimited access
        if subscription.tier == 'pro' and subscription.is_active:
            return None
        
        # Basic users: check daily limit
        if subscription.tier == 'basic':
            today = timezone.now().date()
            cache_key = f"usage_{request.user.id}_{today}"
            
            # Get current usage from cache or database
            current_usage = cache.get(cache_key)
            if current_usage is None:
                usage, created = Usage.objects.get_or_create(
                    user=request.user,
                    date=today,
                    defaults={'prompt_count': 0}
                )
                current_usage = usage.prompt_count
                cache.set(cache_key, current_usage, 86400)  # Cache for 24 hours
            
            # Check if limit exceeded
            if current_usage >= subscription.daily_limit:
                return self._rate_limit_response(
                    f'Daily limit of {subscription.daily_limit} messages reached. Upgrade to Pro for unlimited access.'
                )
            
            # Increment usage in cache
            cache.set(cache_key, current_usage + 1, 86400)
        
        return None
    
    def _is_message_endpoint(self, path):
        """Check if the request is for a message sending endpoint"""
        return '/message/' in path
    
    def _rate_limit_response(self, message):
        """Return consistent rate limit error response"""
        return JsonResponse({
            'error': 'Rate limit exceeded',
            'message': message,
            'status': 'error',
            'upgrade_required': True
        }, status=429) 