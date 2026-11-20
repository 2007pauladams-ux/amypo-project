from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'avatar_color', 'created_at', 'updated_at')
    search_fields = ('user__username', 'user__email', 'bio')
    filter_horizontal = ('preferred_categories',)
