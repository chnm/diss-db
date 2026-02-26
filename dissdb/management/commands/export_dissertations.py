import csv
from django.core.management.base import BaseCommand
from django.db.models import Prefetch
from dissdb.models import Dissertation, CommitteeMember

class Command(BaseCommand):
    help = 'Export dissertations with advisor info for a specific school'

    def add_arguments(self, parser):
        parser.add_argument('school_name', type=str)
        parser.add_argument('--output', type=str, default='dissertations.csv')

    def handle(self, *args, **options):
        dissertations = Dissertation.objects.filter(
            school__name__icontains=options['school_name']
        ).select_related(
            'author',
            'school',
        ).prefetch_related(
            Prefetch(
                'committeemember_set',
                queryset=CommitteeMember.objects.filter(
                    role=CommitteeMember.CHAIR
                ).select_related('scholar'),
                to_attr='chairs'
            )
        ).order_by('year')

        with open(options['output'], 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Author',
                'Advisor',
                'Dissertation Title',
                'Year',
                'School',
            ])

            count = 0
            for d in dissertations:
                advisor = d.chairs[0].scholar.name_full_rev if d.chairs else 'No advisor on record'
                writer.writerow([
                    d.author.name_full_rev,
                    advisor,
                    d.title,
                    d.year,
                ])
                count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Exported {count} records to {options["output"]}')
        )