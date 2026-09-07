from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom User model for Hold On social media platform."""
    email = models.EmailField(unique=True, verbose_name="Email Address")
    bio = models.TextField(max_length=500, blank=True, verbose_name="Bio")
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        blank=True,
        null=True,
        verbose_name="Profile Picture"
    )
    website_link = models.URLField(max_length=255, blank=True, verbose_name="Website")
    is_private = models.BooleanField(
        default=False,
        verbose_name="Private Account",
        help_text="If enabled, users must request to follow you."
    )

    class Meta:
        ordering = ['username']

    def __str__(self):
        return self.username

    @property
    def avatar_url(self):
        """Returns uploaded profile picture or a placeholder avatar."""
        if self.profile_picture and hasattr(self.profile_picture, 'url'):
            try:
                return self.profile_picture.url
            except Exception:
                pass
        # Generates a clean avatar using UI Avatars service based on username
        return f"https://ui-avatars.com/api/?name={self.username}&background=262626&color=ffffff&bold=true&size=150"

    def followers_count(self):
        return self.follower_relations.filter(status='accepted').count()

    def following_count(self):
        return self.following_relations.filter(status='accepted').count()

    def posts_count(self):
        return self.posts.count()

    def is_followed_by(self, user):
        """Checks if a given user is an accepted follower."""
        if not user or not user.is_authenticated:
            return False
        return self.follower_relations.filter(follower=user, status='accepted').exists()

    def is_pending_follow(self, user):
        """Checks if a follow request is pending from given user."""
        if not user or not user.is_authenticated:
            return False
        return self.follower_relations.filter(follower=user, status='pending').exists()


class Follow(models.Model):
    """
    Follow relationship supporting public instant-follow and private account requests.
    """
    STATUS_CHOICES = (
        ('pending', 'Pending Approval'),
        ('accepted', 'Accepted'),
    )

    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following_relations'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower_relations'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='accepted'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')
        indexes = [
            models.Index(fields=['follower', 'status']),
            models.Index(fields=['following', 'status']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.follower.username} -> {self.following.username} ({self.status})"
