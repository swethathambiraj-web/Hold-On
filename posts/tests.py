from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from accounts.models import User
from posts.models import Post, PostMedia, Hashtag, Like, Comment, SavedPost


class PostsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='poster',
            email='poster@example.com',
            password='password123'
        )
        self.user2 = User.objects.create_user(
            username='commenter',
            email='commenter@example.com',
            password='password123'
        )
        self.post = Post.objects.create(
            author=self.user,
            caption='Loving the view! #sunset #nature #travel',
            location='Malibu, CA'
        )
        self.post.extract_hashtags()

        self.client = Client()

    def test_post_creation_and_hashtags(self):
        self.assertEqual(self.post.author, self.user)
        self.assertEqual(self.post.hashtags.count(), 3)
        self.assertTrue(Hashtag.objects.filter(name='sunset').exists())
        self.assertTrue(Hashtag.objects.filter(name='nature').exists())

    def test_like_post_ajax(self):
        self.client.login(username='commenter', password='password123')
        response = self.client.post(
            reverse('posts:toggle_like', kwargs={'pk': self.post.pk}),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['is_liked'])
        self.assertEqual(response.json()['likes_count'], 1)
        self.assertTrue(self.post.is_liked_by(self.user2))

        # Unlike
        response = self.client.post(
            reverse('posts:toggle_like', kwargs={'pk': self.post.pk}),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['is_liked'])
        self.assertEqual(response.json()['likes_count'], 0)

    def test_comment_ajax(self):
        self.client.login(username='commenter', password='password123')
        response = self.client.post(
            reverse('posts:add_comment', kwargs={'pk': self.post.pk}),
            {'text': 'Great photo!'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.post.comments.count(), 1)
        self.assertEqual(self.post.comments.first().text, 'Great photo!')

    def test_save_post_ajax(self):
        self.client.login(username='commenter', password='password123')
        response = self.client.post(
            reverse('posts:toggle_save', kwargs={'pk': self.post.pk}),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['is_saved'])
        self.assertTrue(self.post.is_saved_by(self.user2))
