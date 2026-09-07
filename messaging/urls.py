from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('', views.inbox_view, name='inbox'),
    path('chat/<int:conversation_id>/', views.chat_view, name='chat'),
    path('start/<str:username>/', views.start_conversation_view, name='start_conversation'),
    path('send/<int:conversation_id>/', views.send_message_view, name='send_message'),
    path('messages/<int:conversation_id>/', views.get_messages_api_view, name='get_messages'),
]
