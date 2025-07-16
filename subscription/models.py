from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Subscription(models.Model):
    TIER_CHOICES = [
        ('basic', 'Basic'),
        ('pro', 'Pro'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('canceled', 'Canceled'),
        ('past_due', 'Past Due'),
        ('unpaid', 'Unpaid'),
        ('incomplete', 'Incomplete'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    tier = models.CharField(max_length=10, choices=TIER_CHOICES, default='basic')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True)
    current_period_start = models.DateTimeField(blank=True, null=True)
    current_period_end = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.tier} ({self.status})"
    
    @property
    def is_active(self):
        return self.status == 'active'
    
    @property
    def daily_limit(self):
        return 5 if self.tier == 'basic' else float('inf')

class Usage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='usage')
    date = models.DateField(default=timezone.now)
    prompt_count = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['user', 'date']
    
    def __str__(self):
        return f"{self.user.username} - {self.date}: {self.prompt_count} prompts"
    
    @property
    def can_send_prompt(self):
        subscription = self.user.subscription
        if subscription.tier == 'pro':
            return True
        return self.prompt_count < subscription.daily_limit

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    stripe_payment_intent_id = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='usd')
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.amount} {self.currency} ({self.status})"
