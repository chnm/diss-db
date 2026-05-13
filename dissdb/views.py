from collections import defaultdict

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import generic
from django.views.generic.edit import UpdateView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from dissdb.serializers import ScholarCreateSerializer, ScholarSerializer

from .filters import ComMemFilter, DissertationFilter, ScholarFilter
from .forms import (
    CommitteeMemberFormSet,
    DissertationForm,
    DissertationLinkFormSet,
    ScholarForm,
)
from .models import (
    CommitteeMember,
    Dissertation,
    DissertationLink,
    GeographicEmphasis,
    Scholar,
    ScholarWebsite,
    ThematicEmphasis,
)
from .tables import ComMemTable, DissTable, ScholarTable

# import pandas as pd


def index(request):
    return render(request, "index.html")


def about(request):
    return render(request, "about.html")


def contributing(request):
    return render(request, "contributing.html")

def network_viz(request):
    schools = School.objects.all()

    return render(request, "network_viz.html", {
        "schools": schools
    })

def get_school_network_data(request, school_id):
    try:
        school = School.objects.get(id=school_id)
    except School.DoesNotExist:
        return JsonResponse({"error": "School not found"}, status=404)

    # 1. Load all dissertations for this school in one query.
    dissertations = (
        Dissertation.objects
        .filter(school=school)
        .select_related("author")
    )

    if not dissertations.exists():
        return JsonResponse({"nodes": [], "links": []})

    dissertation_ids = [d.id for d in dissertations]

    # 2. Load all committee memberships for those dissertations in one query (avoids N+1).
    committee_members = (
        CommitteeMember.objects
        .filter(dissertation_id__in=dissertation_ids)
        .select_related("scholar", "dissertation__author")
    )

    # 3. Build node registry and link list in memory.
    ROLE_PRIORITY = {"advisor": 3, "author": 2, "committee": 1}

    node_registry = {}   # name_full -> dict
    links = []

    def upsert_node(scholar, group):
        """Add scholar to registry or upgrade their group if higher priority."""
        key = scholar.name_full
        current_priority = ROLE_PRIORITY.get(
            node_registry[key]["group"], 0
        ) if key in node_registry else 0
        if ROLE_PRIORITY[group] > current_priority:
            node_registry[key] = {
                "id": scholar.name_full,
                "scholar_id": scholar.pk,
                "url": scholar.get_absolute_url(),
                "group": group,
            }

    # Register every dissertation author first.
    for diss in dissertations:
        upsert_node(diss.author, "author")

    # Walk committee memberships to register advisors/readers and build links.
    for cm in committee_members:
        author = cm.dissertation.author
        member = cm.scholar

        if cm.role == CommitteeMember.CHAIR:
            upsert_node(member, "advisor")
            links.append({
                "source": author.name_full,
                "target": member.name_full,
                "relationship": "advisor",
            })
        elif cm.role == CommitteeMember.READER:
            upsert_node(member, "committee")
            links.append({
                "source": author.name_full,
                "target": member.name_full,
                "relationship": "committee member",
            })

    nodes = list(node_registry.values())

    return JsonResponse({"nodes": nodes, "links": links})


class ScholarListAPI(generics.ListAPIView):
    serializer_class = ScholarSerializer
    pagination_class = None

    def get_queryset(self):
        from django.contrib.postgres.search import TrigramSimilarity
        from django.db.models import Q
        from django.db.models.functions import Greatest

        qs = Scholar.objects.all()
        q = self.request.query_params.get("q", "")
        if q:
            qs = (
                qs.annotate(
                    similarity=Greatest(
                        TrigramSimilarity("name_first", q),
                        TrigramSimilarity("name_last", q),
                    )
                )
                .filter(
                    Q(name_first__icontains=q)
                    | Q(name_last__icontains=q)
                    | Q(name_middle__icontains=q)
                    | Q(similarity__gte=0.3)
                )
                .order_by("-similarity", "name_last", "name_first")
            )
        else:
            qs = qs.order_by("name_last", "name_first")
        return qs[:50]


class ScholarCreateAPI(generics.CreateAPIView):
    serializer_class = ScholarCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        scholar = serializer.save()
        return Response(
            {"id": scholar.pk, "name_full": scholar.name_full},
            status=status.HTTP_201_CREATED,
        )


class ScholarDetailAPI(APIView):
    def get_object(self, pk):
        try:
            return Scholar.objects.get(id=pk)
        except Scholar.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        data = self.get_object(pk)
        serializer = ScholarSerializer(data)
        return Response(serializer.data)


def _collect_url(urls, scholar):
    """Add a scholar's name_full → absolute URL to the urls dict."""
    urls[scholar.name_full] = scholar.get_absolute_url()


