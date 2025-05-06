# In episodes_app/views.py

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny # Permissions
from rest_framework.parsers import MultiPartParser, FormParser # To handle file uploads
from category.models import Podcast # Import Podcast model to get the parent object
from django.shortcuts import get_object_or_404 # To retrieve the podcast or return 404
from .models import Episode # Import Episode model
from .serializers import EpisodeSerializer # Import Episode serializer

# --- Episode Management (Linked to a Podcast - User Ownership) ---

# View to list episodes for a specific podcast and create new episodes for it
class EpisodeListCreateView(generics.ListCreateAPIView):
    serializer_class = EpisodeSerializer
    # Mandatory: Only authenticated users can create episodes
    # Listing might be public, or restricted depending on requirements.
    # Let's assume listing is public for published episodes, but creation requires auth.
    permission_classes = [IsAuthenticated] # Restrict creation to authenticated users
    # Add parsers for file uploads (audio)
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        """
        Get episodes for a specific podcast based on the podcast_pk in the URL.
        Only show published episodes to unauthenticated users.
        Show all episodes (including drafts) to the podcast owner.
        """
        podcast_pk = self.kwargs['podcast_pk'] # Get podcast_pk from URL
        podcast = get_object_or_404(Podcast.objects.select_related('user'), pk=podcast_pk) # Get the podcast object, eager load user

        # Mandatory: Filter episodes
        queryset = Episode.objects.filter(podcast=podcast).select_related('user', 'podcast') # Filter by podcast, eager load

        user = self.request.user
        # Check if the requesting user is authenticated and is the owner of the podcast
        if user.is_authenticated and user == podcast.user:
             # Owner can see all episodes (published or draft)
             return queryset
        else:
             # Non-owners (authenticated or not) only see published episodes
             return queryset.filter(published_at__isnull=False, published_at__lte=timezone.now())


    def perform_create(self, serializer):
        """
        Create a new episode and associate it with the correct podcast and user.
        """
        podcast_pk = self.kwargs['podcast_pk'] # Get podcast_pk from URL
        podcast = get_object_or_404(Podcast.objects.select_related('user'), pk=podcast_pk) # Get the podcast object, eager load user

        # Mandatory: Verify that the authenticated user owns the podcast
        if self.request.user != podcast.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only add episodes to podcasts you own.")

        # Mandatory: Set the episode's podcast and user automatically
        # The serializer's validation already checked ownership via podcast_id/podcast object
        serializer.save(podcast=podcast, user=self.request.user)


# View to retrieve, update, or delete a specific episode
class EpisodeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Episode.objects.select_related('podcast__user', 'user', 'podcast').all() # Eager load relationships
    serializer_class = EpisodeSerializer
    # Mandatory: Retrieving a *published* episode can be public. Update/Delete requires authentication and ownership.
    # We'll handle view permission in get_object or check manually.
    permission_classes = [IsAuthenticated] # Require authentication for update/delete actions

    def get_object(self):
        """
        Get the episode object and enforce permissions for update/delete.
        Allow retrieval of published episodes for anyone (if not authenticated).
        """
        # Use the default lookup field (pk) for the episode ID
        obj = super().get_object()

        # Mandatory: Permission check for update/delete actions based on ownership
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            if obj.user != self.request.user:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("You do not have permission to edit or delete this episode.")

        # Mandatory: Check if the user can view this episode (published status)
        # This is an additional check beyond IsAuthenticated
        user = self.request.user
        if not user.is_authenticated or user != obj.user:
             # If not the owner, check if it's published
             if not obj.is_published():
                 from rest_framework.exceptions import NotFound # Or PermissionDenied depending on desired visibility
                 raise NotFound("Episode not found or not published.") # Or PermissionDenied

        return obj

    # Alternative using perform_update/destroy (similar to PodcastDetailView)
    # def perform_update(self, serializer):
    #     if serializer.instance.user != self.request.user:
    #          from rest_framework.exceptions import PermissionDenied
    #          raise PermissionDenied("You do not have permission to edit this episode.")
    #     serializer.save()

    # def perform_destroy(self, instance):
    #      if instance.user != self.request.user:
    #         from rest_framework.exceptions import PermissionDenied
    #         raise PermissionDenied("You do not have permission to delete this episode.")
    #      instance.delete()
    