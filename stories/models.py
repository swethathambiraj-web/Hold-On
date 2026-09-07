from datetime import timedelta
from django.db import models
from django.conf import settings
from django.utils import timezone


def get_default_expires_at():
    return timezone.now() + timedelta(hours=24)


class Story(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='stories'
    )
    media = models.ImageField(upload_to='stories/', verbose_name="Story Media")
    caption = models.CharField(max_length=200, blank=True, verbose_name="Caption")
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=get_default_expires_at)

    class Meta:
        ordering = ['created_at']
        verbose_name_plural = 'Stories'

    def __str__(self):
        return f"Story by @{self.user.username} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"

    @property
    def is_active(self):
        return timezone.now() < self.expires_at

    @property
    def views_count(self):
        return self.views.count()

    def is_viewed_by(self, user):
        if not user or not user.is_authenticated:
            return False
        return self.views.filter(viewer=user).exists()


class StoryView(models.Model):
    story = models.ForeignKey(
        Story,
        on_delete=models.CASCADE,
        related_name='views'
    )
    viewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='viewed_stories'
    )
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('story', 'viewer')
        ordering = ['-viewed_at']

    def __str__(self):
        return f"@{self.viewer.username} viewed Story {self.story_id}"
