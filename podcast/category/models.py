from django.db import models
from django.conf import settings # To link to your AUTH_USER_MODEL (CustomUser)
from django.template.defaultfilters import slugify # To generate slugs
import os # To help with deleting old files

# Assuming CustomUser model from Task 1 exists and AUTH_USER_MODEL is set

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, max_length=100, blank=True) # URL-friendly identifier

    class Meta:
        verbose_name_plural = "Categories" # Fixes pluralization in admin

    def save(self, *args, **kwargs):
        # Auto-generate slug if not provided
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

def podcast_image_upload_path(instance, filename):
    """Generates upload path for podcast images."""
    # Files will be uploaded to MEDIA_ROOT/podcasts/user_<id>/<filename>
    return f'podcasts/user_{instance.user.id}/{filename}'

class Podcast(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, # Links to the creator of the podcast
        on_delete=models.CASCADE,
        related_name='podcasts' # Allows accessing user.podcasts
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL, # Don't delete podcast if category is deleted
        null=True, blank=True, # Allow podcasts to be uncategorized
        related_name='podcasts' # Allows accessing category.podcasts
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to=podcast_image_upload_path, null=True, blank=True) # Optional image
    is_featured = models.BooleanField(default=False) # Flag to mark as featured
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    # Optional: Add a method to delete the old image file when a new one is uploaded
    def save(self, *args, **kwargs):
        # Check if the instance already exists in the database
        if self.pk:
            try:
                old_instance = Podcast.objects.get(pk=self.pk)
                # Check if the image file has changed
                if old_instance.image and self.image != old_instance.image:
                    # Delete the old file
                    if os.path.exists(old_instance.image.path):
                        os.remove(old_instance.image.path)
            except Podcast.DoesNotExist:
                pass # New instance, no old file to delete

        super().save(*args, **kwargs)

    # Optional: Add a method to delete the image file when the Podcast object is deleted
    def delete(self, *args, **kwargs):
        if self.image:
            if os.path.exists(self.image.path):
                 os.remove(self.image.path)
        super().delete(*args, **kwargs)