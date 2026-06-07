from django.core.management.base import BaseCommand

from portal.models import WorkItem


class Command(BaseCommand):
    help = "Move user recycle-bin work older than 30 days to Admin Recycle Bin."

    def handle(self, *args, **options):
        before = WorkItem.objects.filter(status=WorkItem.STATUS_RECYCLE).count()
        WorkItem.cleanup_30_day_recycle_bin()
        after = WorkItem.objects.filter(status=WorkItem.STATUS_RECYCLE).count()
        self.stdout.write(self.style.SUCCESS(f"Cleanup complete. Moved {before - after} item(s)."))
