from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from simple_history.admin import SimpleHistoryAdmin

from .models import AccountRequest, CommitteeMember, Dissertation, DissertationLink, DuplicateCandidate, MagicLink, Scholar, ScholarWebsite, School, Source

User = get_user_model()

@admin.register(Source)
class SourceAdmin(SimpleHistoryAdmin):
    list_display = ['name', 'source_type', 'date_added']
    list_filter = ['source_type']
    search_fields = ['name', 'notes']
    history_list_display = ['name', 'source_type']

@admin.register(School)
class SchoolAdmin(SimpleHistoryAdmin):
    search_fields = ("name",)
    history_list_display = ['name']


class DissertationInline(admin.TabularInline):
    model = Dissertation
    fields = ("title", "year", "school")
    readonly_fields = ("title", "year", "school")
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


class CommitteeMemberInline(admin.TabularInline):
    model = CommitteeMember
    fields = ("dissertation", "role")
    readonly_fields = ("dissertation", "role")
    extra = 0
    can_delete = False
    verbose_name_plural = "Committee Membership"

    def has_add_permission(self, request, obj=None):
        return False

class ScholarWebsiteInline(admin.TabularInline):
    model = ScholarWebsite
    extra = 1  # number of empty forms to show
    fields = ['website_type', 'url', 'label', 'source']

class DissertationLinkInline(admin.TabularInline):
    model = DissertationLink
    extra = 1
    fields = ['link_type', 'url', 'label', 'source']


@admin.register(Scholar)
class ScholarAdmin(SimpleHistoryAdmin):
    list_display = (
        "name_last",
        "name_first",
        "name_full_rev",
        "authored_dissertations_count",
        "committee_memberships_count",
        "orcid",
        "id",
    )
    readonly_fields = (
        "id",
        "aha_name",
        "orcid_url",
        "authored_dissertations_links",
        "committee_memberships_links",
    )
    search_fields = ("name_last", "name_first")
    inlines = [DissertationInline, CommitteeMemberInline, ScholarWebsiteInline]

    history_list_display = ['name_last', 'name_first', 'orcid']

    def authored_dissertations_count(self, obj):
        count = obj.dissertation_set.count()
        return count

    authored_dissertations_count.short_description = "Authored"

    def committee_memberships_count(self, obj):
        count = obj.committeemember_set.count()
        return count

    committee_memberships_count.short_description = "Committee"

    def authored_dissertations_links(self, obj):
        dissertations = obj.dissertation_set.all()
        if not dissertations:
            return "No authored dissertations"

        links = []
        for diss in dissertations:
            url = reverse("admin:dissdb_dissertation_change", args=[diss.pk])
            links.append(
                format_html('<a href="{}">{} ({})</a>', url, diss.main_title, diss.year)
            )
        return format_html("<br>".join(links))

    authored_dissertations_links.short_description = "Dissertation"

    def committee_memberships_links(self, obj):
        memberships = obj.committeemember_set.all()
        if not memberships:
            return "No committee memberships"

        links = []
        for membership in memberships:
            url = reverse(
                "admin:dissdb_dissertation_change",
                args=[membership.dissertation.pk],
            )
            links.append(
                format_html(
                    '<a href="{}">{} ({}) - {}</a>',
                    url,
                    membership.dissertation.main_title,
                    membership.dissertation.year,
                    membership.role,
                )
            )
        return format_html("<br>".join(links))

    committee_memberships_links.short_description = "Committee Memberships"


class CommitteeMemberForDissertationInline(admin.TabularInline):
    model = CommitteeMember
    fields = ("scholar", "role")
    readonly_fields = ("scholar", "role")
    extra = 0
    can_delete = False
    verbose_name_plural = "Committee Members"

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Dissertation)
class DissertationAdmin(SimpleHistoryAdmin):
    list_display = ("main_title", "year", "author", "school", "committee_count")
    autocomplete_fields = (
        "author",
        "school",
    )
    search_fields = ("title",)
    inlines = [CommitteeMemberForDissertationInline, DissertationLinkInline]

    history_list_display = ['title', 'year', 'author', 'school']

    def committee_count(self, obj):
        return obj.committeemember_set.count()

    committee_count.short_description = "Committee Size"


@admin.register(CommitteeMember)
class CommitteeMemberAdmin(SimpleHistoryAdmin):
    list_display = ("scholar", "dissertation")
    autocomplete_fields = (
        "scholar",
        "dissertation",
    )
    history_list_display = ['scholar', 'dissertation', 'role']


