from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Follow


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['username', 'email', 'is_private', 'is_staff', 'is_active', 'date_joined']
    list_filter = ['is_private', 'is_staff', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Hold On Profile Info', {
            'fields': ('bio', 'profile_picture', 'website_link', 'is_private')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Hold On Profile Info', {
            'fields': ('email', 'bio', 'profile_picture', 'website_link', 'is_private')
        }),
    )


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ['follower', 'following', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['follower__username', 'following__username']
