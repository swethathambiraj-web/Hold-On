from django.db import models
from django.conf import settings


class Conversation(models.Model):
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='conversations'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        usernames = ", ".join([u.username for u in self.participants.all()])
        return f"Conversation ({usernames})"

    def get_other_participant(self, user):
        return self.participants.exclude(id=user.id).first()

    def last_message(self):
        return self.messages.order_by('-created_at').first()

    def unread_messages_count_for_user(self, user):
        return self.messages.filter(is_read=False).exclude(sender=user).count()


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    text = models.TextField(blank=True, verbose_name="Message Text")
    media = models.ImageField(upload_to='chat_media/', blank=True, null=True, verbose_name="Media")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Message from @{self.sender.username} in Conv {self.conversation_id}"