@admin.register(DuplicateCandidate)
class DuplicateCandidateAdmin(admin.ModelAdmin):
    list_display = (
        "scholar_1",
        "scholar_2",
        "confidence_score",
        "name_comparison",
        "reviewed",
        "is_duplicate",
        "created_at",
    )
    list_filter = (
        "reviewed",
        "is_duplicate",
        "created_at",
    )
    list_editable = ("reviewed", "is_duplicate")
    autocomplete_fields = ("scholar_1", "scholar_2")
    search_fields = (
        "scholar_1__name_last",
        "scholar_2__name_last",
        "scholar_1__name_first",
        "scholar_2__name_first",
    )
    ordering = ("-confidence_score", "-created_at")
    readonly_fields = (
        "confidence_score",
        "created_at",
        "scholar_1_details",
        "scholar_2_details",
        "comparison_summary",
        "scholar_1_dissertations",
        "scholar_2_dissertations",
    )

    def name_comparison(self, obj):
        """Show name differences side by side"""
        s1, s2 = obj.scholar_1, obj.scholar_2

        differences = []
        if s1.name_first != s2.name_first:
            differences.append(f"First: {s1.name_first} ≠ {s2.name_first}")
        if s1.name_middle != s2.name_middle:
            middle1 = s1.name_middle or "None"
            middle2 = s2.name_middle or "None"
            differences.append(f"Middle: {middle1} ≠ {middle2}")
        if s1.name_last != s2.name_last:
            differences.append(f"Last: {s1.name_last} ≠ {s2.name_last}")

        if not differences:
            return "Names identical"
        return format_html("<br>".join(differences))

    name_comparison.short_description = "Name Differences"

    def scholar_1_details(self, obj):
        scholar = obj.scholar_1
        url = reverse("admin:dissdb_scholar_change", args=[scholar.pk])

        details = [
            f"<strong><a href='{url}'>{scholar.name_full}</a></strong>",
            f"ID: {scholar.id}",
        ]

        if scholar.aha_name and scholar.aha_name != scholar.name_full:
            details.append(f"AHA Name: {scholar.aha_name}")
        if scholar.orcid:
            details.append(f"ORCID: {scholar.orcid}")

        return format_html("<br>".join(details))

    scholar_1_details.short_description = "Scholar 1 Details"

    def scholar_2_details(self, obj):
        scholar = obj.scholar_2
        url = reverse("admin:dissdb_scholar_change", args=[scholar.pk])

        details = [
            f"<strong><a href='{url}'>{scholar.name_full}</a></strong>",
            f"ID: {scholar.id}",
        ]

        if scholar.aha_name and scholar.aha_name != scholar.name_full:
            details.append(f"AHA Name: {scholar.aha_name}")
        if scholar.orcid:
            details.append(f"ORCID: {scholar.orcid}")

        return format_html("<br>".join(details))

    scholar_2_details.short_description = "Scholar 2 Details"

    def comparison_summary(self, obj):
        s1, s2 = obj.scholar_1, obj.scholar_2

        summary = []

        # Check if they have different ORCIDs (strong indicator they're different people)
        if s1.orcid and s2.orcid and s1.orcid != s2.orcid:
            summary.append("⚠️ Different ORCIDs - likely different people")
        elif s1.orcid and s2.orcid and s1.orcid == s2.orcid:
            summary.append("✅ Same ORCID - definitely same person")

        # Compare dissertation counts
        s1_authored = s1.dissertation_set.count()
        s2_authored = s2.dissertation_set.count()
        s1_committee = s1.committeemember_set.count()
        s2_committee = s2.committeemember_set.count()

        summary.append(f"Authored: {s1_authored} vs {s2_authored}")
        summary.append(f"Committee: {s1_committee} vs {s2_committee}")

        if (
            s1_authored == 0
            and s2_authored == 0
            and s1_committee == 0
            and s2_committee == 0
        ):
            summary.append("⚠️ Neither has any dissertation activity")

        return format_html("<br>".join(summary))

    comparison_summary.short_description = "Quick Comparison"

    def scholar_1_dissertations(self, obj):
        scholar = obj.scholar_1

        content = []

        # Authored dissertations
        authored = scholar.dissertation_set.all()
        if authored:
            content.append("<strong>Authored:</strong>")
            for diss in authored:
                url = reverse("admin:dissdb_dissertation_change", args=[diss.pk])
                content.append(f'• <a href="{url}">{diss.main_title} ({diss.year})</a>')

        # Committee memberships
        committee = scholar.committeemember_set.all()
        if committee:
            content.append("<strong>Committee Service:</strong>")
            for membership in committee:
                url = reverse(
                    "admin:dissdb_dissertation_change",
                    args=[membership.dissertation.pk],
                )
                content.append(
                    f'• <a href="{url}">{membership.dissertation.main_title} ({membership.dissertation.year})</a> - {membership.role}'
                )

        if not content:
            content.append("No dissertation activity")

        return format_html("<br>".join(content))

    scholar_1_dissertations.short_description = "Scholar 1 Activity"

    def scholar_2_dissertations(self, obj):
        scholar = obj.scholar_2

        content = []

        # Authored dissertations
        authored = scholar.dissertation_set.all()
        if authored:
            content.append("<strong>Authored:</strong>")
            for diss in authored:
                url = reverse("admin:dissdb_dissertation_change", args=[diss.pk])
                content.append(f'• <a href="{url}">{diss.main_title} ({diss.year})</a>')

        # Committee memberships
        committee = scholar.committeemember_set.all()
        if committee:
            content.append("<strong>Committee Service:</strong>")
            for membership in committee:
                url = reverse(
                    "admin:dissdb_dissertation_change",
                    args=[membership.dissertation.pk],
                )
                content.append(
                    f'• <a href="{url}">{membership.dissertation.main_title} ({membership.dissertation.year})</a> - {membership.role}'
                )

        if not content:
            content.append("No dissertation activity")

        return format_html("<br>".join(content))

    scholar_2_dissertations.short_description = "Scholar 2 Activity"

