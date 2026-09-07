from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter

from accounts.views import UserViewSet
from posts.views import PostViewSet
from stories.views import StoryViewSet
from notifications.views import NotificationViewSet
from messaging.views import ConversationViewSet
from feed.views import FeedAPIView, ExploreAPIView

# DRF Router Configuration
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'posts', PostViewSet, basename='post')
router.register(r'stories', StoryViewSet, basename='story')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'conversations', ConversationViewSet, basename='conversation')

urlpatterns = [
    path('admin/', admin.site.urls),

    # App Web URLs
    path('accounts/', include('accounts.urls')),
    path('posts/', include('posts.urls')),
    path('stories/', include('stories.urls')),
    path('notifications/', include('notifications.urls')),
    path('messages/', include('messaging.urls')),
    path('', include('feed.urls')),

    # REST API Endpoints (/api/v1/)
    path('api/v1/', include(router.urls)),
    path('api/v1/feed/', FeedAPIView.as_view(), name='api_feed'),
    path('api/v1/explore/', ExploreAPIView.as_view(), name='api_explore'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
