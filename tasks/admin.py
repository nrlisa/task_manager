from django.contrib import admin
from .models import Task, AuditLog, AdminActionLog

admin.site.site_url = None  # Remove "View site" link

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    # This controls which columns are visible in the admin list view
    list_display = ('title', 'owner', 'is_completed', 'created_at')
    
    # This adds a sidebar filter for easy navigation
    list_filter = ('is_completed', 'owner', 'created_at')
    
    # This adds a search bar to the admin page
    search_fields = ('title', 'description')

@admin.register(AdminActionLog)
class AdminActionLogAdmin(admin.ModelAdmin):
    """Displays Django's internal 'Recent Actions' in the admin panel."""
    list_display = ('action_time', 'user', 'content_type', 'object_repr', 'action_flag', 'change_message')
    list_filter = ('action_flag', 'content_type', 'action_time')
    search_fields = ('object_repr', 'change_message', 'user__username')
    
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'get_user_info', 'action', 'ip_address', 'details')
    list_filter = ('action', 'timestamp')
    search_fields = ('user__username', 'ip_address')
    readonly_fields = ('user', 'action', 'ip_address', 'user_agent', 'details', 'timestamp')

    def get_user_info(self, obj):
        if obj.user:
            return f"{obj.user.get_full_name() or 'User'} ({obj.user.username})"
        return "Anonymous"
    get_user_info.short_description = 'User (Username)'

    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False