import django_filters as df
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Q
from django.db.models.functions import Greatest

from dissdb.models import CommitteeMember, Dissertation, Scholar


class DissertationApiFilter(df.FilterSet):
    """Filters for /api/v1/dissertations/."""

    q = df.CharFilter(method="filter_title", label="Title search")
    year = df.NumberFilter(field_name="year")
    year_min = df.NumberFilter(field_name="year", lookup_expr="gte")
    year_max = df.NumberFilter(field_name="year", lookup_expr="lte")
    school = df.NumberFilter(field_name="school_id")
    author = df.NumberFilter(field_name="author_id")
    advisor = df.NumberFilter(method="filter_advisor")
    thematic_emphasis = df.NumberFilter(field_name="thematic_emphases__id")
    geographic_emphasis = df.NumberFilter(field_name="geographic_emphases__id")

    class Meta:
        model = Dissertation
        fields = []

    def filter_title(self, qs, name, value):
        return qs.annotate(_sim=TrigramSimilarity("title", value)).filter(
            Q(title__icontains=value) | Q(_sim__gte=0.3)
        )

    def filter_advisor(self, qs, name, value):
        chaired = CommitteeMember.objects.filter(
            role=CommitteeMember.CHAIR, scholar_id=value
        ).values_list("dissertation_id", flat=True)
        return qs.filter(id__in=chaired)


class ScholarApiFilter(df.FilterSet):
    """Filters for /api/v1/scholars/."""

    q = df.CharFilter(method="filter_name", label="Name search")
    orcid = df.CharFilter(field_name="orcid", lookup_expr="iexact")
    has_orcid = df.BooleanFilter(method="filter_has_orcid")

    class Meta:
        model = Scholar
        fields = []

    def filter_name(self, qs, name, value):
        return qs.annotate(
            _sim=Greatest(
                TrigramSimilarity("name_first", value),
                TrigramSimilarity("name_last", value),
            )
        ).filter(
            Q(name_first__icontains=value)
            | Q(name_last__icontains=value)
            | Q(name_middle__icontains=value)
            | Q(_sim__gte=0.3)
        )

    def filter_has_orcid(self, qs, name, value):
        blank = Q(orcid="") | Q(orcid__isnull=True)
        return qs.exclude(blank) if value else qs.filter(blank)
