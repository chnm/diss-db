import django_tables2 as tables
from django_tables2.utils import A
from .models import Dissertation, CommitteeMember, Scholar


class DissTable(tables.Table):
    caption = "History dissertations"

    title = tables.Column(
        verbose_name="Title",
        attrs={
            "td": {"style": "font-family: 'EB Garamond', serif; font-size: 18px; font-weight: 500; line-height: 1.3;"},
        },
        linkify=lambda record: record.author.get_absolute_url(),
    )
    author = tables.Column(
        linkify=True,
        verbose_name="Author",
        attrs={
            "td": {"style": "color: var(--accent);"},
        },
    )
    school = tables.Column(
        verbose_name="Institution",
        attrs={
            "td": {"style": "font-size: 13px; color: var(--ink2); max-width: 180px;"},
        },
    )
    year = tables.Column(
        verbose_name="Year",
        attrs={
            "td": {"style": "font-family: 'JetBrains Mono', monospace; font-size: 13px; color: var(--ink2); width: 80px;"},
        },
    )

    class Meta:
        model = Dissertation
        template_name = "django_tables2/tailwind.html"
        fields = ("year", "title", "school", "author")
        attrs = {"class": "archive-table"}
        empty_text = "No dissertations found matching your filters."


class ScholarTable(tables.Table):
    caption = "Scholars"

    name = tables.Column(
        accessor="name_full_rev",
        verbose_name="Scholar",
        linkify=lambda record: record.get_absolute_url(),
        order_by=("name_last", "name_first", "name_middle"),
        attrs={
            "td": {"style": "font-family: 'EB Garamond', serif; font-size: 18px; font-weight: 500;"},
        },
    )
    school = tables.Column(
        verbose_name="Institution",
        empty_values=(),
        orderable=False,
        attrs={
            "td": {"style": "font-size: 13px; color: var(--ink2);"},
        },
    )
    department = tables.Column(
        verbose_name="Department",
        empty_values=(),
        orderable=False,
        attrs={
            "td": {"style": "font-size: 13px; color: var(--ink2);"},
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
        attrs = {"class": "archive-table"}
        empty_text = "No scholars found matching your filters."


class ComMemTable(tables.Table):
    caption = "Committee members"

    scholar = tables.Column(
        linkify=True,
        verbose_name="Member",
        attrs={
            "td": {"style": "font-family: 'EB Garamond', serif; font-size: 19px; font-weight: 500;"},
        },
    )
    role = tables.Column(
        verbose_name="Role",
        attrs={
            "td": {"style": "font-family: 'JetBrains Mono', monospace; font-size: 11px; text-transform: uppercase; letter-spacing: 0.14em;"},
        },
    )
    dissertation = tables.Column(
        verbose_name="Dissertation",
        attrs={
            "td": {"style": "max-width: 300px; font-size: 13px;"},
        },
    )
    author = tables.Column(
        accessor="dissertation__author",
        verbose_name="Author",
        linkify=lambda record: record.dissertation.author.get_absolute_url(),
        attrs={
            "td": {"style": "color: var(--accent);"},
        },
    )

    class Meta:
        model = CommitteeMember
        template_name = "django_tables2/tailwind.html"
        fields = ("scholar", "role", "dissertation", "author")
        attrs = {"class": "archive-table"}
        empty_text = "No committee members found matching your filters."
