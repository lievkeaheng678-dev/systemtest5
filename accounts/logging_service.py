from .models import ActivityLog
from .utils import get_client_ip, get_user_agent


def log_activity(action, request=None, user=None, username="", details=""):
    if user is not None and not username:
        username = user.get_username()
    ActivityLog.objects.create(
        user=user if getattr(user, "pk", None) else None,
        username=username or "",
        action=action,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        details=details[:255],
    )
