# In your Django app's serializers.py

from rest_framework import serializers
from Users.serializers import UserSerializer 
from .models import Category, Podcast # Import your new models

# If models and serializers are in the same app, use:
# from .serializers import UserSerializer # Assuming it's in this file or accessible

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug')
        read_only_fields = ('slug',) # Slug is auto-generated

class PodcastSerializer(serializers.ModelSerializer):
    # Use the UserSerializer to represent the creator
    user = UserSerializer(read_only=True)
    # Use the CategorySerializer to represent the category details
    category = CategorySerializer(read_only=True)
    # Add writeable fields for setting category by ID during creation/update
    category_id = serializers.PrimaryKeyRelatedField(
         queryset=Category.objects.all(), source='category', write_only=True, allow_null=True, required=False
    )

    class Meta:
        model = Podcast
        fields = (
            'id', 'user', 'category', 'category_id', 'title',
            'description', 'image', 'is_featured', 'created_at', 'updated_at'
        )
        read_only_fields = ('user', 'created_at', 'updated_at', 'is_featured') # User, timestamps, and featured are set by the system/admin
        