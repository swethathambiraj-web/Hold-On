from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User, Follow
from posts.models import Post, Hashtag


class FeedTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='feed_user', email='feed@example.com', password='password123')
        self.followed = User.objects.create_user(username='followed_user', email='followed@example.com', password='password123')
        self.stranger = User.objects.create_user(username='stranger_user', email='stranger@example.com', password='password123')

        Follow.objects.create(follower=self.user, following=self.followed, status='accepted')

        self.post1 = Post.objects.create(author=self.followed, caption='Post from followed friend #photography')
        self.post1.extract_hashtags()
        self.post2 = Post.objects.create(author=self.stranger, caption='Post from stranger')

        self.client = Client()

    def test_home_feed_view(self):
        self.client.login(username='feed_user', password='password123')
        response = self.client.get(reverse('feed:home'))
        self.assertEqual(response.status_code, 200)
        posts = list(response.context['posts'])
        self.assertIn(self.post1, posts)
        self.assertNotIn(self.post2, posts)

    def test_explore_view(self):
        response = self.client.get(reverse('feed:explore'))
        self.assertEqual(response.status_code, 200)

    def test_search_view(self):
        response = self.client.get(reverse('feed:search'), {'q': 'followed'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.followed, list(response.context['users']))
