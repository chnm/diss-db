from django.contrib import admin
from .models import School, Scholar, Dissertation


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    pass


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
    pass
