from django.db import models
from django.contrib.auth.models import User
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