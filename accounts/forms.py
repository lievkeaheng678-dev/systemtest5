from datetime import timedelta

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import Group
from django.utils import timezone

from .models import ActivityLog, Profile

User = get_user_model()

DEFAULT_GROUP = "Member"


class SecureAuthenticationForm(AuthenticationForm):
    """Login form that temporarily locks a username after too many failures."""

    def clean(self):
        username = self.data.get("username", "")
        window = timezone.now() - timedelta(minutes=settings.LOGIN_LOCKOUT_MINUTES)
        failures = ActivityLog.objects.filter(
            username=username,
            action=ActivityLog.Action.LOGIN_FAILED,
            created_at__gte=window,
        ).count()
        if username and failures >= settings.LOGIN_MAX_FAILED_ATTEMPTS:
            raise forms.ValidationError(
                f"Too many failed attempts. Try again in {settings.LOGIN_LOCKOUT_MINUTES} minutes. "
                "ព្យាយាមចូលច្រើនដងពេក សូមរង់ចាំបន្តិច។",
                code="locked",
            )
        return super().clean()


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email")

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            group, _ = Group.objects.get_or_create(name=DEFAULT_GROUP)
            user.groups.add(group)
        return user


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("phone", "department", "bio")
        widgets = {"bio": forms.Textarea(attrs={"rows": 4})}
