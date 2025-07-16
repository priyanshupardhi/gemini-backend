from django.urls import path
from .views import ChatroomListView, ChatroomDetailView, SendMessageView

urlpatterns = [
    path('', ChatroomListView.as_view(), name='chatroom-list'),
    path('<int:chatroom_id>/', ChatroomDetailView.as_view(), name='chatroom-detail'),
    path('<int:chatroom_id>/message/', SendMessageView.as_view(), name='send-message'),
] 