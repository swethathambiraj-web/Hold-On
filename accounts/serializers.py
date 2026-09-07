from rest_framework import serializers
from .models import User, Follow


class UserSummarySerializer(serializers.ModelSerializer):
    avatar_url = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'avatar_url', 'is_private']


class UserProfileSerializer(serializers.ModelSerializer):
    avatar_url = serializers.ReadOnlyField()
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    posts_count = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    is_pending = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'bio', 'avatar_url', 'website_link', 'is_private',
            'followers_count', 'following_count', 'posts_count',
            'is_following', 'is_pending', 'date_joined'
        ]
        read_only_fields = ['id', 'date_joined', 'email']

    def get_followers_count(self, obj):
        return obj.followers_count()

    def get_following_count(self, obj):
        return obj.following_count()

    def get_posts_count(self, obj):
        return obj.posts_count()

    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.is_followed_by(request.user)
        return False

    def get_is_pending(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.is_pending_follow(request.user)
        return False


class FollowSerializer(serializers.ModelSerializer):
    follower = UserSummarySerializer(read_only=True)
    following = UserSummarySerializer(read_only=True)

    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following', 'status', 'created_at']
