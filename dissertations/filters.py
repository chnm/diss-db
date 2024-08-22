import django_filters
from django_filters import FilterSet
from .models import Dissertation, CommitteeMember


class DissertationFilter(FilterSet):
    authorLastName = django_filters.CharFilter(
        field_name="author__name_last", lookup_expr="contains"
    )
    authorFirstName = django_filters.CharFilter(
        field_name="author__name_first", lookup_expr="contains"
    )
    year = django_filters.RangeFilter(field_name="year", lookup_expr="exact")

    class Meta:
        model = Dissertation
        fields = {"title": ["contains"], "school": ["exact"]}


class ComMemFilter(FilterSet):
    scholarLastName = django_filters.CharFilter(
        field_name="scholar__name_last", lookup_expr="exact"
    )
    scholarFirstName = django_filters.CharFilter(
        field_name="scholar__name_first", lookup_expr="exact"
    )
    dissertationTitle = django_filters.CharFilter(
        field_name="dissertation__title", lookup_expr="contains"
    )

    """class Meta:
        model = CommitteeMember
        fields = {"role": ["exact"]}"""
