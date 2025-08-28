import django_tables2 as tables
from django_tables2.utils import A
from .models import Dissertation, CommitteeMember, Scholar


class DissTable(tables.Table):
    title = tables.Column(
        linkify=True,
        verbose_name="Dissertation Title",
        attrs={"td": {"class": "font-medium text-blue-600 hover:text-blue-800"}}
    )
    author = tables.Column(
        linkify=True,
        verbose_name="Author",
        attrs={"td": {"class": "text-blue-600 hover:text-blue-800"}}
    )
    school = tables.Column(verbose_name="Institution")
    year = tables.Column(verbose_name="Year")

    class Meta:
        model = Dissertation
        template_name = "django_tables2/tailwind.html"
        fields = ("title", "author", "school", "year")
        attrs = {"class": "min-w-full divide-y divide-gray-200"}


class ComMemTable(tables.Table):
    scholar = tables.Column(
        linkify=True,
        verbose_name="Scholar",
        attrs={"td": {"class": "text-blue-600 hover:text-blue-800"}}
    )
    role = tables.Column(verbose_name="Role")
    dissertation = tables.Column(
        verbose_name="Dissertation",
        attrs={"td": {"class": "max-w-xs truncate"}}
    )

    class Meta:
        model = CommitteeMember
        template_name = "django_tables2/tailwind.html"
        fields = ("scholar", "role", "dissertation")
        attrs = {"class": "min-w-full divide-y divide-gray-200"}
