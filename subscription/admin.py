from django.contrib import admin
from .models import Subscription, Usage, Payment

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'tier', 'status', 'created_at', 'updated_at']
    list_filter = ['tier', 'status', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Usage)
class UsageAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'prompt_count', 'can_send_prompt']
    list_filter = ['date']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['can_send_prompt']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'currency', 'status', 'created_at']
    list_filter = ['status', 'currency', 'created_at']
    search_fields = ['user__username', 'user__email', 'stripe_payment_intent_id']
    readonly_fields = ['created_at']
