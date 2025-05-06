# In subscriptions_app/views.py

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated # Permissions
from category.models import Podcast # Import Podcast model
from django.shortcuts import get_object_or_404 # For retrieving objects
from .models import Subscription
from .serializers import SubscriptionSerializer, SubscribeUnsubscribeSerializer # Import your serializers

# --- Subscribe to a Podcast ---
class SubscribeView(APIView):
    # Mandatory: Only authenticated users can subscribe
    permission_classes = [IsAuthenticated]
    serializer_class = SubscribeUnsubscribeSerializer # Use this for input validation

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request}) # Pass request context
        serializer.is_valid(raise_exception=True) # Validation includes duplicate check

        podcast = serializer.validated_data['podcast'] # Get podcast object from validated data
        user = serializer.validated_data['user']       # Get user object from validated data

        # Mandatory: Create the subscription
        subscription = Subscription.objects.create(user=user, podcast=podcast)

        # Optionally, return the created subscription details
        # subscription_serializer = SubscriptionSerializer(subscription)
        # return Response(subscription_serializer.data, status=status.HTTP_201_CREATED)

        return Response({'detail': f'Successfully subscribed to {podcast.title}.'}, status=status.HTTP_201_CREATED)


# --- Unsubscribe from a Podcast ---
class UnsubscribeView(APIView):
    # Mandatory: Only authenticated users can unsubscribe
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs): # Using POST for unsubscribe is common for APIs
         podcast_id = request.data.get('podcast_id') # Get podcast_id from request body

         if not podcast_id:
             return Response({'detail': 'podcast_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

         user = request.user # Authenticated user

         # Mandatory: Find the subscription to delete
         try:
             subscription = Subscription.objects.get(user=user, podcast__id=podcast_id) # Use podcast__id for lookup
         except Subscription.DoesNotExist:
             # Mandatory: Return error if subscription doesn't exist
             return Response({'detail': 'You are not subscribed to this podcast.'}, status=status.HTTP_404_NOT_FOUND)

         # Mandatory: Delete the subscription
         subscription.delete()

         # Get the podcast title for the response (optional)
         try:
             podcast_title = Podcast.objects.get(id=podcast_id).title
         except Podcast.DoesNotExist:
             podcast_title = 'the podcast' # Fallback

         return Response({'detail': f'Successfully unsubscribed from {podcast_title}.'}, status=status.HTTP_200_OK)

    # Alternatively, use DELETE method targeting /subscriptions/{podcast_id}
    # def delete(self, request, podcast_id, *args, **kwargs):
    #    # ... same logic as above, get podcast_id from URL kwargs['podcast_id'] ...


# --- List User's Subscriptions ---
# Using RetrieveAPIView for a single user's subscriptions
class UserSubscriptionsView(generics.ListAPIView):
    serializer_class = SubscriptionSerializer
    # Mandatory: Only authenticated users can view their subscriptions
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return a list of subscriptions for the currently authenticated user.
        """
        user = self.request.user
        # Mandatory: Filter subscriptions by the authenticated user
        # Use select_related to eager load podcast details for the serializer
        queryset = Subscription.objects.filter(user=user).select_related('podcast')
        return queryset

    # We don't need perform_create, perform_update, perform_destroy here
    # as this view is only for listing.
    