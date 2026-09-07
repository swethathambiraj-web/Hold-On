def unread_notifications(request):
    """Context processor that injects unread notification and message counts into templates."""
    if request.user.is_authenticated:
        try:
            from .models import Notification
            count = Notification.objects.filter(recipient=request.user, is_read=False).count()
            
            from messaging.models import Message
            unread_messages = Message.objects.filter(
                conversation__participants=request.user,
                is_read=False
            ).exclude(sender=request.user).count()

            return {
                'unread_notifications_count': count,
                'unread_messages_count': unread_messages,
            }
        except Exception:
            return {
                'unread_notifications_count': 0,
                'unread_messages_count': 0,
            }
    return {
        'unread_notifications_count': 0,
        'unread_messages_count': 0,
    }
