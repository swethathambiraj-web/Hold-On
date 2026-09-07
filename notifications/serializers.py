from rest_framework import serializers
from accounts.serializers import UserSummarySerializer
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    sender = UserSummarySerializer(read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'sender', 'notification_type',
            'post', 'comment', 'is_read', 'created_at'
        ]
        read_only_fields = ['id', 'recipient', 'sender', 'created_at']