@admin.register(ScholarWebsite)
class ScholarWebsiteAdmin(admin.ModelAdmin):
    list_display = ['scholar', 'website_type', 'url', 'label']
    search_fields = ['scholar__name_last', 'url']
    list_filter = ['website_type']


@admin.register(DissertationLink)
class DissertationLinkAdmin(admin.ModelAdmin):
    list_display = ['dissertation', 'link_type', 'url', 'label']
    search_fields = ['dissertation__title', 'url']
    list_filter = ['link_type']


@admin.register(AccountRequest)
class AccountRequestAdmin(SimpleHistoryAdmin):
    list_display = ['email', 'name', 'status', 'created_at', 'reviewed_by', 'reviewed_at']
    list_filter = ['status', 'created_at']
    search_fields = ['email', 'name']
    readonly_fields = ['created_at', 'updated_at', 'reviewed_by', 'reviewed_at']
    actions = ['approve_requests', 'reject_requests']

    @admin.action(description="Approve selected requests and create user accounts")
    def approve_requests(self, request, queryset):
        from .views import _create_and_send_magic_link

        approved = 0
        for acct_request in queryset.filter(status=AccountRequest.PENDING):
            user, created = User.objects.get_or_create(
                email=acct_request.email,
                defaults={
                    "username": acct_request.email,
                    "first_name": acct_request.name.split()[0] if acct_request.name else "",
                    "last_name": " ".join(acct_request.name.split()[1:]) if acct_request.name else "",
                },
            )
            if created:
                user.set_unusable_password()
                user.save()

            _create_and_send_magic_link(request, user)

            acct_request.status = AccountRequest.APPROVED
            acct_request.reviewed_by = request.user
            acct_request.reviewed_at = timezone.now()
            acct_request.save()
            approved += 1

        self.message_user(
            request,
            f"{approved} request(s) approved. Login links have been sent.",
            messages.SUCCESS,
        )

    @admin.action(description="Reject selected requests")
    def reject_requests(self, request, queryset):
        updated = queryset.filter(status=AccountRequest.PENDING).update(
            status=AccountRequest.REJECTED,
            reviewed_by=request.user,
            reviewed_at=timezone.now(),
        )
        self.message_user(request, f"{updated} request(s) rejected.", messages.SUCCESS)


@admin.register(MagicLink)
class MagicLinkAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'expires_at', 'used', 'used_at']
    list_filter = ['used', 'created_at']
    search_fields = ['user__email', 'user__username']
    readonly_fields = ['token', 'user', 'expires_at', 'used', 'used_at', 'created_at']

    def has_add_permission(self, request):
        return False