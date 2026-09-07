from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User, Follow


class AccountsModelAndAuthTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='password123',
            bio='Test bio 1',
            is_private=False
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='password123',
            bio='Test bio 2',
            is_private=True
        )
        self.client = Client()

    def test_user_creation_and_attributes(self):
        self.assertEqual(self.user1.username, 'user1')
        self.assertEqual(self.user1.email, 'user1@example.com')
        self.assertEqual(self.user1.bio, 'Test bio 1')
        self.assertFalse(self.user1.is_private)
        self.assertTrue(self.user2.is_private)
        self.assertTrue(self.user1.avatar_url.startswith('https://ui-avatars.com/api/'))

    def test_follow_public_user(self):
        follow = Follow.objects.create(
            follower=self.user1,
            following=self.user2,
            status='pending'
        )
        self.assertEqual(follow.status, 'pending')
        self.assertTrue(self.user2.is_pending_follow(self.user1))
        self.assertFalse(self.user2.is_followed_by(self.user1))

        # Accept follow request
        follow.status = 'accepted'
        follow.save()
        self.assertTrue(self.user2.is_followed_by(self.user1))
        self.assertEqual(self.user2.followers_count(), 1)
        self.assertEqual(self.user1.following_count(), 1)

    def test_signup_view(self):
        response = self.client.post(reverse('accounts:signup'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'ComplexPassword123!',
            'password2': 'ComplexPassword123!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login_and_logout_views(self):
        # Login
        response = self.client.post(reverse('accounts:login'), {
            'username': 'user1',
            'password': 'password123',
        })
        self.assertEqual(response.status_code, 302)

        # Logout
        response = self.client.get(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 302)

    def test_toggle_follow_ajax(self):
        self.client.login(username='user1', password='password123')
        # User2 is private, so status becomes pending
        response = self.client.post(
            reverse('accounts:toggle_follow', kwargs={'username': 'user2'}),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'pending')

        # Toggle again to unfollow/cancel
        response = self.client.post(
            reverse('accounts:toggle_follow', kwargs={'username': 'user2'}),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'unfollowed')