def get_viz_data(request, pk):
    data = []
    urls = {}
    scholar = Scholar.objects.get(id=pk)
    _collect_url(urls, scholar)

    # issue- what if scholar does not have a dissertation (only in Db as a Committee Member)
    try:
        dissertation = Dissertation.objects.get(author=scholar.id)
        has_dissertation = True
    except Dissertation.DoesNotExist:
        dissertation = None
        has_dissertation = False

    # get advisors (co-chairs) if scholar has a dissertation
    advisors = []
    if has_dissertation:
        advisors = list(
            CommitteeMember.objects.filter(
                dissertation=dissertation, role="chair"
            ).select_related("scholar")
        )

    advisorData = ""
    if advisors:
        for adv in advisors:
            _collect_url(urls, adv.scholar)
            data.append(adv.scholar.name_full + "/")
        # Use first advisor as the path prefix for the tree structure
        advisorData = advisors[0].scholar.name_full + "/" + scholar.name_full + "/"
        data.append(advisorData)
        # Add co-chairs as additional parent paths
        for adv in advisors[1:]:
            coAdvisorData = adv.scholar.name_full + "/" + scholar.name_full + "/"
            data.append(coAdvisorData)
    else:
        advisorData = scholar.name_full + "/"
        data.append(advisorData)

    # get their advisees
    advisees = CommitteeMember.objects.filter(role="chair", scholar=pk).select_related(
        "dissertation__author"
    )
    if advisees.exists():
        for advisee in advisees:
            _collect_url(urls, advisee.dissertation.author)
            adviseeData = advisorData + advisee.dissertation.author.name_full
            data.append(adviseeData)

    return JsonResponse({"paths": data, "urls": urls})


def get_viz_data_complex(request, pk):
    """Build the full genealogy tree for a scholar.

    Loads all chair records in a single query, then traverses in memory
    to avoid the N+1 query problem that caused production timeouts.
    """
    data = []
    urls = {}

    # Load all chair records with related scholars in ONE query
    all_chairs = list(
        CommitteeMember.objects.filter(role="chair").select_related(
            "scholar", "dissertation__author"
        )
    )

    # Build lookup maps
    # advisor_of: author_id -> advisor's Scholar object
    advisor_of = {}
    # advisees_of: scholar_id -> list of advisee Scholar objects
    advisees_of = defaultdict(list)
    # All scholars we've seen
    scholars = {}

    for cm in all_chairs:
        if cm.dissertation and cm.dissertation.author_id:
            author_id = cm.dissertation.author_id
            # Store first advisor only (handles multiple chairs gracefully)
            if author_id not in advisor_of:
                advisor_of[author_id] = cm.scholar
            advisees_of[cm.scholar_id].append(cm.dissertation.author)
            scholars[cm.scholar_id] = cm.scholar
            scholars[cm.dissertation.author_id] = cm.dissertation.author

    # Get the target scholar
    scholar = scholars.get(pk)
    if not scholar:
        try:
            scholar = Scholar.objects.get(id=pk)
            scholars[pk] = scholar
        except Scholar.DoesNotExist:
            return JsonResponse({"paths": [], "urls": {}})

    # Walk up to root ancestor (with cycle detection)
    current_id = pk
    visited = set()
    while current_id in advisor_of and current_id not in visited:
        visited.add(current_id)
        current_id = advisor_of[current_id].id
    root_id = current_id

    # Traverse downward in memory (no DB queries)
    def traverse(scholar_id, path, visited_down):
        s = scholars.get(scholar_id)
        if not s or scholar_id in visited_down:
            return
        visited_down.add(scholar_id)
        _collect_url(urls, s)
        path = path + s.name_full + "/"

        children = advisees_of.get(scholar_id, [])
        if children:
            for child in children:
                traverse(child.id, path, visited_down)
        data.append(path[0:-1])

    traverse(root_id, "", set())
    if data:
        data[-1] = data[-1] + "/"

    return JsonResponse({"paths": data, "urls": urls})


# @api_view(['GET'])
# def api_root(request, format=None):
#     return Response({
#         'scholars': reverse('scholar-list-api', request=request, format=format)
#     })


class FilteredScholarListView(SingleTableMixin, FilterView):
    table_class = ScholarTable
    model = Scholar
    filterset_class = ScholarFilter
    template_name = "dissertations/scholar_filter.html"


class ScholarCreateView(LoginRequiredMixin, generic.CreateView):
    model = Scholar
    form_class = ScholarForm
    template_name = "dissertations/scholar_create.html"
    login_url = "/admin/login/"

    def get_success_url(self):
        return self.object.get_absolute_url()


def _build_emphasis_tree(model):
    """Build a nested tree structure from a self-referential emphasis model."""
    all_items = model.objects.select_related("parent").order_by("name")
    by_parent = defaultdict(list)
    for item in all_items:
        by_parent[item.parent_id].append(item)

    def _subtree(parent_id):
        nodes = []
        for item in by_parent.get(parent_id, []):
            nodes.append(
                {
                    "id": item.pk,
                    "name": item.name,
                    "children": _subtree(item.pk),
                }
            )
        return nodes

    return _subtree(None)


