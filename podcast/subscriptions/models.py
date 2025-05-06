from django.db import models
from django.conf import settings # To link to AUTH_USER_MODEL (CustomUser)
from django.utils import timezone
from category.models import Podcast


class Subscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, # Links to the user subscribing
        on_delete=models.CASCADE, # If user is deleted, delete their subscriptions
        related_name='subscriptions' # Allows accessing user.subscriptions
    )
    podcast = models.ForeignKey(
        Podcast,
        on_delete=models.CASCADE, # If podcast is deleted, delete its subscriptions
        related_name='subscriptions' # Allows accessing podcast.subscriptions (useful for counting subscribers)
    )
    subscribed_at = models.DateTimeField(auto_now_add=True) # When the subscription occurred

    class Meta:
        # Mandatory: Prevents a user from subscribing to the same podcast more than once
        unique_together = ('user', 'podcast')
        ordering = ['-subscribed_at'] # Order by most recent subscriptions first

    def __str__(self):
        return f"{self.user.username} subscribed to {self.podcast.title}"
    