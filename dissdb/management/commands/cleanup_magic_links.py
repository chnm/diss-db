from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from dissdb.models import AccountRequest, MagicLink


class Command(BaseCommand):
    help = "Delete expired/used magic link tokens and stale pending account requests."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be deleted without actually deleting.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        # Magic links: expired or used
        ml_qs = MagicLink.objects.filter(
            used=True,
        ) | MagicLink.objects.filter(
            expires_at__lt=timezone.now(),
        )
        ml_count = ml_qs.count()

        # Account requests: pending and older than 7 days
        stale_cutoff = timezone.now() - timedelta(days=7)
        ar_qs = AccountRequest.objects.filter(
            status=AccountRequest.PENDING,
            created_at__lt=stale_cutoff,
        )
        ar_count = ar_qs.count()

        if dry_run:
            self.stdout.write(f"Would delete {ml_count} magic link(s).")
            self.stdout.write(f"Would delete {ar_count} stale account request(s).")
        else:
            ml_qs.delete()
            ar_qs.delete()
            self.stdout.write(self.style.SUCCESS(f"Deleted {ml_count} magic link(s)."))
            self.stdout.write(
                self.style.SUCCESS(f"Deleted {ar_count} stale account request(s).")
            )
