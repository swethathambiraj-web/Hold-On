from django.contrib import admin
from .models import Story, StoryView


class StoryViewInline(admin.TabularInline):
    model = StoryView
    extra = 0
    readonly_fields = ['viewer', 'viewed_at']


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'caption', 'created_at', 'expires_at', 'views_count']
    list_filter = ['created_at', 'expires_at']
    search_fields = ['user__username', 'caption']
    inlines = [StoryViewInline]


@admin.register(StoryView)
class StoryViewAdmin(admin.ModelAdmin):
    list_display = ['story', 'viewer', 'viewed_at']
    search_fields = ['viewer__username']
