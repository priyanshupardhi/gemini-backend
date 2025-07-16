from django.urls import path
from .views import (
    SignupView, SendOTPView, VerifyOTPView, ForgotPasswordView, ChangePasswordView, UserMeView
)

urlpatterns = [
    path('signup', SignupView.as_view(), name='signup'),
    path('send-otp', SendOTPView.as_view(), name='send-otp'),
    path('verify-otp', VerifyOTPView.as_view(), name='verify-otp'),
    path('forgot-password', ForgotPasswordView.as_view(), name='forgot-password'),
    path('change-password', ChangePasswordView.as_view(), name='change-password'),
    path('user/me', UserMeView.as_view(), name='user-me'),
] 