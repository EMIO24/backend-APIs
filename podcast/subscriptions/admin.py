from django.contrib import admin
from .models import Subscription

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'podcast', 'subscribed_at')
    list_filter = ('subscribed_at', 'podcast', 'user')
    search_fields = ('user__username', 'user__email', 'podcast__title')
    raw_id_fields = ('user', 'podcast') # Use raw IDs for FKs
    