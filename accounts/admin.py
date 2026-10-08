from django.contrib import admin, messages
from django.contrib.admin.sites import NotRegistered
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.utils import timezone

from .models import ActivityLog, Profile

User = get_user_model()

# ---------------------------------------------------------------- Branding
admin.site.site_header = "ប្រព័ន្ធគ្រប់គ្រង | Administration & Identity Management"
admin.site.site_title = "Identity Admin"
admin.site.index_title = "ផ្ទាំងគ្រប់គ្រង / Dashboard"


# ---------------------------------------------------------------- User admin
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    extra = 0


try:
    admin.site.unregister(User)
except NotRegistered:
    pass


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = [ProfileInline]
    list_display = (
        "username", "email", "first_name", "last_name",
        "group_list", "is_staff", "is_active", "last_login",
    )
    list_filter = ("is_active", "is_staff", "is_superuser", "groups")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("username",)
    actions = ["activate_users", "deactivate_users"]

    @admin.display(description="Groups")
    def group_list(self, obj):
        return ", ".join(g.name for g in obj.groups.all()) or "-"

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("groups")

    @admin.action(description="Activate selected users")
    def activate_users(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f"{count} user(s) activated.", messages.SUCCESS)

    @admin.action(description="Deactivate selected users")
    def deactivate_users(self, request, queryset):
        queryset = queryset.exclude(pk=request.user.pk)  # never lock yourself out
        count = queryset.update(is_active=False)
        self.message_user(request, f"{count} user(s) deactivated.", messages.WARNING)


# ---------------------------------------------------------------- Group admin (permissions)
try:
    admin.site.unregister(Group)
except NotRegistered:
    pass


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("name", "member_count", "permission_count")
    search_fields = ("name",)
    filter_horizontal = ("permissions",)

    @admin.display(description="Members")
    def member_count(self, obj):
        return obj.user_set.count()

    @admin.display(description="Permissions")
    def permission_count(self, obj):
        return obj.permissions.count()


# ---------------------------------------------------------------- Profile & audit log
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "department", "phone", "created_at")
    search_fields = ("user__username", "department", "phone")
    list_select_related = ("user",)


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    """Audit trail: read-only so entries cannot be tampered with."""

    list_display = ("created_at", "username", "action", "ip_address", "details")
    list_filter = ("action", "created_at")
    search_fields = ("username", "ip_address", "details")
    date_hierarchy = "created_at"
    readonly_fields = [f.name for f in ActivityLog._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


# ---------------------------------------------------------------- Dashboard statistics
_original_index = admin.site.index


def _index_with_stats(request, extra_context=None):
    today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    extra_context = extra_context or {}
    extra_context["stats"] = {
        "total_users": User.objects.count(),
        "active_users": User.objects.filter(is_active=True).count(),
        "staff_users": User.objects.filter(is_staff=True).count(),
        "groups": Group.objects.count(),
        "logins_today": ActivityLog.objects.filter(
            action=ActivityLog.Action.LOGIN, created_at__gte=today
        ).count(),
        "failed_today": ActivityLog.objects.filter(
            action=ActivityLog.Action.LOGIN_FAILED, created_at__gte=today
        ).count(),
    }
    return _original_index(request, extra_context)


admin.site.index = _index_with_stats
