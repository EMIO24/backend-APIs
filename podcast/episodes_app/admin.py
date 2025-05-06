from django.contrib import admin
from .models import Episode

@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ('title', 'podcast', 'user', 'is_published', 'published_at', 'created_at')
    list_filter = ('published_at', 'podcast', 'user')
    search_fields = ('title', 'show_notes', 'podcast__title', 'user__username')
    raw_id_fields = ('podcast', 'user')
    actions = ['make_published', 'make_draft'] # Add custom actions

    fieldsets = (
        (None, {
            'fields': ('podcast', 'user', 'title', 'audio_url', 'duration', 'show_notes', 'published_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

    # Custom admin actions
    def make_published(self, request, queryset):
        now = timezone.now()
        updated_count = queryset.filter(published_at__isnull=True).update(published_at=now)
        self.message_user(request, f"{updated_count} episodes marked as published.")
    make_published.short_description = "Mark selected episodes as published now"

    def make_draft(self, request, queryset):
        updated_count = queryset.filter(published_at__isnull=False).update(published_at=None)
        self.message_user(request, f"{updated_count} episodes marked as draft.")
    make_draft.short_description = "Mark selected episodes as draft"
    