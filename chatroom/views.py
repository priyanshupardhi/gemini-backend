from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.utils import timezone
from .models import Chatroom, Message
from .serializers import (
    ChatroomSerializer, ChatroomListSerializer, 
    MessageSerializer, SendMessageSerializer
)
from subscription.models import Usage

class ChatroomListView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    @method_decorator(cache_page(60 * 5))  # Cache for 5 minutes
    def get(self, request):
        """List all chatrooms for the authenticated user with caching."""
        cache_key = f"chatrooms_{request.user.id}"
        cached_data = cache.get(cache_key)
        
        if cached_data is None:
            chatrooms = Chatroom.objects.filter(user=request.user)
            serializer = ChatroomListSerializer(chatrooms, many=True)
            cached_data = serializer.data
            cache.set(cache_key, cached_data, 300)  # Cache for 5 minutes
        
        return Response({
            'data': cached_data,
            'status': 'success',
            'message': 'Chatrooms retrieved successfully'
        })
    
    def post(self, request):
        """Create a new chatroom for the authenticated user."""
        serializer = ChatroomSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            chatroom = serializer.save()
            # Clear cache for this user
            cache.delete(f"chatrooms_{request.user.id}")
            return Response({
                'data': serializer.data,
                'status': 'success',
                'message': 'Chatroom created successfully'
            }, status=status.HTTP_201_CREATED)
        return Response({
            'errors': serializer.errors,
            'status': 'error',
            'message': 'Invalid data provided'
        }, status=status.HTTP_400_BAD_REQUEST)

class ChatroomDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, chatroom_id):
        """Retrieve detailed information about a specific chatroom."""
        chatroom = get_object_or_404(Chatroom, id=chatroom_id, user=request.user)
        serializer = ChatroomSerializer(chatroom)
        return Response({
            'data': serializer.data,
            'status': 'success',
            'message': 'Chatroom details retrieved successfully'
        })

class SendMessageView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, chatroom_id):
        """Send a message to the chatroom and receive Gemini response asynchronously."""
        chatroom = get_object_or_404(Chatroom, id=chatroom_id, user=request.user)
        serializer = SendMessageSerializer(data=request.data)
        
        if serializer.is_valid():
            # Rate limiting is now handled by middleware
            # Save user message
            user_message = Message.objects.create(
                chatroom=chatroom,
                sender='user',
                content=serializer.validated_data['content']
            )
            
            # Update usage in database (cache is handled by middleware)
            today = timezone.now().date()
            usage, created = Usage.objects.get_or_create(
                user=request.user, 
                date=today, 
                defaults={'prompt_count': 0}
            )
            usage.prompt_count += 1
            usage.save()
            
            # TODO: Enqueue Gemini API call asynchronously using Celery
            # For now, we'll create a placeholder Gemini response
            gemini_message = Message.objects.create(
                chatroom=chatroom,
                sender='gemini',
                content="This is a placeholder response. Gemini API integration will be implemented with Celery."
            )
            
            # Clear cache for this user
            cache.delete(f"chatrooms_{request.user.id}")
            
            return Response({
                'data': {
                    'user_message': MessageSerializer(user_message).data,
                    'gemini_message': MessageSerializer(gemini_message).data,
                    'usage_remaining': usage.can_send_prompt
                },
                'status': 'success',
                'message': 'Message sent successfully'
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'errors': serializer.errors,
            'status': 'error',
            'message': 'Invalid message data'
        }, status=status.HTTP_400_BAD_REQUEST) 