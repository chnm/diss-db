import django_tables2 as tables
from django_tables2.utils import A
from .models import Dissertation, CommitteeMember, Scholar


class DissTable(tables.Table):
    title = tables.Column(linkify=True)
    author = tables.Column(linkify=True)

    class Meta:
        model = Dissertation
        template_name = "django_tables2/bootstrap5.html"
        fields = (
            "title",
            "author",
            "school",
            "year",
        )


class ComMemTable(tables.Table):
    scholar = tables.Column(linkify=True)

    class Meta:
        model = CommitteeMember
        template_name = "django_tables2/bootstrap5.html"
        fields = (
            "scholar",
            "role",
            "dissertation",
        )
