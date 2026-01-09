from django.db import models
from django.contrib.auth.models import User
from django.contrib.admin.models import LogEntry
from django.core.validators import RegexValidator

class Task(models.Model):
    title = models.CharField(
        max_length=200,
        validators=[RegexValidator(r'^[a-zA-Z0-9\s\-\.\?]+$', "Only alphanumeric characters, spaces, and basic punctuation are allowed.")]
    )
    description = models.TextField()
    is_completed = models.BooleanField(default=False)
    # RBAC: Track which user owns the task to prevent IDOR 
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('failed', 'Login Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    details = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Security Event"
        verbose_name_plural = "Logging & Monitoring (Security)"
        ordering = ['-timestamp']

    def __str__(self):
        user_info = f"{self.user.username}" if self.user else "Anonymous"
        return f"{user_info} - {self.action} at {self.timestamp}"

class AdminActionLog(LogEntry):
    """Proxy model to show Recent Actions under the tasks app section."""
    class Meta:
        proxy = True
        verbose_name = "Admin Action"
        verbose_name_plural = "Logging & Monitoring (Admin Actions)"