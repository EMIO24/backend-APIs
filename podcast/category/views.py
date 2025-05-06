from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser # Permissions
from rest_framework.parsers import MultiPartParser, FormParser # To handle file uploads

from .models import Category, Podcast # Import your new models
from .serializers import CategorySerializer, PodcastSerializer # Import your new serializers

# --- Category Management (Admin Only) ---
class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    # Mandatory: Only admin users can list or create categories
    permission_classes = [IsAdminUser]

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    # Mandatory: Only admin users can retrieve, update, or delete categories
    permission_classes = [IsAdminUser]
    lookup_field = 'slug' # Use slug instead of ID in the URL


# --- Podcast Management (User Ownership) ---
class PodcastListCreateView(generics.ListCreateAPIView):
    # No queryset defined here, we'll filter it in get_queryset
    serializer_class = PodcastSerializer
    # Mandatory: Only authenticated users can list or create podcasts
    permission_classes = [IsAuthenticated]
    # Add parsers for file uploads (image)
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        """
        Optionally restricts the returned podcasts to a given user
        by filtering against a `user_id` in the URL.
        Or, for authenticated users, show only their podcasts.
        """
        queryset = Podcast.objects.all()

        # Example: Filter by user ID if provided in query params (optional)
        user_id = self.request.query_params.get('user_id', None)
        if user_id is not None:
            queryset = queryset.filter(user__id=user_id)
        # else: # Default behavior: show all podcasts to authenticated users
        #    pass # Keep queryset as all podcasts

        # You could also restrict viewing *other* users' podcasts if needed
        # e.g., return queryset.filter(user=self.request.user) # Only show current user's podcasts

        return queryset.select_related('user', 'category') # Eager load related objects

    def perform_create(self, serializer):
        # Mandatory: Set the podcast's user to the currently authenticated user
        serializer.save(user=self.request.user)


class PodcastDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Podcast.objects.all().select_related('user', 'category') # Eager load
    serializer_class = PodcastSerializer
    # Mandatory: Only authenticated users can retrieve, update, or delete podcasts
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk' # Use ID for detail view

    def get_object(self):
        """
        Ensures that a user can only update or delete their own podcasts,
        but anyone (authenticated) can retrieve any podcast.
        """
        obj = super().get_object()

        # Mandatory: Permission check for update/delete actions
        # DRF's has_object_permission is typically used for this, but doing it here for clarity
        # A more robust way is a custom permission class or overriding the perform_update/destroy
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            if obj.user != self.request.user:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("You do not have permission to edit or delete this podcast.")

        return obj

    # Alternatively, override perform_update and perform_destroy for ownership check:
    # def perform_update(self, serializer):
    #     # Check ownership before saving update
    #     if serializer.instance.user != self.request.user:
    #         from rest_framework.exceptions import PermissionDenied
    #         raise PermissionDenied("You do not have permission to edit this podcast.")
    #     serializer.save()

    # def perform_destroy(self, instance):
    #     # Check ownership before deleting
    #      if instance.user != self.request.user:
    #         from rest_framework.exceptions import PermissionDenied
    #         raise PermissionDenied("You do not have permission to delete this podcast.")
    #      instance.delete()