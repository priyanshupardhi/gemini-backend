from django.urls import path
from .views import SubscribeProView, StripeWebhookView, SubscriptionStatusView

urlpatterns = [
    path('subscribe/pro', SubscribeProView.as_view(), name='subscribe-pro'),
    path('webhook/stripe', StripeWebhookView.as_view(), name='stripe-webhook'),
    path('subscription/status', SubscriptionStatusView.as_view(), name='subscription-status'),
] 