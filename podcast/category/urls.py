# In your Django app's urls.py (your_podcast_app)

from django.urls import path
from .views import (
    CategoryListCreateView, CategoryDetailView,
    PodcastListCreateView, PodcastDetailView
)

urlpatterns = [
    # Category URLs (Admin Only)
    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<slug:slug>/', CategoryDetailView.as_view(), name='category-detail'), # Using slug

    # Podcast URLs (Authenticated - User Ownership for edit/delete)
    path('podcasts/', PodcastListCreateView.as_view(), name='podcast-list-create'),
    path('podcasts/<int:pk>/', PodcastDetailView.as_view(), name='podcast-detail'), # Using ID (pk)
]
