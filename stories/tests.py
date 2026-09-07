from datetime import timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from accounts.models import User
from stories.models import Story, StoryView


class StoriesTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='story_user', email='story@example.com', password='password123')
        self.viewer = User.objects.create_user(username='viewer_user', email='viewer@example.com', password='password123')
        self.story = Story.objects.create(
            user=self.user,
            caption='24h snapshot',
            expires_at=timezone.now() + timedelta(hours=24)
        )
        self.client = Client()

    def test_story_expiration(self):
        self.assertTrue(self.story.is_active)
        self.story.expires_at = timezone.now() - timedelta(hours=1)
        self.story.save()
        self.assertFalse(self.story.is_active)

    def test_story_view_tracking(self):
        self.client.login(username='viewer_user', password='password123')
        response = self.client.post(
            reverse('stories:mark_viewed', kwargs={'story_id': self.story.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.story.is_viewed_by(self.viewer))
        self.assertEqual(self.story.views_count, 1)
