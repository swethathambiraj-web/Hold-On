import re
from django.db import models
from django.conf import settings
from django.urls import reverse


class Post(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    caption = models.TextField(blank=True, verbose_name="Caption")
    location = models.CharField(max_length=150, blank=True, verbose_name="Location")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Post by @{self.author.username} on {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    def get_absolute_url(self):
        return reverse('posts:post_detail', kwargs={'pk': self.pk})

    @property
    def likes_count(self):
        return self.likes.count()

    @property
    def comments_count(self):
        return self.comments.count()

    def is_liked_by(self, user):
        if not user or not user.is_authenticated:
            return False
        return self.likes.filter(user=user).exists()

    def is_saved_by(self, user):
        if not user or not user.is_authenticated:
            return False
        return self.saved_by.filter(user=user).exists()

    def extract_hashtags(self):
        """Extracts hashtags starting with # from the caption."""
        tag_names = set(re.findall(r'#(\w+)', self.caption))
        for name in tag_names:
            hashtag, _ = Hashtag.objects.get_or_create(name=name.lower())
            self.hashtags.add(hashtag)


class PostMedia(models.Model):
    MEDIA_TYPE_CHOICES = (
        ('image', 'Image'),
        ('video', 'Video'),
    )

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='media_items'
    )
    file = models.FileField(upload_to='post_media/', verbose_name="Media File")
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES, default='image')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"Media {self.order} for Post {self.post_id}"


class Hashtag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    posts = models.ManyToManyField(Post, related_name='hashtags', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"#{self.name}"

    @property
    def posts_count(self):
        return self.posts.count()


class Like(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')
        ordering = ['-created_at']

    def __str__(self):
        return f"@{self.user.username} liked Post {self.post_id}"


class Comment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )
    text = models.TextField(max_length=1000, verbose_name="Comment Text")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by @{self.user.username} on Post {self.post_id}"


class SavedPost(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='saved_posts'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='saved_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')
        ordering = ['-created_at']

    def __str__(self):
        return f"@{self.user.username} saved Post {self.post_id}"
