from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import AccessToken, PromoCode, TokenUsageLog, WorkItem
from .utils import consume_token, create_token_for_email, send_token_email


def home(request):
    return render(request, "portal/home.html")


def services(request):
    return render(request, "portal/services.html")


def about(request):
    return render(request, "portal/about.html")


def contact(request):
    return render(request, "portal/contact.html")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect("dashboard")
    return render(request, "portal/login.html", {"form": form})


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = UserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("dashboard")
    return render(request, "portal/signup.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("home")


@login_required
def dashboard(request):
    WorkItem.cleanup_30_day_recycle_bin()
    works = WorkItem.objects.filter(user=request.user).order_by("-created_at")
    promos = PromoCode.objects.filter(active=True).filter(scope=PromoCode.SCOPE_ALL)
    limited_promos = PromoCode.objects.filter(active=True, scope=PromoCode.SCOPE_LIMITED, limited_users=request.user)
    return render(
        request,
        "portal/dashboard.html",
        {
            "works": works,
            "active_count": works.filter(status=WorkItem.STATUS_ACTIVE).count(),
            "recycle_count": works.filter(status=WorkItem.STATUS_RECYCLE).count(),
            "token_count": TokenUsageLog.objects.filter(used_by=request.user).count(),
            "promos": promos | limited_promos,
        },
    )


@login_required
def tool_view(request, tool):
    titles = {
        "normal-analysis": "Normal Forest Inventory Data Analysis Report",
        "sustainable-analysis": "Sustainable Forest Inventory Data Analysis Report",
        "maps-report": "Maps Report",
        "operational-plan": "Operational Plan Report",
    }
    title = titles.get(tool, "GFC Tool")
    if request.method == "POST":
        ok, msg = consume_token(
            request.POST.get("codepass_token"),
            request.user.email,
            request.user,
            request.META.get("REMOTE_ADDR"),
        )
        if not ok:
            messages.error(request, msg)
            return redirect("tool", tool=tool)
        WorkItem.objects.create(user=request.user, tool=tool, title=title, file_name=f"{tool}.xlsx")
        messages.success(request, "Token valid भयो र काम history मा save भयो। पुरानो Flask Excel generator यहाँ जोड्न बाँकी छ।")
        return redirect("dashboard")
    return render(request, "portal/tool.html", {"tool": tool, "title": title})


@login_required
@require_POST
def delete_work(request, pk):
    work = get_object_or_404(WorkItem, pk=pk, user=request.user)
    work.move_to_recycle()
    messages.success(request, "काम Recycle Bin मा सारियो।")
    return redirect("dashboard")


@login_required
@require_POST
def admin_recycle_work(request, pk):
    work = get_object_or_404(WorkItem, pk=pk, user=request.user, status=WorkItem.STATUS_RECYCLE)
    work.move_to_admin_recycle()
    messages.success(request, "काम Admin Recycle Bin मा सुरक्षित राखियो।")
    return redirect("dashboard")


@staff_member_required
def admin_dashboard(request):
    WorkItem.cleanup_30_day_recycle_bin()
    users = User.objects.annotate(work_count=Count("workitem")).order_by("username")
    works = WorkItem.objects.select_related("user").order_by("-created_at")
    return render(
        request,
        "portal/admin_dashboard.html",
        {
            "users": users,
            "works": works,
            "admin_bin": works.filter(status=WorkItem.STATUS_ADMIN_RECYCLE),
            "token_logs": TokenUsageLog.objects.select_related("used_by")[:80],
            "tokens": AccessToken.objects.all()[:80],
            "promos": PromoCode.objects.all().order_by("-created_at"),
        },
    )


@staff_member_required
@require_POST
def admin_send_token(request):
    token = create_token_for_email(request.POST.get("email", ""))
    send_token_email(token)
    messages.success(request, f"Token generate भयो: {token.token}")
    return redirect("admin_dashboard")


@staff_member_required
@require_POST
def admin_add_promo(request):
    promo = PromoCode.objects.create(
        code=request.POST.get("code", "").upper(),
        offer_text=request.POST.get("offer_text", ""),
        scope=request.POST.get("scope", PromoCode.SCOPE_ALL),
    )
    usernames = [u.strip() for u in request.POST.get("limited_users", "").split(",") if u.strip()]
    if usernames:
        promo.limited_users.set(User.objects.filter(username__in=usernames))
    messages.success(request, "Promo code save भयो।")
    return redirect("admin_dashboard")
