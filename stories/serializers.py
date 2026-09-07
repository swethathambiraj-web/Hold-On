from rest_framework import serializers
from accounts.serializers import UserSummarySerializer
from .models import Story, StoryView


class StorySerializer(serializers.ModelSerializer):
    user = UserSummarySerializer(read_only=True)
    is_viewed = serializers.SerializerMethodField()
    views_count = serializers.ReadOnlyField()

    class Meta:
        model = Story
        fields = ['id', 'user', 'media', 'caption', 'created_at', 'expires_at', 'is_viewed', 'views_count']
        read_only_fields = ['id', 'user', 'created_at', 'expires_at']

    def get_is_viewed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.is_viewed_by(request.user)
        return False


class StoryViewSerializer(serializers.ModelSerializer):
    viewer = UserSummarySerializer(read_only=True)

    class Meta:
        model = StoryView
        fields = ['id', 'story', 'viewer', 'viewed_at']
