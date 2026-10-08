from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("login/", views.SecureLoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),  # POST only (Django 5)
    path("password-change/", auth_views.PasswordChangeView.as_view(
        template_name="accounts/password_change.html",
        success_url="/profile/"), name="password_change"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("profile/", views.profile, name="profile"),
    path("security-plan/", views.security_plan, name="security_plan"),
    path("users/", views.user_list, name="user_list"),
    path("users/<int:pk>/toggle/", views.toggle_user_active, name="toggle_user_active"),
    path("activity/", views.activity_log, name="activity_log"),
]
