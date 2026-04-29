import django_filters
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import F, Q
from django.db.models.functions import Greatest
from django.forms.widgets import TextInput
from django_filters import FilterSet
from django_filters.widgets import RangeWidget

from .models import (
    CommitteeMember,
    Dissertation,
    GeographicEmphasis,
    Scholar,
    ThematicEmphasis,
)


class LabeledRangeWidget(RangeWidget):
    """RangeWidget that adds distinct aria-labels to each sub-input."""

    def __init__(self, attrs=None):
        widgets = (
            TextInput(attrs={"placeholder": "YYYY", "aria-label": "Year from"}),
            TextInput(attrs={"placeholder": "YYYY", "aria-label": "Year to"}),
        )
        super(RangeWidget, self).__init__(widgets, attrs)


def _filter_name(queryset, value, prefix=""):
    """Shared fuzzy name filter. prefix is e.g. 'author__' or 'scholar__'."""
    terms = value.split()
    qs = queryset
    for term in terms:
        qs = qs.filter(
            Q(**{f"{prefix}name_first__icontains": term})
            | Q(**{f"{prefix}name_last__icontains": term})
            | Q(**{f"{prefix}name_middle__icontains": term})
        )
    return qs


class DissertationFilter(FilterSet):
    title = django_filters.CharFilter(
        label="Dissertation Title",
        method="filter_title",
        widget=TextInput(attrs={"placeholder": "Colonial Virginia"}),
    )
    author = django_filters.CharFilter(
        label="Author",
        method="filter_author",
        widget=TextInput(attrs={"placeholder": "Jane Smith"}),
    )
    school = django_filters.CharFilter(
        label="Institution",
        method="filter_school",
        widget=TextInput(attrs={"placeholder": "George Mason University"}),
    )
    year = django_filters.RangeFilter(
        field_name="year",
        widget=LabeledRangeWidget(),
    )
    thematic_emphases = django_filters.ModelMultipleChoiceFilter(
        queryset=ThematicEmphasis.objects.all(),
        field_name="thematic_emphases",
        conjoined=False,
    )
    geographic_emphases = django_filters.ModelMultipleChoiceFilter(
        queryset=GeographicEmphasis.objects.all(),
        field_name="geographic_emphases",
        conjoined=False,
    )

    def filter_title(self, queryset, name, value):
        return queryset.annotate(
            _title_sim=TrigramSimilarity("title", value),
        ).filter(Q(title__icontains=value) | Q(_title_sim__gte=0.3))

    def filter_author(self, queryset, name, value):
        return _filter_name(queryset, value, prefix="author__")

    def filter_school(self, queryset, name, value):
        return queryset.annotate(
            _school_sim=TrigramSimilarity("school__name", value),
        ).filter(Q(school__name__icontains=value) | Q(_school_sim__gte=0.3))

    class Meta:
        model = Dissertation
        fields = []


class ComMemFilter(FilterSet):
    scholar = django_filters.CharFilter(
        label="Scholar",
        method="filter_scholar",
        widget=TextInput(attrs={"placeholder": "Jane Smith"}),
    )
    dissertation = django_filters.CharFilter(
        label="Dissertation Title",
        method="filter_dissertation",
        widget=TextInput(attrs={"placeholder": "Colonial Virginia"}),
    )

    def filter_scholar(self, queryset, name, value):
        return _filter_name(queryset, value, prefix="scholar__")

    def filter_dissertation(self, queryset, name, value):
        return queryset.annotate(
            _diss_sim=TrigramSimilarity("dissertation__title", value),
        ).filter(Q(dissertation__title__icontains=value) | Q(_diss_sim__gte=0.3))

    class Meta:
        model = CommitteeMember
        fields = []


class ScholarFilter(FilterSet):
    name = django_filters.CharFilter(
        label="Name",
        method="filter_name",
        widget=TextInput(attrs={"placeholder": "Jane Smith"}),
    )
    school = django_filters.CharFilter(
        label="Dissertation Institution",
        method="filter_school",
        widget=TextInput(attrs={"placeholder": "George Mason University"}),
    )

    def filter_name(self, queryset, name, value):
        terms = value.split()
        qs = queryset
        if len(terms) == 1:
            term = terms[0]
            qs = qs.annotate(
                _name_sim=Greatest(
                    TrigramSimilarity("name_last", term),
                    TrigramSimilarity("name_first", term),
                )
            ).filter(
                Q(name_first__icontains=term)
                | Q(name_last__icontains=term)
                | Q(name_middle__icontains=term)
                | Q(_name_sim__gte=0.3)
            )
        else:
            qs = _filter_name(qs, value)
        return qs

    def filter_school(self, queryset, name, value):
        return queryset.annotate(
            _school_sim=TrigramSimilarity("dissertation__school__name", value),
        ).filter(
            Q(dissertation__school__name__icontains=value) | Q(_school_sim__gte=0.3)
        )

    @property
    def qs(self):
        qs = super().qs
        if not self.form.is_valid():
            return qs
        data = self.form.cleaned_data
        # Order by relevance when filters are active
        parts = []
        if data.get("name") and len(data["name"].split()) == 1:
            parts.append(F("_name_sim") * 3)
        if data.get("school"):
            parts.append(F("_school_sim") * 2)
        if parts:
            relevance = parts[0]
            for p in parts[1:]:
                relevance = relevance + p
            qs = qs.annotate(relevance=relevance).order_by("-relevance")
        return qs

    class Meta:
        model = Scholar
        fields = []
