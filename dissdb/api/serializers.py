"""Serializers for the public read-only API (v1).

Response shapes are documented on the /api page and are part of the public
contract — change them deliberately and bump the version if they break.
"""

from rest_framework import serializers
from rest_framework.reverse import reverse

from dissdb.models import (
    CommitteeMember,
    Dissertation,
    DissertationLink,
    ScholarWebsite,
)


def _api_url(view_name, pk, context):
    return reverse(view_name, kwargs={"pk": pk}, request=context.get("request"))


def _site_url(obj, context):
    url = obj.get_absolute_url()
    request = context.get("request")
    return request.build_absolute_uri(url) if request else url


# ── Nested / reference serializers ────────────────────────────────────

class ScholarRefSerializer(serializers.Serializer):
    """Compact scholar reference embedded in other records."""

    id = serializers.IntegerField(read_only=True)
    name_full = serializers.CharField(read_only=True)
    api_url = serializers.SerializerMethodField()

    def get_api_url(self, obj):
        return _api_url("apiv1:scholar-detail", obj.pk, self.context)


class SchoolRefSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)


class SchoolSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    aha_school_id = serializers.IntegerField(read_only=True)


class DepartmentRefSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)


class EmphasisSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    slug = serializers.CharField(read_only=True)


class DissertationLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = DissertationLink
        fields = ["url", "link_type", "label"]


class ScholarWebsiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScholarWebsite
        fields = ["url", "website_type", "label"]


class CommitteeMemberSerializer(serializers.Serializer):
    role = serializers.CharField(read_only=True)
    scholar = ScholarRefSerializer(read_only=True)


class DissertationRefSerializer(serializers.Serializer):
    """Compact dissertation reference embedded in scholar records."""

    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(read_only=True)
    year = serializers.IntegerField(read_only=True)
    api_url = serializers.SerializerMethodField()

    def get_api_url(self, obj):
        return _api_url("apiv1:dissertation-detail", obj.pk, self.context)


# ── Dissertation ──────────────────────────────────────────────────────

class DissertationListSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(read_only=True)
    year = serializers.IntegerField(read_only=True)
    author = ScholarRefSerializer(read_only=True)
    school = SchoolRefSerializer(read_only=True)
    advisor = serializers.SerializerMethodField()
    site_url = serializers.SerializerMethodField()
    api_url = serializers.SerializerMethodField()

    def get_advisor(self, obj):
        for cm in obj.committeemember_set.all():
            if cm.role == CommitteeMember.CHAIR:
                return ScholarRefSerializer(cm.scholar, context=self.context).data
        return None

    def get_site_url(self, obj):
        return _site_url(obj, self.context)

    def get_api_url(self, obj):
        return _api_url("apiv1:dissertation-detail", obj.pk, self.context)


class DissertationDetailSerializer(DissertationListSerializer):
    aha_dissertation_id = serializers.IntegerField(read_only=True)
    abstract = serializers.CharField(read_only=True)
    department = serializers.SerializerMethodField()
    school = SchoolSerializer(read_only=True)
    committee = serializers.SerializerMethodField()
    thematic_emphases = EmphasisSerializer(many=True, read_only=True)
    geographic_emphases = EmphasisSerializer(many=True, read_only=True)
    links = DissertationLinkSerializer(many=True, read_only=True)

    def get_department(self, obj):
        if obj.department_id:
            return DepartmentRefSerializer(obj.department, context=self.context).data
        return None

    def get_committee(self, obj):
        # chair(s) first, then readers
        members = sorted(
            obj.committeemember_set.all(),
            key=lambda cm: 0 if cm.role == CommitteeMember.CHAIR else 1,
        )
        return CommitteeMemberSerializer(members, many=True, context=self.context).data


# ── Scholar ───────────────────────────────────────────────────────────

class ScholarListSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name_full = serializers.CharField(read_only=True)
    orcid = serializers.CharField(read_only=True)
    orcid_url = serializers.CharField(read_only=True)
    dissertation_count = serializers.IntegerField(read_only=True)
    advised_count = serializers.IntegerField(read_only=True)
    site_url = serializers.SerializerMethodField()
    api_url = serializers.SerializerMethodField()

    def get_site_url(self, obj):
        return _site_url(obj, self.context)

    def get_api_url(self, obj):
        return _api_url("apiv1:scholar-detail", obj.pk, self.context)


class ScholarDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    aha_scholar_id = serializers.IntegerField(read_only=True)
    name_first = serializers.CharField(read_only=True)
    name_middle = serializers.CharField(read_only=True)
    name_last = serializers.CharField(read_only=True)
    name_suffix = serializers.CharField(read_only=True)
    name_full = serializers.CharField(read_only=True)
    orcid = serializers.CharField(read_only=True)
    orcid_url = serializers.CharField(read_only=True)
    affiliation = serializers.CharField(read_only=True)
    websites = ScholarWebsiteSerializer(many=True, read_only=True)
    dissertations_authored = serializers.SerializerMethodField()
    dissertations_advised = serializers.SerializerMethodField()
    site_url = serializers.SerializerMethodField()
    api_url = serializers.SerializerMethodField()

    def get_dissertations_authored(self, obj):
        qs = obj.dissertation_set.all().order_by("-year", "title")
        return DissertationRefSerializer(qs, many=True, context=self.context).data

    def get_dissertations_advised(self, obj):
        diss = (
            Dissertation.objects.filter(
                committeemember__scholar=obj,
                committeemember__role=CommitteeMember.CHAIR,
            )
            .distinct()
            .order_by("-year", "title")
        )
        return DissertationRefSerializer(diss, many=True, context=self.context).data

    def get_site_url(self, obj):
        return _site_url(obj, self.context)

    def get_api_url(self, obj):
        return _api_url("apiv1:scholar-detail", obj.pk, self.context)
