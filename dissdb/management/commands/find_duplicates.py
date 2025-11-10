import re
from difflib import SequenceMatcher

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

from dissdb.models import DuplicateCandidate, Scholar


class Command(BaseCommand):
    help = "Find duplicate scholars using simple name similarity"

    def add_arguments(self, parser):
        parser.add_argument(
            "--threshold",
            type=float,
            default=0.9,
            help="Similarity threshold for duplicate detection (0.0-1.0, default: 0.9)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Don't save results to database, just show what would be found",
        )
        parser.add_argument(
            "--limit",
            type=int,
            help="Limit number of scholars to process (for testing)",
        )

    def normalize_name(self, name):
        """Normalize names for comparison"""
        if not name:
            return ""
        # Convert to lowercase, remove punctuation, collapse whitespace
        name = re.sub(r"[^\w\s]", " ", name.lower())
        name = re.sub(r"\s+", " ", name).strip()
        return name

    def check_middle_name_similarity(self, middle1, middle2):
        """Check similarity between middle names, including abbreviated forms"""
        if not middle1 or not middle2:
            # If one has middle name and other doesn't, neutral score
            return 0.5 if (middle1 or middle2) else 1.0

        middle1_norm = self.normalize_name(middle1)
        middle2_norm = self.normalize_name(middle2)

        # Direct match
        if middle1_norm == middle2_norm:
            return 1.0

        # Check if one is initial of the other
        if len(middle1_norm) == 1 and middle2_norm.startswith(middle1_norm):
            return 0.9
        if len(middle2_norm) == 1 and middle1_norm.startswith(middle2_norm):
            return 0.9

        # Check if both are initials and match
        if len(middle1_norm) == 1 and len(middle2_norm) == 1:
            return 1.0 if middle1_norm == middle2_norm else 0.0

        # Regular string similarity for full middle names
        return SequenceMatcher(None, middle1_norm, middle2_norm).ratio()

    def calculate_similarity(self, scholar1, scholar2):
        """Calculate similarity score between two scholars"""
        scores = []

        # Compare full names
        name1 = self.normalize_name(scholar1.name_full)
        name2 = self.normalize_name(scholar2.name_full)
        scores.append(SequenceMatcher(None, name1, name2).ratio())

        # Compare last names (weighted more heavily)
        last1 = self.normalize_name(scholar1.name_last)
        last2 = self.normalize_name(scholar2.name_last)
        last_score = SequenceMatcher(None, last1, last2).ratio()
        scores.extend([last_score, last_score])  # Weight it double

        # Compare first names
        first1 = self.normalize_name(scholar1.name_first)
        first2 = self.normalize_name(scholar2.name_first)
        first_score = SequenceMatcher(None, first1, first2).ratio()

        scores.append(first_score)

        # Compare middle names
        middle_score = self.check_middle_name_similarity(
            scholar1.name_middle, scholar2.name_middle
        )
        scores.append(middle_score)

        # Compare AHA names if available
        if scholar1.aha_name and scholar2.aha_name:
            aha1 = self.normalize_name(scholar1.aha_name)
            aha2 = self.normalize_name(scholar2.aha_name)
            scores.append(SequenceMatcher(None, aha1, aha2).ratio())

        return sum(scores) / len(scores)

    def handle(self, *args, **options):
        self.stdout.write("Starting duplicate detection for scholars...")

        # Get scholars if names exist
        scholars = Scholar.objects.filter(
            name_first__isnull=False, name_last__isnull=False
        ).exclude(Q(name_first="") | Q(name_last=""))

        if options.get("limit"):
            scholars = scholars[: options["limit"]]

        if not scholars.exists():
            raise CommandError("No scholars with valid names found")

        scholars_list = list(scholars)
        total_scholars = len(scholars_list)
        self.stdout.write(f"Processing {total_scholars} scholars")

        threshold = options["threshold"]
        duplicates_found = 0

        if options["dry_run"]:
            self.stdout.write("\nDRY RUN - No changes will be saved to database\n")

        # Compare each scholar with every other scholar
        for i in range(total_scholars):
            scholar1 = scholars_list[i]

            # Show progress every 1000 scholars
            if i % 1000 == 0:
                self.stdout.write(
                    f"Progress: {i}/{total_scholars} ({i / total_scholars * 100:.1f}%)"
                )

            for j in range(i + 1, total_scholars):
                scholar2 = scholars_list[j]

                # Quick check: if last names are too different, skip
                if not scholar1.name_last or not scholar2.name_last:
                    continue

                last_similarity = SequenceMatcher(
                    None,
                    self.normalize_name(scholar1.name_last),
                    self.normalize_name(scholar2.name_last),
                ).ratio()

                # Only do full comparison if last names are somewhat similar
                if last_similarity < 0.6:
                    continue

                similarity = self.calculate_similarity(scholar1, scholar2)

                if similarity >= threshold:
                    self.stdout.write(
                        f"\nPotential duplicate (similarity: {similarity:.3f}):"
                    )
                    self.stdout.write(f"  {scholar1.name_full} (ID: {scholar1.id})")
                    self.stdout.write(f"  {scholar2.name_full} (ID: {scholar2.id})")

                    if not options["dry_run"]:
                        # Save to database (avoid duplicates)
                        duplicate_candidate, created = (
                            DuplicateCandidate.objects.get_or_create(
                                scholar_1=scholar1,
                                scholar_2=scholar2,
                                defaults={
                                    "confidence_score": similarity,
                                    "reviewed": False,
                                },
                            )
                        )

                        if created:
                            duplicates_found += 1
                            self.stdout.write(
                                self.style.SUCCESS("    → Saved duplicate candidate")
                            )
                        else:
                            self.stdout.write(
                                self.style.WARNING("    → Already exists in database")
                            )
                    else:
                        duplicates_found += 1

        if options["dry_run"]:
            self.stdout.write(
                f"\nDRY RUN COMPLETE: Found {duplicates_found} potential duplicate pairs"
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\nCompleted! Found and saved {duplicates_found} new potential duplicate pairs."
                )
            )
            self.stdout.write(
                "Review duplicates in Django admin or create a view to manually verify them."
            )
