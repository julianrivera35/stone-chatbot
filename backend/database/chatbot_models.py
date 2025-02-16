from django.db import models
from django.utils.timezone import now, timedelta
from database.user_models import Customer



class ChatSession(models.Model):
    user = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="chat_sessions", null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now=True)

    def is_expired(self):
        return now() - self.last_active > timedelta(hours=6)

    def __str__(self):
        return f"ChatSession {self.id} - User: {self.user.email}"

class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name="messages")
    sender = models.CharField(
        max_length=10,
        choices=[
            ("user", "User"),
            ("chatbot", "Chatbot"),
        ]
    )
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.capitalize()} ({self.timestamp}): {self.text[:50]}"
