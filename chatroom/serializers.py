from rest_framework import serializers
from .models import Chatroom, Message

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'sender', 'content', 'created_at']
        read_only_fields = ['created_at']

class ChatroomSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Chatroom
        fields = ['id', 'name', 'created_at', 'updated_at', 'messages', 'message_count']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_message_count(self, obj):
        return obj.messages.count()
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class ChatroomListSerializer(serializers.ModelSerializer):
    message_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = Chatroom
        fields = ['id', 'name', 'created_at', 'updated_at', 'message_count', 'last_message']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_message_count(self, obj):
        return obj.messages.count()
    
    def get_last_message(self, obj):
        last_message = obj.messages.last()
        if last_message:
            return {
                'content': last_message.content[:100] + '...' if len(last_message.content) > 100 else last_message.content,
                'sender': last_message.sender,
                'created_at': last_message.created_at
            }
        return None

class SendMessageSerializer(serializers.Serializer):
    content = serializers.CharField(max_length=10000) 