from django.contrib.auth import get_user_model
from django.contrib.auth.signals import (
    user_logged_in,
    user_logged_out,
    user_login_failed,
)
from django.db.models.signals import post_save
from django.dispatch import receiver

from .logging_service import log_activity
from .models import ActivityLog, Profile

User = get_user_model()


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)


@receiver(user_logged_in)
def on_login(sender, request, user, **kwargs):
    log_activity(ActivityLog.Action.LOGIN, request=request, user=user)


@receiver(user_logged_out)
def on_logout(sender, request, user, **kwargs):
    if user is not None:
        log_activity(ActivityLog.Action.LOGOUT, request=request, user=user)


@receiver(user_login_failed)
def on_login_failed(sender, credentials, request=None, **kwargs):
    log_activity(
        ActivityLog.Action.LOGIN_FAILED,
        request=request,
        username=credentials.get("username", ""),
    )
