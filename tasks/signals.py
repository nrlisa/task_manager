import logging
from django.dispatch import receiver
from django.contrib.auth.signals import user_login_failed

logger = logging.getLogger(__name__)

@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, **kwargs):
    username = credentials.get('username', 'UNKNOWN')
    logger.warning(f"Security Audit: Failed login attempt for username: {username}")
