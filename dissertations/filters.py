import django_filters
from django_filters import FilterSet
from django_filters.widgets import RangeWidget
from django.forms.widgets import TextInput
from .models import Dissertation, CommitteeMember


class DissertationFilter(FilterSet):
    title = django_filters.CharFilter(
        label="Dissertation Title", field_name="title", lookup_expr="icontains", widget=TextInput(attrs={'placeholder': 'Colonial Virgina'})
    )
    authorLastName = django_filters.CharFilter(
        label="Author's Last Name", field_name="author__name_last", lookup_expr="icontains", widget=TextInput(attrs={'placeholder': 'Smith'})
    )
    authorFirstName = django_filters.CharFilter(
        label="Author's First Name", field_name="author__name_first", lookup_expr="icontains", widget=TextInput(attrs={'placeholder': 'John'})
    )
    year = django_filters.RangeFilter(field_name="year", lookup_expr="exact", widget=RangeWidget(attrs={'placeholder': 'YYYY'}))

    class Meta:
        model = Dissertation
        fields = {"school": ["exact"]}


class ComMemFilter(FilterSet):
    scholarLastName = django_filters.CharFilter(
        label="Scholar's Last Name", field_name="scholar__name_last", lookup_expr="exact", widget=TextInput(attrs={'placeholder': 'Smith'})
    )
    scholarFirstName = django_filters.CharFilter(
        label="Scholar's First Name", field_name="scholar__name_first", lookup_expr="exact", widget=TextInput(attrs={'placeholder': 'John'})
    )
    dissertationTitle = django_filters.CharFilter(
        label="Dissertation Advised", field_name="dissertation__title", lookup_expr="icontains", widget=TextInput(attrs={'placeholder': 'Colonial Virgina'})
    )


    
