import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.utils import timezone
from .models import Subscription, Usage
from .serializers import SubscriptionStatusSerializer, StripeCheckoutSerializer

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

class SubscribeProView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Initiates a Pro subscription via Stripe Checkout."""
        serializer = StripeCheckoutSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Get or create Stripe customer
                subscription, created = Subscription.objects.get_or_create(
                    user=request.user,
                    defaults={'tier': 'basic', 'status': 'active'}
                )
                
                if not subscription.stripe_customer_id:
                    customer = stripe.Customer.create(
                        email=request.user.email,
                        metadata={'user_id': request.user.id}
                    )
                    subscription.stripe_customer_id = customer.id
                    subscription.save()
                
                # Create Stripe checkout session
                checkout_session = stripe.checkout.Session.create(
                    customer=subscription.stripe_customer_id,
                    payment_method_types=['card'],
                    line_items=[{
                        'price': settings.STRIPE_PRO_PRICE_ID,
                        'quantity': 1,
                    }],
                    mode='subscription',
                    success_url=serializer.validated_data['success_url'],
                    cancel_url=serializer.validated_data['cancel_url'],
                    metadata={'user_id': request.user.id}
                )
                
                return Response({
                    'data': {
                        'checkout_url': checkout_session.url,
                        'session_id': checkout_session.id
                    },
                    'status': 'success',
                    'message': 'Checkout session created successfully'
                })
                
            except stripe.error.StripeError as e:
                return Response({
                    'error': 'Stripe error',
                    'message': str(e),
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'errors': serializer.errors,
            'status': 'error',
            'message': 'Invalid checkout data'
        }, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
    permission_classes = []  # No authentication for webhooks
    
    def post(self, request):
        """Handles Stripe webhook events (e.g., payment success/failure)."""
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            return HttpResponse(status=400)
        
        # Handle the event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            self.handle_checkout_completed(session)
        elif event['type'] == 'customer.subscription.updated':
            subscription = event['data']['object']
            self.handle_subscription_updated(subscription)
        elif event['type'] == 'customer.subscription.deleted':
            subscription = event['data']['object']
            self.handle_subscription_deleted(subscription)
        
        return HttpResponse(status=200)
    
    def handle_checkout_completed(self, session):
        """Handle successful checkout completion."""
        user_id = session.metadata.get('user_id')
        if user_id:
            try:
                subscription = Subscription.objects.get(user_id=user_id)
                subscription.tier = 'pro'
                subscription.status = 'active'
                subscription.stripe_subscription_id = session.subscription
                subscription.save()
            except Subscription.DoesNotExist:
                pass
    
    def handle_subscription_updated(self, stripe_subscription):
        """Handle subscription updates from Stripe."""
        try:
            subscription = Subscription.objects.get(
                stripe_subscription_id=stripe_subscription.id
            )
            subscription.status = stripe_subscription.status
            subscription.current_period_start = timezone.datetime.fromtimestamp(
                stripe_subscription.current_period_start, tz=timezone.utc
            )
            subscription.current_period_end = timezone.datetime.fromtimestamp(
                stripe_subscription.current_period_end, tz=timezone.utc
            )
            subscription.save()
        except Subscription.DoesNotExist:
            pass
    
    def handle_subscription_deleted(self, stripe_subscription):
        """Handle subscription cancellation from Stripe."""
        try:
            subscription = Subscription.objects.get(
                stripe_subscription_id=stripe_subscription.id
            )
            subscription.status = 'canceled'
            subscription.tier = 'basic'
            subscription.save()
        except Subscription.DoesNotExist:
            pass

class SubscriptionStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Checks the user's current subscription tier (Basic or Pro)."""
        subscription, created = Subscription.objects.get_or_create(
            user=request.user,
            defaults={'tier': 'basic', 'status': 'active'}
        )
        
        serializer = SubscriptionStatusSerializer(subscription)
        return Response({
            'data': serializer.data,
            'status': 'success',
            'message': 'Subscription status retrieved successfully'
        })
