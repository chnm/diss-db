from django.db.models import Count, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny
from rest_framework.throttling import ScopedRateThrottle

from dissdb.models import CommitteeMember, Dissertation, Scholar

from . import serializers as s
from .filters import DissertationApiFilter, ScholarApiFilter
from .pagination import DefaultPagination


class BaseApiViewSet(viewsets.ReadOnlyModelViewSet):
    """Shared config for public read endpoints: open access, paginated, throttled."""

    permission_classes = [AllowAny]
    pagination_class = DefaultPagination
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "api-v1"
    filter_backends = [DjangoFilterBackend, OrderingFilter]


class DissertationViewSet(BaseApiViewSet):
    filterset_class = DissertationApiFilter
    ordering_fields = ["year", "title", "id"]
    ordering = ["-year", "title"]

    def get_queryset(self):
        qs = Dissertation.objects.select_related(
            "author", "school", "department"
        ).prefetch_related("committeemember_set__scholar")
        if self.action == "retrieve":
            qs = qs.prefetch_related(
                "thematic_emphases", "geographic_emphases", "links"
            )
        return qs

    def get_serializer_class(self):
        if self.action == "retrieve":
            return s.DissertationDetailSerializer
        return s.DissertationListSerializer


class ScholarViewSet(BaseApiViewSet):
    filterset_class = ScholarApiFilter
    ordering_fields = ["name_last", "name_first", "id"]
    ordering = ["name_last", "name_first"]

    def get_queryset(self):
        qs = Scholar.objects.all()
        if self.action == "list":
            qs = qs.annotate(
                dissertation_count=Count("dissertation", distinct=True),
                advised_count=Count(
                    "committeemember",
                    filter=Q(committeemember__role=CommitteeMember.CHAIR),
                    distinct=True,
                ),
            )
        else:
            qs = qs.prefetch_related("websites")
        return qs

    def get_serializer_class(self):
        if self.action == "retrieve":
            return s.ScholarDetailSerializer
        return s.ScholarListSerializer
