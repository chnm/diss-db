from django import template

register = template.Library()


@register.simple_tag
def site_counts():
    from django.db.models import Max, Min

    from dissdb.models import CommitteeMember, Dissertation, Scholar

    diss_count = Dissertation.objects.count()
    scholar_count = Scholar.objects.count()
    advisor_count = (
        CommitteeMember.objects.filter(role="chair")
        .values("scholar")
        .distinct()
        .count()
    )
    institution_count = Dissertation.objects.values("school").distinct().count()
    coverage = Dissertation.objects.aggregate(
        first_year=Min("year"),
        last_year=Max("year"),
    )
    return {
        "dissertations": diss_count,
        "scholars": scholar_count,
        "advisors": advisor_count,
        "institutions": institution_count,
        "first_year": coverage["first_year"],
        "last_year": coverage["last_year"],
    }


@register.filter
def intcomma_plain(value):
    """Format an integer with commas: 12418 -> 12,418"""
    try:
        return f"{int(value):,}"
    except (ValueError, TypeError):
        return value


@register.filter
def initials(name):
    """Extract initials from a full name: 'Jane Doe' -> 'JD'"""
    parts = str(name).split()
    return "".join(p[0] for p in parts if p)[:2].upper()


@register.filter
def make_list_from_csv(value):
    """Split a comma-separated string into a list."""
    return [v.strip() for v in value.split(",")]
