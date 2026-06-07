from django.urls import path

from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("home/", views.home, name="home"),
    path("services/", views.services, name="services"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("tool/<slug:tool>/", views.tool_view, name="tool"),
    path("work/<int:pk>/delete/", views.delete_work, name="delete_work"),
    path("work/<int:pk>/admin-recycle/", views.admin_recycle_work, name="admin_recycle_work"),
    path("control/", views.admin_dashboard, name="admin_dashboard"),
    path("control/send-token/", views.admin_send_token, name="admin_send_token"),
    path("control/promo/", views.admin_add_promo, name="admin_add_promo"),
]