class FilteredDissertationListView(SingleTableMixin, FilterView):
    table_class = DissTable
    model = Dissertation
    filterset_class = DissertationFilter
    template_name = "dissertations/dissertation_filter.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["geographic_tree"] = _build_emphasis_tree(GeographicEmphasis)
        context["thematic_tree"] = _build_emphasis_tree(ThematicEmphasis)
        # Pass currently selected IDs so Alpine can check them on page load
        context["selected_geographic"] = self.request.GET.getlist("geographic_emphases")
        context["selected_thematic"] = self.request.GET.getlist("thematic_emphases")
        return context


class FilteredComMemListView(SingleTableMixin, FilterView):
    table_class = ComMemTable
    model = CommitteeMember
    filterset_class = ComMemFilter
    template_name = "dissertations/committeemember_filter.html"


# class DissDetailView(generic.DetailView):
#     model = Dissertation
#     context_object_name = "dissertation_detail"
#     template_name = 'dissertations/dissertation_detail.html'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#
#         current_diss = self.get_object()
#
#         try:
#             context["advisor"] = CommitteeMember.objects.get(dissertation=current_diss)
#         except:
#             context["advisor"] = "information not available"
#         return context


class ScholarDetailView(generic.DetailView):
    model = Scholar
    context_object_name = "scholar_detail"
    template_name = "dissertations/scholar_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        scholar = self.object

        try:
            dissertation = Dissertation.objects.get(author=scholar.id)
            context["dissertation"] = dissertation

            advisors = CommitteeMember.objects.filter(
                dissertation=dissertation,
                role="chair",
            ).select_related("scholar")
            context["advisors"] = advisors if advisors.exists() else None

            readers = CommitteeMember.objects.filter(
                dissertation=dissertation,
                role="reader",
            ).select_related("scholar")
            context["readers"] = readers if readers.exists() else None

            context["dissLinks"] = DissertationLink.objects.filter(
                dissertation=dissertation
            )

        except Dissertation.DoesNotExist:
            context["dissertation"] = "information not available"
            context["advisors"] = None
            context["readers"] = None

        advisees = CommitteeMember.objects.filter(
            role="chair", scholar=scholar.id
        ).select_related("dissertation__author")
        context["advisees"] = advisees if advisees.exists() else None

        websites = ScholarWebsite.objects.filter(scholar=scholar.id)
        context["websites"] = websites if websites.exists() else None

        return context


class ScholarUpdateView(LoginRequiredMixin, UpdateView):
    model = Scholar
    form_class = ScholarForm
    template_name = "dissertations/scholar_edit.html"
    login_url = "/admin/login/"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            self.object = form.save()
            return redirect(self.object.get_absolute_url())
        return self.render_to_response(self.get_context_data(form=form))


class DissertationUpdateView(LoginRequiredMixin, UpdateView):
    model = Dissertation
    form_class = DissertationForm
    template_name = "dissertations/dissertation_edit.html"
    login_url = "/admin/login/"

    def get_context_data(self, **kwargs):
        if "link_formset" not in kwargs:
            kwargs["link_formset"] = DissertationLinkFormSet(
                instance=self.object, prefix="links"
            )
        if "cm_formset" not in kwargs:
            kwargs["cm_formset"] = CommitteeMemberFormSet(
                instance=self.object, prefix="cm"
            )
        context = super().get_context_data(**kwargs)
        context["geographic_tree"] = _build_emphasis_tree(GeographicEmphasis)
        context["thematic_tree"] = _build_emphasis_tree(ThematicEmphasis)
        context["selected_geographic_ids"] = list(
            self.object.geographic_emphases.values_list("pk", flat=True)
        )
        context["selected_thematic_ids"] = list(
            self.object.thematic_emphases.values_list("pk", flat=True)
        )
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        link_formset = DissertationLinkFormSet(
            request.POST, instance=self.object, prefix="links"
        )
        cm_formset = CommitteeMemberFormSet(
            request.POST, instance=self.object, prefix="cm"
        )
        if form.is_valid() and link_formset.is_valid() and cm_formset.is_valid():
            self.object = form.save()
            link_formset.instance = self.object
            link_formset.save()
            cm_formset.instance = self.object
            cm_formset.save()
            return redirect(self.object.author.get_absolute_url())
        return self.render_to_response(
            self.get_context_data(
                form=form, link_formset=link_formset, cm_formset=cm_formset
            )
        )


class DissertationCreateView(LoginRequiredMixin, generic.CreateView):
    model = Dissertation
    form_class = DissertationForm
    template_name = "dissertations/dissertation_create.html"
    login_url = "/admin/login/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["author"] = get_object_or_404(Scholar, pk=self.kwargs["pk"])
        context["geographic_tree"] = _build_emphasis_tree(GeographicEmphasis)
        context["thematic_tree"] = _build_emphasis_tree(ThematicEmphasis)
        context["selected_geographic_ids"] = []
        context["selected_thematic_ids"] = []
        return context

    def form_valid(self, form):
        author = get_object_or_404(Scholar, pk=self.kwargs["pk"])
        form.instance.author = author
        self.object = form.save()
        return redirect(author.get_absolute_url())
