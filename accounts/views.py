from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import (
    ProfileUpdateForm,
    RegisterForm,
    SecureAuthenticationForm,
    UserUpdateForm,
)
from .logging_service import log_activity
from .models import ActivityLog

User = get_user_model()


class SecureLoginView(LoginView):
    template_name = "registration/login.html"
    authentication_form = SecureAuthenticationForm
    redirect_authenticated_user = True


def home(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")
    return render(request, "accounts/home.html")


def register(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        log_activity(ActivityLog.Action.REGISTER, request=request, user=user)
        login(request, user)
        messages.success(request, "Account created. Welcome! / បង្កើតគណនីបានជោគជ័យ។")
        return redirect("accounts:dashboard")
    return render(request, "accounts/register.html", {"form": form})


# ------------------------------------------------------------------ Protected views
@login_required
def dashboard(request):
    user = request.user
    context = {
        "groups": user.groups.all(),
        "permission_count": len(user.get_all_permissions()),
        "session_expiry": request.session.get_expiry_date(),
        "recent_activity": ActivityLog.objects.filter(user=user)[:8],
    }
    return render(request, "accounts/dashboard.html", context)


@login_required
def profile(request):
    user_form = UserUpdateForm(request.POST or None, instance=request.user)
    profile_form = ProfileUpdateForm(request.POST or None, instance=request.user.profile)
    if request.method == "POST" and user_form.is_valid() and profile_form.is_valid():
        user_form.save()
        profile_form.save()
        log_activity(ActivityLog.Action.PROFILE_UPDATE, request=request, user=request.user)
        messages.success(request, "Profile saved. / រក្សាទុកព័ត៌មានរួចរាល់។")
        return redirect("accounts:profile")
    return render(
        request,
        "accounts/profile.html",
        {"user_form": user_form, "profile_form": profile_form},
    )


@login_required
def security_plan(request):
    return render(request, "accounts/security_plan.html")


# ------------------------------------------------------------------ Permission-protected views
@permission_required("auth.view_user", raise_exception=True)
def user_list(request):
    query = request.GET.get("q", "").strip()
    users = User.objects.prefetch_related("groups").order_by("username")
    if query:
        users = users.filter(
            Q(username__icontains=query)
            | Q(email__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
        )
    page = Paginator(users, 10).get_page(request.GET.get("page"))
    return render(request, "accounts/user_list.html", {"page": page, "query": query})


@require_POST
@permission_required("auth.change_user", raise_exception=True)
def toggle_user_active(request, pk):
    target = get_object_or_404(User, pk=pk)
    if target == request.user:
        messages.error(request, "You cannot deactivate your own account.")
    elif target.is_superuser and not request.user.is_superuser:
        messages.error(request, "Only a superuser can change a superuser.")
    else:
        target.is_active = not target.is_active
        target.save(update_fields=["is_active"])
        action = (
            ActivityLog.Action.USER_ACTIVATED
            if target.is_active
            else ActivityLog.Action.USER_DEACTIVATED
        )
        log_activity(action, request=request, user=request.user, details=f"target={target.username}")
        messages.success(
            request,
            f"{target.username} is now {'active' if target.is_active else 'inactive'}.",
        )
    return redirect("accounts:user_list")


@permission_required("accounts.view_activitylog", raise_exception=True)
def activity_log(request):
    logs = ActivityLog.objects.select_related("user")
    action = request.GET.get("action", "")
    if action:
        logs = logs.filter(action=action)
    page = Paginator(logs, 20).get_page(request.GET.get("page"))
    return render(
        request,
        "accounts/activity_log.html",
        {"page": page, "actions": ActivityLog.Action.choices, "selected": action},
    )


def permission_denied(request, exception=None):
    return render(request, "403.html", status=403)
