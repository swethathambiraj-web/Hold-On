from django.contrib import admin
from .models import Post, PostMedia, Hashtag, Like, Comment, SavedPost


class PostMediaInline(admin.TabularInline):
    model = PostMedia
    extra = 1


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'created_at', 'likes_count', 'comments_count', 'location']
    list_filter = ['created_at']
    search_fields = ['author__username', 'caption', 'location']
    inlines = [PostMediaInline]


@admin.register(Hashtag)
class HashtagAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'created_at']
    search_fields = ['user__username']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'parent', 'created_at']
    search_fields = ['user__username', 'text']


@admin.register(SavedPost)
class SavedPostAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'created_at']
    search_fields = ['user__username']
