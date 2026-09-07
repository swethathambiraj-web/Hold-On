from rest_framework import serializers
from accounts.serializers import UserSummarySerializer
from .models import Post, PostMedia, Hashtag, Like, Comment, SavedPost


class PostMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostMedia
        fields = ['id', 'file', 'media_type', 'order']


class CommentSerializer(serializers.ModelSerializer):
    user = UserSummarySerializer(read_only=True)
    replies_count = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'user', 'post', 'parent', 'text', 'replies_count', 'created_at']
        read_only_fields = ['id', 'user', 'created_at', 'post']

    def get_replies_count(self, obj):
        return obj.replies.count()


class HashtagSerializer(serializers.ModelSerializer):
    posts_count = serializers.ReadOnlyField()

    class Meta:
        model = Hashtag
        fields = ['id', 'name', 'posts_count', 'created_at']


class PostSerializer(serializers.ModelSerializer):
    author = UserSummarySerializer(read_only=True)
    media_items = PostMediaSerializer(many=True, read_only=True)
    likes_count = serializers.ReadOnlyField()
    comments_count = serializers.ReadOnlyField()
    is_liked = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()
    hashtags = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'
    )

    class Meta:
        model = Post
        fields = [
            'id', 'author', 'caption', 'location',
            'media_items', 'hashtags', 'likes_count',
            'comments_count', 'is_liked', 'is_saved',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.is_liked_by(request.user)
        return False

    def get_is_saved(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.is_saved_by(request.user)
        return False
