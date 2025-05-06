from django.urls import path
from .views import EpisodeListCreateView, EpisodeDetailView

urlpatterns = [
    # Episodes nested under a specific podcast
    # <int:podcast_pk> captures the primary key of the podcast from the URL
    path('podcasts/<int:podcast_pk>/episodes/', EpisodeListCreateView.as_view(), name='episode-list-create'),
    path('episodes/<int:pk>/', EpisodeDetailView.as_view(), name='episode-detail'), # Detail view for a specific episode by its own ID
]