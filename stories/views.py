from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db import models
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Story, StoryView
from .forms import StoryCreateForm
from .serializers import StorySerializer


@login_required
def story_create_view(request):
    if request.method == 'POST':
        form = StoryCreateForm(request.POST, request.FILES)
        if form.is_valid():
            story = form.save(commit=False)
            story.user = request.user
            story.save()
            messages.success(request, "Your story was published! It will remain active for 24 hours.")
            return redirect('feed:home')
    else:
        form = StoryCreateForm()
    return render(request, 'stories/story_create.html', {'form': form})


@login_required
@require_POST
def mark_story_viewed_view(request, story_id):
    story = get_object_or_404(Story, id=story_id)
    if story.user != request.user:
        StoryView.objects.get_or_create(story=story, viewer=request.user)
    return JsonResponse({'status': 'viewed', 'views_count': story.views.count()})


@login_required
def user_stories_json_view(request, username):
    """Returns all active stories for a specific user as JSON for the story viewer modal."""
    from accounts.models import User
    target_user = get_object_or_404(User, username=username)
    
    # Check permission
    if target_user.is_private and target_user != request.user:
        if not target_user.is_followed_by(request.user):
            return JsonResponse({'error': 'Private account'}, status=403)

    active_stories = Story.objects.filter(
        user=target_user,
        expires_at__gt=timezone.now()
    ).order_by('created_at')

    stories_data = []
    for s in active_stories:
        stories_data.append({
            'id': s.id,
            'media_url': s.media.url if s.media else '',
            'caption': s.caption,
            'created_at': s.created_at.strftime('%H:%M %p'),
            'views_count': s.views.count(),
            'is_viewed': s.is_viewed_by(request.user),
            'is_owner': (s.user == request.user),
        })

    return JsonResponse({
        'user': {
            'username': target_user.username,
            'avatar_url': target_user.avatar_url,
        },
        'stories': stories_data
    })


@login_required
@require_POST
def story_delete_view(request, story_id):
    story = get_object_or_404(Story, id=story_id, user=request.user)
    story.delete()
    return JsonResponse({'success': True})


# DRF API ViewSet
class StoryViewSet(viewsets.ModelViewSet):
    serializer_class = StorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Return all active stories visible to the user
        following_ids = self.request.user.following_relations.filter(
            status='accepted'
        ).values_list('following_id', flat=True)

        return Story.objects.filter(
            expires_at__gt=timezone.now()
        ).filter(
            models.Q(user=self.request.user) | models.Q(user_id__in=following_ids)
        ).select_related('user').prefetch_related('views')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_viewed(self, request, pk=None):
        story = self.get_object()
        if story.user != request.user:
            StoryView.objects.get_or_create(story=story, viewer=request.user)
        return Response({'status': 'viewed', 'views_count': story.views.count()})
