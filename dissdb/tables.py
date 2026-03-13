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
        empty_text = "No dissertations found matching your filters."


class ScholarTable(tables.Table):
    name = tables.Column(
        accessor="name_full_rev",
        verbose_name="Name",
        linkify=lambda record: record.get_absolute_url(),
        order_by=("name_last", "name_first", "name_middle"),
        attrs={
            "th": {"class": "w-1/4"},
            "td": {"class": "text-blue-600 hover:text-blue-800 font-medium"},
        },
    )
    school = tables.Column(
        verbose_name="Institution",
        empty_values=(),
        orderable=False,
        attrs={
            "th": {"class": "w-1/4"},
            "td": {"class": "text-gray-700"},
        },
    )
    department = tables.Column(
        verbose_name="Department",
        empty_values=(),
        orderable=False,
        attrs={
            "th": {"class": "w-1/4"},
            "td": {"class": "text-gray-700"},
        },
    )

    def render_school(self, record):
        diss = Dissertation.objects.filter(author=record).select_related("school").first()
        return diss.school.name if diss else "—"

    def render_department(self, record):
        diss = Dissertation.objects.filter(author=record).select_related("department").first()
        return diss.department.name if diss and diss.department else "—"

    class Meta:
        model = Scholar
        template_name = "django_tables2/tailwind.html"
        fields = ("name", "school", "department")
        attrs = {"class": "w-full table-fixed divide-y divide-gray-200"}
        empty_text = "No scholars found matching your filters."


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
    author = tables.Column(
        accessor="dissertation__author",
        verbose_name="Author",
        linkify=lambda record: record.dissertation.author.get_absolute_url(),
        attrs={"td": {"class": "text-blue-600 hover:text-blue-800"}},
    )

    class Meta:
        model = CommitteeMember
        template_name = "django_tables2/tailwind.html"
        fields = ("scholar", "role", "dissertation", "author")
        attrs = {"class": "min-w-full divide-y divide-gray-200"}
        empty_text = "No committee members found matching your filters."
