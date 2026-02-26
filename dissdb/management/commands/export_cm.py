import csv
from django.core.management.base import BaseCommand
from django.db.models import Prefetch
from dissdb.models import Dissertation, CommitteeMember

class Command(BaseCommand):
    help = 'Export author-committee edge list for a specific school for network analysis'

    def add_arguments(self, parser):
        parser.add_argument('school_name', type=str)
        parser.add_argument('--output', type=str, default='network_edges.csv')

    def handle(self, *args, **options):
        dissertations = Dissertation.objects.filter(
            school__name__icontains=options['school_name']
        ).select_related(
            'author',
        ).prefetch_related(
            Prefetch(
                'committeemember_set',
                queryset=CommitteeMember.objects.select_related('scholar'),
                to_attr='committee'
            )
        ).order_by('year')

        with open(options['output'], 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['author', 'committee_member'])

            count = 0
            for d in dissertations:
                for member in d.committee:
                    writer.writerow([
                        d.author.name_full_rev,
                        member.scholar.name_full_rev,
                    ])
                    count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Exported {count} edges to {options["output"]}')
        )