from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from posts.models import Post
from notifications.models import Notification


class NotificationsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user_notif', email='u1@example.com', password='password123')
        self.sender = User.objects.create_user(username='sender_notif', email='u2@example.com', password='password123')
        self.post = Post.objects.create(author=self.user, caption='Awesome day!')
        self.client = Client()

    def test_notification_creation_and_read_state(self):
        notif = Notification.objects.create(
            recipient=self.user,
            sender=self.sender,
            notification_type='like',
            post=self.post
        )
        self.assertFalse(notif.is_read)

        self.client.login(username='user_notif', password='password123')
        response = self.client.get(reverse('notifications:list'))
        self.assertEqual(response.status_code, 200)

        notif.refresh_from_db()
        self.assertTrue(notif.is_read)
