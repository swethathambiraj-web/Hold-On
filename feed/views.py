from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

from accounts.models import User
from posts.models import Post, Hashtag
from posts.serializers import PostSerializer
from stories.models import Story


@login_required
def home_feed_view(request):
    user = request.user

    # 1. Followed users' IDs
    following_ids = list(
        user.following_relations.filter(status='accepted').values_list('following_id', flat=True)
    )
    # Include own posts
    feed_user_ids = following_ids + [user.id]

    # 2. Feed Posts
    posts_qs = Post.objects.filter(
        author_id__in=feed_user_ids
    ).select_related('author').prefetch_related(
        'media_items', 'hashtags', 'likes', 'comments__user'
    ).order_by('-created_at')

    paginator = Paginator(posts_qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 3. Active Stories Tray (from followed users + self)
    active_stories = Story.objects.filter(
        user_id__in=feed_user_ids,
        expires_at__gt=timezone.now()
    ).select_related('user').prefetch_related('views').order_by('created_at')

    # Group stories by user and track if user has unseen stories
    stories_by_user = {}
    for story in active_stories:
        u_id = story.user.id
        if u_id not in stories_by_user:
            stories_by_user[u_id] = {
                'user': story.user,
                'stories': [],
                'all_viewed': True,
                'is_self': (story.user == user)
            }
        stories_by_user[u_id]['stories'].append(story)
        if not story.is_viewed_by(user):
            stories_by_user[u_id]['all_viewed'] = False

    # Check if current user has any active story
    has_my_story = user.id in stories_by_user

    # 4. Suggested Users (up to 5 users not followed yet)
    excluded_ids = following_ids + [user.id]
    suggested_users = User.objects.filter(
        is_active=True
    ).exclude(
        id__in=excluded_ids
    ).annotate(
        followers_total=Count('follower_relations')
    ).order_by('-followers_total')[:5]

    context = {
        'posts': page_obj,
        'page_obj': page_obj,
        'stories_tray': list(stories_by_user.values()),
        'has_my_story': has_my_story,
        'suggested_users': suggested_users,
    }
    return render(request, 'feed/home.html', context)


def explore_view(request):
    # Explore shows public posts, most recent / popular
    posts_qs = Post.objects.filter(
        author__is_private=False
    ).select_related('author').prefetch_related(
        'media_items', 'likes', 'comments'
    ).order_by('-created_at')

    paginator = Paginator(posts_qs, 24)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Popular hashtags
    popular_tags = Hashtag.objects.annotate(
        num_posts=Count('posts')
    ).order_by('-num_posts')[:10]

    return render(request, 'feed/explore.html', {
        'posts': page_obj,
        'page_obj': page_obj,
        'popular_tags': popular_tags,
    })


def search_view(request):
    query = request.GET.get('q', '').strip()
    is_json = request.GET.get('format') == 'json' or request.headers.get('x-requested-with') == 'XMLHttpRequest'

    if not query:
        if is_json:
            return JsonResponse({'users': [], 'hashtags': []})
        return render(request, 'feed/search_results.html', {'query': query, 'users': [], 'posts': [], 'hashtags': []})

    # Search users
    users = User.objects.filter(
        Q(username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query)
    ).filter(is_active=True)[:10]

    # Search hashtags
    cleaned_tag = query.lstrip('#')
    hashtags = Hashtag.objects.filter(name__icontains=cleaned_tag)[:10]

    if is_json:
        user_data = [{
            'username': u.username,
            'avatar_url': u.avatar_url,
            'name': u.get_full_name() or u.username,
            'is_private': u.is_private
        } for u in users]

        tag_data = [{
            'name': h.name,
            'posts_count': h.posts.count()
        } for h in hashtags]

        return JsonResponse({'users': user_data, 'hashtags': tag_data})

    # Search posts
    posts = Post.objects.filter(
        Q(caption__icontains=query) | Q(location__icontains=query) | Q(hashtags__name__icontains=cleaned_tag)
    ).distinct().select_related('author').prefetch_related('media_items', 'likes', 'comments')

    if not request.user.is_authenticated:
        posts = posts.filter(author__is_private=False)
    else:
        following_ids = request.user.following_relations.filter(status='accepted').values_list('following_id', flat=True)
        posts = posts.filter(
            Q(author__is_private=False) | Q(author=request.user) | Q(author_id__in=following_ids)
        )

    return render(request, 'feed/search_results.html', {
        'query': query,
        'users': users,
        'hashtags': hashtags,
        'posts': posts[:30]
    })


# DRF API View for Home Feed
class FeedAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        following_ids = list(
            request.user.following_relations.filter(status='accepted').values_list('following_id', flat=True)
        )
        feed_user_ids = following_ids + [request.user.id]

        posts = Post.objects.filter(
            author_id__in=feed_user_ids
        ).select_related('author').prefetch_related(
            'media_items', 'hashtags', 'likes', 'comments'
        ).order_by('-created_at')[:30]

        serializer = PostSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)


# DRF API View for Explore
class ExploreAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        posts = Post.objects.filter(
            author__is_private=False
        ).select_related('author').prefetch_related(
            'media_items', 'hashtags', 'likes', 'comments'
        ).order_by('-created_at')[:30]

        serializer = PostSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)
