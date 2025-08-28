from django.contrib import admin
from .models import School, Scholar, Dissertation, CommitteeMember


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(Scholar)
class ScholarAdmin(admin.ModelAdmin):
    list_display = ("name_full_rev", "orcid", "id")
    readonly_fields = (
        "id",
        "aha_name",
        "orcid_url",
    )
    search_fields = ("name_last__startswith",)


@admin.register(Dissertation)
class DissertationAdmin(admin.ModelAdmin):
    list_display = ("main_title", "year", "author", "school")
    autocomplete_fields = (
        "author",
        "school",
    )
    search_fields = ("title",)


@admin.register(CommitteeMember)
class CommitteeMemberAdmin(admin.ModelAdmin):
    list_display = ("scholar", "dissertation")
    autocomplete_fields = (
        "scholar",
        "dissertation",
    )
