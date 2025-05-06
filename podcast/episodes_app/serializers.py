from rest_framework import serializers
from .models import Episode
# You might need serializers for related models if you want nested data
# from your_podcast_app_name.serializers import PodcastSerializer # If needed
# from your_auth_app_name.serializers import UserSerializer # If needed

class EpisodeSerializer(serializers.ModelSerializer):
    # Read-only fields to include in the output
    # user = UserSerializer(read_only=True) # Include creator details if needed
    # podcast = PodcastSerializer(read_only=True) # Include podcast details if needed

    # Writeable field to link the episode to a podcast by ID during creation
    podcast_id = serializers.PrimaryKeyRelatedField(
         queryset=Episode.objects.select_related('podcast__user').all().values_list('podcast', flat=True).distinct(), # Limit queryset to existing podcast IDs
         source='podcast', # Map this field to the 'podcast' ForeignKey
         write_only=True
    )

    # Custom field to handle the published status based on published_at
    is_published = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Episode
        fields = (
            'id', 'podcast', 'podcast_id', 'user', 'title', 'audio_url',
            'duration', 'show_notes', 'published_at', 'is_published',
            'created_at', 'updated_at'
        )
        # Mandatory: These fields are set by the system or view, not the client directly on create/update
        read_only_fields = ('user', 'podcast', 'created_at', 'updated_at', 'is_published')
        # Note: 'published_at' IS writeable initially for setting the status


    def get_is_published(self, obj):
        """Method to determine if the episode is currently published."""
        return obj.is_published() # Use the model method

    def validate(self, data):
         # Custom validation to ensure the authenticated user owns the podcast
         # this episode is being added/updated for.
         podcast = data.get('podcast') # Get the podcast object from validated data (via podcast_id)

         # This validation is crucial for both create and update operations
         if podcast and self.context['request'].user != podcast.user:
              raise serializers.ValidationError("You can only add or modify episodes for podcasts you own.")

         # Validation for setting published_at
         published_at = data.get('published_at')
         # If published_at is being set and it's in the future, that's fine (scheduled)
         # If it's being set and is in the past, it's published immediately
         # If it's being set to None, it becomes a draft

         return data

    def create(self, validated_data):
        # The user and podcast are automatically set by the view (see perform_create)
        # Ensure validated_data['user'] is the authenticated user and validated_data['podcast']
        # is the podcast related via podcast_id before saving.
        return super().create(validated_data)

    def update(self, instance, validated_data):
         # Ownership check is handled in the validate method
         return super().update(instance, validated_data)
     