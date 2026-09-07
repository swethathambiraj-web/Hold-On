from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db import transaction

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Post, PostMedia, Hashtag, Like, Comment, SavedPost
from .forms import PostCreateForm, CommentForm
from .serializers import PostSerializer, CommentSerializer


@login_required
def post_create_view(request):
    if request.method == 'POST':
        form = PostCreateForm(request.POST)
        media_files = request.FILES.getlist('media_files')

        if not media_files:
            messages.error(request, "Please select at least one image or video for your post.")
            return render(request, 'posts/post_form.html', {'form': form})

        if form.is_valid():
            with transaction.atomic():
                post = form.save(commit=False)
                post.author = request.user
                post.save()

                # Process multiple media files (carousel)
                for index, file_obj in enumerate(media_files):
                    content_type = getattr(file_obj, 'content_type', '')
                    media_type = 'video' if 'video' in content_type else 'image'
                    PostMedia.objects.create(
                        post=post,
                        file=file_obj,
                        media_type=media_type,
                        order=index
                    )

                # Extract and assign hashtags
                post.extract_hashtags()

            messages.success(request, "Your post has been shared successfully!")
            return redirect('posts:post_detail', pk=post.pk)
    else:
        form = PostCreateForm()

    return render(request, 'posts/post_form.html', {'form': form})


