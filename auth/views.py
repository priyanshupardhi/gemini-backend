from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import get_user_model, authenticate
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from .models import OTP
from .serializers import (
    SignupSerializer, OTPSendSerializer, OTPVerifySerializer,
    ForgotPasswordSerializer, ChangePasswordSerializer, UserMeSerializer
)
import random
import datetime

User = get_user_model()

class SignupView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'data': serializer.data,
                'status': 'success',
                'message': 'User registered successfully'
            }, status=status.HTTP_201_CREATED)
        return Response({
            'errors': serializer.errors,
            'status': 'error',
            'message': 'Invalid registration data'
        }, status=status.HTTP_400_BAD_REQUEST)

class SendOTPView(APIView):
    def post(self, request):
        serializer = OTPSendSerializer(data=request.data)
        if serializer.is_valid():
            mobile = serializer.validated_data['mobile']
            code = f"{random.randint(100000, 999999)}"
            expires_at = timezone.now() + datetime.timedelta(minutes=5)
            OTP.objects.create(mobile=mobile, code=code, expires_at=expires_at)
            return Response({
                'data': {'otp': code},
                'status': 'success',
                'message': 'OTP sent successfully'
            }, status=status.HTTP_200_OK)
        return Response({
            'errors': serializer.errors,
            'status': 'error',
            'message': 'Invalid mobile number'
        }, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPView(APIView):
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            mobile = serializer.validated_data['mobile']
            code = serializer.validated_data['code']
            try:
                otp_obj = OTP.objects.filter(mobile=mobile, code=code, verified=False).latest('created_at')
                if otp_obj.is_expired():
                    return Response({
                        'error': 'OTP expired',
                        'status': 'error',
                        'message': 'OTP has expired. Please request a new one.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                otp_obj.verified = True
                otp_obj.save()
                user, created = User.objects.get_or_create(mobile=mobile, defaults={'username': mobile})
                refresh = RefreshToken.for_user(user)
                return Response({
                    'data': {'token': str(refresh.access_token)},
                    'status': 'success',
                    'message': 'OTP verified successfully'
                }, status=status.HTTP_200_OK)
            except OTP.DoesNotExist:
                return Response({
                    'error': 'Invalid OTP',
                    'status': 'error',
                    'message': 'Invalid OTP code provided'
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            'errors': serializer.errors,
            'status': 'error',
            'message': 'Invalid verification data'
        }, status=status.HTTP_400_BAD_REQUEST)

class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            mobile = serializer.validated_data['mobile']
            code = f"{random.randint(100000, 999999)}"
            expires_at = timezone.now() + datetime.timedelta(minutes=5)
            OTP.objects.create(mobile=mobile, code=code, expires_at=expires_at)
            return Response({
                'data': {'otp': code},
                'status': 'success',
                'message': 'Password reset OTP sent successfully'
            }, status=status.HTTP_200_OK)
        return Response({
            'errors': serializer.errors,
            'status': 'error',
            'message': 'Invalid mobile number'
        }, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({
                    'error': 'Invalid password',
                    'status': 'error',
                    'message': 'Old password is incorrect'
                }, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({
                'status': 'success',
                'message': 'Password changed successfully'
            }, status=status.HTTP_200_OK)
        return Response({
            'errors': serializer.errors,
            'status': 'error',
            'message': 'Invalid password data'
        }, status=status.HTTP_400_BAD_REQUEST)

class UserMeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        serializer = UserMeSerializer(request.user)
        return Response({
            'data': serializer.data,
            'status': 'success',
            'message': 'User details retrieved successfully'
        })
