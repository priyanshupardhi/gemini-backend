from rest_framework import serializers
from .models import Subscription, Usage
from django.utils import timezone

class SubscriptionStatusSerializer(serializers.ModelSerializer):
    daily_limit = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    current_usage = serializers.SerializerMethodField()
    
    class Meta:
        model = Subscription
        fields = ['tier', 'status', 'is_active', 'daily_limit', 'current_usage', 
                 'current_period_start', 'current_period_end']
    
    def get_current_usage(self, obj):
        today = timezone.now().date()
        usage, created = Usage.objects.get_or_create(
            user=obj.user, 
            date=today, 
            defaults={'prompt_count': 0}
        )
        return usage.prompt_count

class StripeCheckoutSerializer(serializers.Serializer):
    success_url = serializers.URLField()
    cancel_url = serializers.URLField()

class UsageSerializer(serializers.ModelSerializer):
    can_send_prompt = serializers.ReadOnlyField()
    
    class Meta:
        model = Usage
        fields = ['date', 'prompt_count', 'can_send_prompt'] 