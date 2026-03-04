from django import forms
from django.forms import inlineformset_factory

from .models import CommitteeMember, Dissertation, DissertationLink, Scholar, ScholarWebsite

INPUT_CLASSES = "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
TEXTAREA_CLASSES = "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
SELECT_CLASSES = "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"


class ScholarForm(forms.ModelForm):
    class Meta:
        model = Scholar
        fields = ["name_first", "name_middle", "name_last", "name_suffix", "orcid", "affiliation"]
        widgets = {
            "name_first": forms.TextInput(attrs={"class": INPUT_CLASSES}),
            "name_middle": forms.TextInput(attrs={"class": INPUT_CLASSES}),
            "name_last": forms.TextInput(attrs={"class": INPUT_CLASSES}),
            "name_suffix": forms.TextInput(attrs={"class": INPUT_CLASSES}),
            "orcid": forms.TextInput(attrs={"class": INPUT_CLASSES, "placeholder": "0000-0000-0000-0000"}),
            "affiliation": forms.TextInput(attrs={"class": INPUT_CLASSES}),
        }


ScholarWebsiteFormSet = inlineformset_factory(
    Scholar,
    ScholarWebsite,
    fields=["website_type", "url", "label"],
    extra=1,
    can_delete=True,
    widgets={
        "website_type": forms.Select(attrs={"class": SELECT_CLASSES}),
        "url": forms.URLInput(attrs={"class": INPUT_CLASSES}),
        "label": forms.TextInput(attrs={"class": INPUT_CLASSES, "placeholder": "Optional display label"}),
    },
)


class DissertationForm(forms.ModelForm):
    class Meta:
        model = Dissertation
        fields = ["title", "year", "school", "abstract"]
        widgets = {
            "title": forms.TextInput(attrs={"class": INPUT_CLASSES}),
            "year": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "school": forms.Select(attrs={"class": SELECT_CLASSES}),
            "abstract": forms.Textarea(attrs={"class": TEXTAREA_CLASSES, "rows": 6}),
        }


CommitteeMemberFormSet = inlineformset_factory(
    Dissertation,
    CommitteeMember,
    fields=["scholar", "role"],
    extra=1,
    can_delete=True,
    widgets={
        "scholar": forms.HiddenInput(),
        "role": forms.Select(attrs={"class": SELECT_CLASSES}),
    },
)


DissertationLinkFormSet = inlineformset_factory(
    Dissertation,
    DissertationLink,
    fields=["link_type", "url", "label"],
    extra=1,
    can_delete=True,
    widgets={
        "link_type": forms.Select(attrs={"class": SELECT_CLASSES}),
        "url": forms.URLInput(attrs={"class": INPUT_CLASSES}),
        "label": forms.TextInput(attrs={"class": INPUT_CLASSES, "placeholder": "Optional display label"}),
    },
)