def post_detail_view(request, pk):
    post = get_object_or_404(
        Post.objects.select_related('author').prefetch_related('media_items', 'hashtags', 'likes'),
        pk=pk
    )

    # Privacy check
    author = post.author
    if author.is_private and request.user != author:
        if not (request.user.is_authenticated and author.is_followed_by(request.user)):
            messages.warning(request, "This account is private. Follow to see their posts.")
            return redirect('accounts:profile', username=author.username)

    # Top-level comments
    comments = post.comments.filter(parent=None).select_related('user').prefetch_related(
        'replies__user'
    ).order_by('-created_at')

    comment_form = CommentForm()

    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'is_liked': post.is_liked_by(request.user) if request.user.is_authenticated else False,
        'is_saved': post.is_saved_by(request.user) if request.user.is_authenticated else False,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_edit_view(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    if request.method == 'POST':
        form = PostCreateForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save()
            post.extract_hashtags()
            messages.success(request, "Post updated successfully.")
            return redirect('posts:post_detail', pk=post.pk)
    else:
        form = PostCreateForm(instance=post)

    return render(request, 'posts/post_edit.html', {'form': form, 'post': post})


@login_required
@require_POST
def post_delete_view(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    post.delete()
    messages.success(request, "Your post has been deleted.")
    return redirect('accounts:profile', username=request.user.username)


@login_required
@require_POST
def toggle_like_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    like = Like.objects.filter(user=request.user, post=post).first()

    if like:
        like.delete()
        is_liked = False
    else:
        Like.objects.create(user=request.user, post=post)
        is_liked = True

        # Send notification to post author if not liking own post
        if post.author != request.user:
            try:
                from notifications.models import Notification
                Notification.objects.create(
                    recipient=post.author,
                    sender=request.user,
                    notification_type='like',
                    post=post
                )
            except Exception:
                pass

    return JsonResponse({
        'is_liked': is_liked,
        'likes_count': post.likes.count()
    })


@login_required
@require_POST
def toggle_save_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    saved = SavedPost.objects.filter(user=request.user, post=post).first()

    if saved:
        saved.delete()
        is_saved = False
    else:
        SavedPost.objects.create(user=request.user, post=post)
        is_saved = True

    return JsonResponse({
        'is_saved': is_saved
    })


@login_required
@require_POST
def add_comment_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    text = request.POST.get('text', '').strip()
    parent_id = request.POST.get('parent_id')

    if not text:
        return JsonResponse({'error': 'Comment text cannot be empty.'}, status=400)

    parent_comment = None
    if parent_id:
        parent_comment = Comment.objects.filter(pk=parent_id, post=post).first()

    comment = Comment.objects.create(
        user=request.user,
        post=post,
        parent=parent_comment,
        text=text
    )

    # Trigger notification
    if post.author != request.user:
        try:
            from notifications.models import Notification
            Notification.objects.create(
                recipient=post.author,
                sender=request.user,
                notification_type='comment',
                post=post,
                comment=comment
            )
        except Exception:
            pass

    return JsonResponse({
        'id': comment.id,
        'user': {
            'username': request.user.username,
            'avatar_url': request.user.avatar_url,
        },
        'text': comment.text,
        'created_at': 'Just now',
        'comments_count': post.comments.count(),
        'parent_id': parent_id,
    })


@login_required
@require_POST
def delete_comment_view(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    # Only comment owner or post owner can delete
    if request.user == comment.user or request.user == comment.post.author:
        post = comment.post
        comment.delete()
        return JsonResponse({
            'success': True,
            'comments_count': post.comments.count()
        })
    return JsonResponse({'error': 'Permission denied.'}, status=403)


def hashtag_posts_view(request, tag_name):
    hashtag = get_object_or_404(Hashtag, name=tag_name.lower())
    posts = hashtag.posts.all().select_related('author').prefetch_related('media_items', 'likes', 'comments')
    
    # Filter private users' posts if viewer is not allowed
    if not request.user.is_authenticated:
        posts = posts.filter(author__is_private=False)
    else:
        # Include public posts, own posts, or posts by followed users
        following_ids = request.user.following_relations.filter(
            status='accepted'
        ).values_list('following_id', flat=True)
        posts = posts.filter(
            models.Q(author__is_private=False) |
            models.Q(author=request.user) |
            models.Q(author_id__in=following_ids)
        )

    paginator = Paginator(posts, 18)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'posts/hashtag.html', {
        'hashtag': hashtag,
        'page_obj': page_obj,
        'posts': page_obj
    })


# DRF API ViewSets
class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        queryset = Post.objects.select_related('author').prefetch_related(
            'media_items', 'hashtags', 'likes', 'comments'
        )
        if not user.is_authenticated:
            return queryset.filter(author__is_private=False)
        following_ids = user.following_relations.filter(status='accepted').values_list('following_id', flat=True)
        return queryset.filter(
            models.Q(author__is_private=False) |
            models.Q(author=user) |
            models.Q(author_id__in=following_ids)
        )

    def perform_create(self, serializer):
        post = serializer.save(author=self.request.user)
        # Process files from request.FILES
        media_files = self.request.FILES.getlist('media_files')
        for index, file_obj in enumerate(media_files):
            content_type = getattr(file_obj, 'content_type', '')
            media_type = 'video' if 'video' in content_type else 'image'
            PostMedia.objects.create(
                post=post,
                file=file_obj,
                media_type=media_type,
                order=index
            )
        post.extract_hashtags()

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def toggle_like(self, request, pk=None):
        post = self.get_object()
        like = Like.objects.filter(user=request.user, post=post).first()
        if like:
            like.delete()
            return Response({'status': 'unliked', 'likes_count': post.likes.count()})
        else:
            Like.objects.create(user=request.user, post=post)
            if post.author != request.user:
                try:
                    from notifications.models import Notification
                    Notification.objects.create(
                        recipient=post.author,
                        sender=request.user,
                        notification_type='like',
                        post=post
                    )
                except Exception:
                    pass
            return Response({'status': 'liked', 'likes_count': post.likes.count()})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def toggle_save(self, request, pk=None):
        post = self.get_object()
        saved = SavedPost.objects.filter(user=request.user, post=post).first()
        if saved:
            saved.delete()
            return Response({'status': 'unsaved'})
        else:
            SavedPost.objects.create(user=request.user, post=post)
            return Response({'status': 'saved'})

    @action(detail=True, methods=['get', 'post'], permission_classes=[permissions.IsAuthenticatedOrReadOnly])
    def comments(self, request, pk=None):
        post = self.get_object()
        if request.method == 'POST':
            if not request.user.is_authenticated:
                return Response({'detail': 'Authentication credentials were not provided.'}, status=status.HTTP_401_UNAUTHORIZED)
            serializer = CommentSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                comment = serializer.save(user=request.user, post=post)
                if post.author != request.user:
                    try:
                        from notifications.models import Notification
                        Notification.objects.create(
                            recipient=post.author,
                            sender=request.user,
                            notification_type='comment',
                            post=post,
                            comment=comment
                        )
                    except Exception:
                        pass
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            comments = post.comments.filter(parent=None)
            serializer = CommentSerializer(comments, many=True, context={'request': request})
            return Response(serializer.data)
