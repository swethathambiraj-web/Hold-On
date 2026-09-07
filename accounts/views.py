from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import User, Follow
from .forms import CustomUserCreationForm, ProfileEditForm
from .serializers import UserProfileSerializer, FollowSerializer, UserSummarySerializer


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('feed:home')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to Hold On, @{user.username}!")
            return redirect('feed:home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('feed:home')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next') or 'feed:home'
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('accounts:login')


@login_required
def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    is_owner = (request.user == profile_user)

    # Determine follow relationship status
    follow_relation = Follow.objects.filter(follower=request.user, following=profile_user).first()
    is_following = bool(follow_relation and follow_relation.status == 'accepted')
    is_pending = bool(follow_relation and follow_relation.status == 'pending')

    # Can view posts if public, or is owner, or accepted follower
    can_view_content = is_owner or not profile_user.is_private or is_following

    posts = profile_user.posts.all().prefetch_related('media_items', 'likes', 'comments') if can_view_content else []
    saved_posts = []
    if is_owner:
        saved_posts = [sp.post for sp in request.user.saved_posts.all().select_related('post').prefetch_related('post__media_items', 'post__likes', 'post__comments')]

    # Check pending requests if owner
    pending_requests = profile_user.follower_relations.filter(status='pending').select_related('follower') if is_owner else []

    context = {
        'profile_user': profile_user,
        'is_owner': is_owner,
        'is_following': is_following,
        'is_pending': is_pending,
        'can_view_content': can_view_content,
        'posts': posts,
        'saved_posts': saved_posts,
        'pending_requests': pending_requests,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect('accounts:profile', username=request.user.username)
    else:
        form = ProfileEditForm(instance=request.user)
    return render(request, 'accounts/edit_profile.html', {'form': form})


@login_required
@require_POST
def toggle_follow_view(request, username):
    target_user = get_object_or_404(User, username=username)
    if target_user == request.user:
        return JsonResponse({'error': 'You cannot follow yourself.'}, status=400)

    follow_relation = Follow.objects.filter(follower=request.user, following=target_user).first()

    if follow_relation:
        follow_relation.delete()
        status_result = 'unfollowed'
    else:
        if target_user.is_private:
            Follow.objects.create(follower=request.user, following=target_user, status='pending')
            status_result = 'pending'
            # Trigger notification
            try:
                from notifications.models import Notification
                Notification.objects.create(
                    recipient=target_user,
                    sender=request.user,
                    notification_type='follow_request'
                )
            except Exception:
                pass
        else:
            Follow.objects.create(follower=request.user, following=target_user, status='accepted')
            status_result = 'following'
            # Trigger notification
            try:
                from notifications.models import Notification
                Notification.objects.create(
                    recipient=target_user,
                    sender=request.user,
                    notification_type='follow'
                )
            except Exception:
                pass

    return JsonResponse({
        'status': status_result,
        'followers_count': target_user.followers_count(),
        'following_count': target_user.following_count(),
    })


@login_required
@require_POST
def handle_follow_request_view(request, follow_id, action):
    follow = get_object_or_404(Follow, id=follow_id, following=request.user, status='pending')
    if action == 'accept':
        follow.status = 'accepted'
        follow.save()
        try:
            from notifications.models import Notification
            Notification.objects.create(
                recipient=follow.follower,
                sender=request.user,
                notification_type='follow'
            )
        except Exception:
            pass
        return JsonResponse({'status': 'accepted', 'follower': follow.follower.username})
    elif action == 'deny':
        follow.delete()
        return JsonResponse({'status': 'denied'})
    return JsonResponse({'error': 'Invalid action'}, status=400)


@login_required
def followers_list_view(request, username):
    target_user = get_object_or_404(User, username=username)
    followers = [f.follower for f in target_user.follower_relations.filter(status='accepted').select_related('follower')]
    return render(request, 'accounts/user_list.html', {
        'title': f"@{target_user.username}'s Followers",
        'users_list': followers,
        'target_user': target_user
    })


@login_required
def following_list_view(request, username):
    target_user = get_object_or_404(User, username=username)
    followings = [f.following for f in target_user.following_relations.filter(status='accepted').select_related('following')]
    return render(request, 'accounts/user_list.html', {
        'title': f"Users @{target_user.username} Follows",
        'users_list': followings,
        'target_user': target_user
    })


# DRF API ViewSet
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'username'

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def toggle_follow(self, request, username=None):
        target_user = self.get_object()
        if target_user == request.user:
            return Response({'error': 'You cannot follow yourself.'}, status=status.HTTP_400_BAD_REQUEST)

        follow_relation = Follow.objects.filter(follower=request.user, following=target_user).first()
        if follow_relation:
            follow_relation.delete()
            return Response({'status': 'unfollowed', 'followers_count': target_user.followers_count()})
        else:
            if target_user.is_private:
                Follow.objects.create(follower=request.user, following=target_user, status='pending')
                return Response({'status': 'pending', 'followers_count': target_user.followers_count()})
            else:
                Follow.objects.create(follower=request.user, following=target_user, status='accepted')
                return Response({'status': 'following', 'followers_count': target_user.followers_count()})
