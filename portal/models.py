from datetime import timedelta

from django.conf import settings
from django.contrib.gis.db import models as gis_models
from django.db import models
from django.utils import timezone


class AccessToken(models.Model):
    token = models.CharField(max_length=32, unique=True)
    email = models.EmailField()
    used = models.BooleanField(default=False)
    used_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    used_ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.token} ({'used' if self.used else 'active'})"


class TokenUsageLog(models.Model):
    access_token = models.ForeignKey(AccessToken, null=True, blank=True, on_delete=models.SET_NULL)
    token = models.CharField(max_length=32)
    email = models.EmailField()
    used_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]


class PromoCode(models.Model):
    SCOPE_ALL = "all"
    SCOPE_LIMITED = "limited"
    SCOPE_CHOICES = [(SCOPE_ALL, "All users"), (SCOPE_LIMITED, "Limited users")]

    code = models.CharField(max_length=40, unique=True)
    offer_text = models.CharField(max_length=255)
    scope = models.CharField(max_length=12, choices=SCOPE_CHOICES, default=SCOPE_ALL)
    limited_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.code


class WorkItem(models.Model):
    STATUS_ACTIVE = "active"
    STATUS_RECYCLE = "recycle_bin"
    STATUS_ADMIN_RECYCLE = "admin_recycle_bin"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_RECYCLE, "Recycle Bin"),
        (STATUS_ADMIN_RECYCLE, "Admin Recycle Bin"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tool = models.CharField(max_length=80)
    title = models.CharField(max_length=180)
    file_name = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=24, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def move_to_recycle(self):
        self.status = self.STATUS_RECYCLE
        self.deleted_at = timezone.now()
        self.save(update_fields=["status", "deleted_at", "updated_at"])

    def move_to_admin_recycle(self):
        self.status = self.STATUS_ADMIN_RECYCLE
        self.save(update_fields=["status", "updated_at"])

    @classmethod
    def cleanup_30_day_recycle_bin(cls):
        cutoff = timezone.now() - timedelta(days=30)
        cls.objects.filter(status=cls.STATUS_RECYCLE, deleted_at__lt=cutoff).update(
            status=cls.STATUS_ADMIN_RECYCLE
        )


class ForestArea(gis_models.Model):
    name = models.CharField(max_length=180)
    forest_type = models.CharField(max_length=80, blank=True)
    district = models.CharField(max_length=120, blank=True)
    boundary = gis_models.MultiPolygonField(null=True, blank=True, srid=4326)
    center = gis_models.PointField(null=True, blank=True, srid=4326)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class ServiceLocation(gis_models.Model):
    title = models.CharField(max_length=180)
    service_type = models.CharField(max_length=120)
    location = gis_models.PointField(srid=4326)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title
