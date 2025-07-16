from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Chatroom(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chatrooms')
    name = models.CharField(max_length=255, default='New Chat')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.name}"

    class Meta:
        ordering = ['-updated_at']

class Message(models.Model):
    SENDER_CHOICES = [
        ('user', 'User'),
        ('gemini', 'Gemini'),
    ]
    
    chatroom = models.ForeignKey(Chatroom, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.chatroom.name} - {self.sender}: {self.content[:50]}"
    
    class Meta:
        ordering = ['created_at'] 