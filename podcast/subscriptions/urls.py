# In subscriptions_app/urls.py

from django.urls import path
from .views import SubscribeView, UnsubscribeView, UserSubscriptionsView

urlpatterns = [
    # Endpoint to subscribe to a podcast
    path('subscribe/', SubscribeView.as_view(), name='subscribe'),
    # Endpoint to unsubscribe from a podcast
    path('unsubscribe/', UnsubscribeView.as_view(), name='unsubscribe'),
    # Endpoint to list the authenticated user's subscriptions
    path('me/subscriptions/', UserSubscriptionsView.as_view(), name='user-subscriptions'),

    # Alternative URL structures:
    # path('podcasts/<int:podcast_pk>/subscribe/', SubscribeView.as_view(), name='subscribe'), # Subscribe via podcast ID in URL
    # path('podcasts/<int:podcast_pk>/unsubscribe/', UnsubscribeView.as_view(), name='unsubscribe'), # Unsubscribe via podcast ID in URL
    # path('subscriptions/<int:pk>/', SubscriptionDetailView.as_view(), name='subscription-detail'), # Detail view if needed, but often not
]
