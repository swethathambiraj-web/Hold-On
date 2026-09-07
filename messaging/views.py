from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.models import User
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer


@login_required
def inbox_view(request):
    conversations = request.user.conversations.all().prefetch_related(
        'participants', 'messages__sender'
    )
    return render(request, 'messaging/inbox.html', {
        'conversations': conversations
    })


@login_required
def chat_view(request, conversation_id):
    conversation = get_object_or_404(
        request.user.conversations.prefetch_related('participants', 'messages__sender'),
        id=conversation_id
    )

    # Mark incoming unread messages as read
    conversation.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    other_user = conversation.get_other_participant(request.user)
    messages_list = conversation.messages.all().select_related('sender').order_by('created_at')

    # All user conversations for left sidebar in chat view
    all_conversations = request.user.conversations.all().prefetch_related('participants')

    return render(request, 'messaging/chat.html', {
        'conversation': conversation,
        'other_user': other_user,
        'messages_list': messages_list,
        'all_conversations': all_conversations,
    })


@login_required
def start_conversation_view(request, username):
    other_user = get_object_or_404(User, username=username)
    if other_user == request.user:
        return redirect('messaging:inbox')

    # Find existing conversation between the two users
    conversation = Conversation.objects.filter(
        participants=request.user
    ).filter(
        participants=other_user
    ).first()

    if not conversation:
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, other_user)

    return redirect('messaging:chat', conversation_id=conversation.id)


@login_required
@require_POST
def send_message_view(request, conversation_id):
    conversation = get_object_or_404(
        request.user.conversations.all(),
        id=conversation_id
    )
    text = request.POST.get('text', '').strip()
    media = request.FILES.get('media')

    if not text and not media:
        return JsonResponse({'error': 'Message cannot be empty.'}, status=400)

    message = Message.objects.create(
        conversation=conversation,
        sender=request.user,
        text=text,
        media=media
    )
    # Touch conversation updated_at
    conversation.save()

    # Trigger notification to recipient
    other_user = conversation.get_other_participant(request.user)
    if other_user:
        try:
            from notifications.models import Notification
            Notification.objects.create(
                recipient=other_user,
                sender=request.user,
                notification_type='message'
            )
        except Exception:
            pass

    return JsonResponse({
        'id': message.id,
        'sender': message.sender.username,
        'text': message.text,
        'media_url': message.media.url if message.media else None,
        'created_at': message.created_at.strftime('%H:%M'),
        'is_me': True,
    })


@login_required
def get_messages_api_view(request, conversation_id):
    """Polling endpoint to retrieve newest messages."""
    conversation = get_object_or_404(
        request.user.conversations.all(),
        id=conversation_id
    )
    after_id = request.GET.get('after_id', 0)
    messages_qs = conversation.messages.filter(id__gt=after_id).select_related('sender').order_by('created_at')

    # Mark as read
    messages_qs.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    data = []
    for msg in messages_qs:
        data.append({
            'id': msg.id,
            'sender': msg.sender.username,
            'avatar_url': msg.sender.avatar_url,
            'text': msg.text,
            'media_url': msg.media.url if msg.media else None,
            'created_at': msg.created_at.strftime('%H:%M'),
            'is_me': (msg.sender == request.user),
        })

    return JsonResponse({'messages': data})


# DRF API ViewSets
class ConversationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.conversations.all().prefetch_related('participants', 'messages')

    @action(detail=True, methods=['get', 'post'])
    def messages(self, request, pk=None):
        conversation = self.get_object()
        if request.method == 'POST':
            serializer = MessageSerializer(data=request.data)
            if serializer.is_valid():
                msg = serializer.save(conversation=conversation, sender=request.user)
                conversation.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            messages = conversation.messages.all().select_related('sender')
            serializer = MessageSerializer(messages, many=True)
            return Response(serializer.data)
