from rest_framework import serializers
from category.models import Podcast
from category.serializers import PodcastSerializer
from .models import Subscription


class SubscriptionSerializer(serializers.ModelSerializer):
    # Nested serializer to show the details of the subscribed podcast
    # Make it read-only as you don't update the podcast *via* the subscription serializer
    podcast = PodcastSerializer(read_only=True)
    # You might add a user field if needed, but typically listing a user's subscriptions
    # implies the user is already known, so it's often omitted or read-only.
    # user = UserSerializer(read_only=True)

    class Meta:
        model = Subscription
        # We include 'podcast_id' as write_only for subscribing/unsubscribing input
        # but it's not in the 'fields' for the standard read serializer output.
        fields = ('id', 'podcast', 'subscribed_at') # Fields to show in the output
        read_only_fields = ('podcast', 'subscribed_at') # These are set automatically or linked

# Serializer specifically for input when subscribing/unsubscribing
class SubscribeUnsubscribeSerializer(serializers.Serializer):
    podcast_id = serializers.PrimaryKeyRelatedField(
         queryset=Podcast.objects.all(), # Ensure the podcast exists
         write_only=True # Only for input
    )

    # Custom validation to check for duplicate subscriptions during create
    def validate(self, data):
        podcast = data['podcast_id'] # The PrimaryKeyRelatedField gives us the object
        user = self.context['request'].user # Get the authenticated user

        # Check if the user is already subscribed to this podcast
        if Subscription.objects.filter(user=user, podcast=podcast).exists():
             # Mandatory: Raise validation error for duplicate subscription
             raise serializers.ValidationError("You are already subscribed to this podcast.")

        data['podcast'] = podcast # Add the podcast object to validated data
        data['user'] = user       # Add the user object to validated data
        return data
    