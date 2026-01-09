from django.contrib import admin
from .models import Task

admin.site.site_url = None  # Remove "View site" link

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    # This controls which columns are visible in the admin list view
    list_display = ('title', 'owner', 'is_completed', 'created_at')
    
    # This adds a sidebar filter for easy navigation
    list_filter = ('is_completed', 'owner', 'created_at')
    
    # This adds a search bar to the admin page
    search_fields = ('title', 'description')