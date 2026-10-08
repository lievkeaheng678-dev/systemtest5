from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

# group name -> list of (app_label, codename)
GROUPS = {
    "Administrator": [
        ("auth", "add_user"), ("auth", "change_user"), ("auth", "delete_user"), ("auth", "view_user"),
        ("auth", "add_group"), ("auth", "change_group"), ("auth", "delete_group"), ("auth", "view_group"),
        ("accounts", "view_profile"), ("accounts", "change_profile"),
        ("accounts", "view_activitylog"),
    ],
    "Staff Manager": [
        ("auth", "view_user"), ("auth", "change_user"),
        ("accounts", "view_profile"),
        ("accounts", "view_activitylog"),
    ],
    "Member": [],  # normal users: can only use login-protected pages
}


class Command(BaseCommand):
    help = "Create default user groups and assign their permissions."

    def handle(self, *args, **options):
        for name, perms in GROUPS.items():
            group, created = Group.objects.get_or_create(name=name)
            objs = []
            for app_label, codename in perms:
                try:
                    objs.append(
                        Permission.objects.get(
                            content_type__app_label=app_label, codename=codename
                        )
                    )
                except Permission.DoesNotExist:
                    self.stderr.write(f"Missing permission {app_label}.{codename}")
            group.permissions.set(objs)
            self.stdout.write(
                self.style.SUCCESS(f"{'Created' if created else 'Updated'} group '{name}' ({len(objs)} permissions)")
            )
