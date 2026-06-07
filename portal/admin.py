from django.contrib import admin

try:
    from django.contrib.gis.admin import GISModelAdmin
except Exception:
    GISModelAdmin = admin.ModelAdmin

from .models import AccessToken, ForestArea, PromoCode, ServiceLocation, TokenUsageLog, WorkItem


@admin.register(AccessToken)
class AccessTokenAdmin(admin.ModelAdmin):
    list_display = ("token", "email", "used", "used_by", "used_at", "created_at")
    search_fields = ("token", "email", "used_by__username")
    list_filter = ("used", "created_at")


@admin.register(TokenUsageLog)
class TokenUsageLogAdmin(admin.ModelAdmin):
    list_display = ("token", "email", "used_by", "ip_address", "created_at")
    search_fields = ("token", "email", "used_by__username")


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ("code", "offer_text", "scope", "active", "created_at")
    filter_horizontal = ("limited_users",)
    list_filter = ("scope", "active")


@admin.register(WorkItem)
class WorkItemAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "tool", "status", "created_at", "deleted_at")
    search_fields = ("title", "user__username", "tool", "file_name")
    list_filter = ("status", "tool", "created_at")


@admin.register(ForestArea)
class ForestAreaAdmin(GISModelAdmin):
    list_display = ("name", "forest_type", "district", "created_at")
    search_fields = ("name", "district", "forest_type")


@admin.register(ServiceLocation)
class ServiceLocationAdmin(GISModelAdmin):
    list_display = ("title", "service_type", "created_at")
    search_fields = ("title", "service_type")
