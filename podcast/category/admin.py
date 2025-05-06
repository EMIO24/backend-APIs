from django.contrib import admin
from .models import Category, Podcast

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)} # Auto-fill slug based on name

@admin.register(Podcast)
class PodcastAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'is_featured', 'created_at')
    list_filter = ('is_featured', 'category', 'user')
    search_fields = ('title', 'description', 'user__username', 'category__name')
    raw_id_fields = ('user', 'category') # Use raw IDs for FKs in admin for large numbers
    # Allow admin to set is_featured
    fieldsets = (
        (None, {
            'fields': ('user', 'category', 'title', 'description', 'image', 'is_featured')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',), # Hide by default
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    