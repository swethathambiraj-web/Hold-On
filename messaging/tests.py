from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from messaging.models import Conversation, Message


class MessagingTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='chat1', email='chat1@example.com', password='password123')
        self.user2 = User.objects.create_user(username='chat2', email='chat2@example.com', password='password123')
        self.client = Client()

    def test_start_conversation_and_send_message(self):
        self.client.login(username='chat1', password='password123')

        # Start conversation
        response = self.client.get(reverse('messaging:start_conversation', kwargs={'username': 'chat2'}))
        self.assertEqual(response.status_code, 302)

        conversation = Conversation.objects.filter(participants=self.user1).filter(participants=self.user2).first()
        self.assertIsNotNone(conversation)

        # Send Message
        response = self.client.post(
            reverse('messaging:send_message', kwargs={'conversation_id': conversation.id}),
            {'text': 'Hello world!'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(conversation.messages.count(), 1)
        self.assertEqual(conversation.messages.first().text, 'Hello world!')
