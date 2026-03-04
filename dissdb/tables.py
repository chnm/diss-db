import django_tables2 as tables
from django_tables2.utils import A
from .models import Dissertation, CommitteeMember, Scholar


class DissTable(tables.Table):
    title = tables.Column(
        verbose_name="Dissertation Title",
        attrs={
            "th": {"class": "w-1/2"},
            "td": {"class": "whitespace-normal break-words"},
        },
    )
    author = tables.Column(
        linkify=True,
        verbose_name="Author",
        attrs={
            "th": {"class": "w-1/4"},
            "td": {"class": "text-blue-600 hover:text-blue-800"},
        },
    )
    school = tables.Column(
        verbose_name="Institution",
        attrs={"th": {"class": "w-1/6"}},
    )
    year = tables.Column(
        verbose_name="Year",
        attrs={"th": {"class": "w-1/12"}},
    )

    class Meta:
        model = Dissertation
        template_name = "django_tables2/tailwind.html"
        fields = ("title", "author", "school", "year")
        attrs = {"class": "w-full table-fixed divide-y divide-gray-200"}


class ScholarTable(tables.Table):
    name = tables.Column(
        accessor="name_full_rev",
        verbose_name="Name",
        linkify=lambda record: record.get_absolute_url(),
        order_by=("name_last", "name_first", "name_middle"),
        attrs={
            "th": {"class": "w-1/3"},
            "td": {"class": "text-blue-600 hover:text-blue-800 font-medium"},
        },
    )
    affiliation = tables.Column(
        verbose_name="Affiliation",
        attrs={
            "th": {"class": "w-1/3"},
            "td": {"class": "text-gray-700"},
        },
    )

    def render_affiliation(self, value):
        return value or "—"

    class Meta:
        model = Scholar
        template_name = "django_tables2/tailwind.html"
        fields = ("name", "affiliation")
        attrs = {"class": "w-full table-fixed divide-y divide-gray-200"}


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
