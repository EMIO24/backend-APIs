from django.db import models
from django.conf import settings # To link to AUTH_USER_MODEL (CustomUser)
from django.utils import timezone
import os # To help with deleting old files
from category.models import Podcast 

def episode_audio_upload_path(instance, filename):
    """Generates upload path for episode audio."""
    # Files will be uploaded to MEDIA_ROOT/episodes/podcast_<podcast_id>/<filename>
    # Or maybe organize by user as well? Let's stick to podcast for now.
    return f'episodes/podcast_{instance.podcast.id}/{filename}'


class Episode(models.Model):
    podcast = models.ForeignKey(
        Podcast,
        on_delete=models.CASCADE, # If podcast is deleted, delete episodes
        related_name='episodes' # Allows accessing podcast.episodes
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, # Links to the creator of the episode (should match podcast user)
        on_delete=models.CASCADE,
        related_name='episodes' # Allows accessing user.episodes
    )
    title = models.CharField(max_length=200)
    audio_url = models.FileField(upload_to=episode_audio_upload_path) # Stores the audio file
    duration = models.PositiveIntegerField(null=True, blank=True) # Duration in seconds
    show_notes = models.TextField(blank=True) # Notes for the episode
    published_at = models.DateTimeField(null=True, blank=True) # Null means draft, timestamp means published
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at', '-created_at'] # Order by most recent published first

    def __str__(self):
        return f"{self.podcast.title} - {self.title}"

    def is_published(self):
        """Checks if the episode is published."""
        return self.published_at is not None and self.published_at <= timezone.now()

    # Optional: Add methods to delete the old audio file when updated/deleted
    def save(self, *args, **kwargs):
        if self.pk:
            try:
                old_instance = Episode.objects.get(pk=self.pk)
                if old_instance.audio_url and self.audio_url != old_instance.audio_url:
                     if os.path.exists(old_instance.audio_url.path):
                        os.remove(old_instance.audio_url.path)
            except Episode.DoesNotExist:
                pass
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.audio_url:
             if os.path.exists(self.audio_url.path):
                 os.remove(self.audio_url.path)
        super().delete(*args, **kwargs)
        
