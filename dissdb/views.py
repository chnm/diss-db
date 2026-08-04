from collections import defaultdict

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Max, Min, Q
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import generic
from django.views.decorators.http import require_http_methods
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
    Department,
    Dissertation,
    DissertationLink,
    GeographicEmphasis,
    Scholar,
    ScholarWebsite,
    School,
    ThematicEmphasis,
)
from .tables import ComMemTable, DissTable, ScholarTable

# import pandas as pd


def index(request):
    recent_dissertations = (
        Dissertation.objects.select_related("author", "school")
        .prefetch_related("committeemember_set__scholar")
        .order_by("-year", "-id")[:6]
    )

    # Annotate each dissertation with its advisor
    recent_with_advisors = []
    for diss in recent_dissertations:
        advisor = None
        for cm in diss.committeemember_set.all():
            if cm.role == CommitteeMember.CHAIR:
                advisor = cm.scholar
                break
        recent_with_advisors.append({"dissertation": diss, "advisor": advisor})

    # Stats
    diss_count = Dissertation.objects.count()
    scholar_count = Scholar.objects.count()
    advisor_count = (
        CommitteeMember.objects.filter(role="chair")
        .values("scholar")
        .distinct()
        .count()
    )
    institution_count = Dissertation.objects.values("school").distinct().count()
    year_range = Dissertation.objects.aggregate(
        first_year=Min("year"), last_year=Max("year")
    )

    # Decade counts
    from django.db.models import F
    from django.db.models.functions import Floor

    decade_counts = (
        Dissertation.objects.annotate(
            decade=Floor(F("year") / 10) * 10,
        )
        .values("decade")
        .annotate(count=Count("id"))
        .order_by("-decade")
    )
    decades = [
        {
            "label": f"{int(d['decade'])}s",
            "count": d["count"],
            "decade": int(d["decade"]),
        }
        for d in decade_counts
    ]

    context = {
        "active_nav": "home",
        "recent_dissertations": recent_with_advisors,
        "diss_count": diss_count,
        "scholar_count": scholar_count,
        "advisor_count": advisor_count,
        "institution_count": institution_count,
        "first_year": year_range.get("first_year"),
        "last_year": year_range.get("last_year"),
        "decades": decades,
    }
    return render(request, "index.html", context)


def _matching_scholars(query):
    """Match each search term against any part of a scholar's public name."""
    scholars = Scholar.objects.all()
    for term in query.split():
        scholars = scholars.filter(
            Q(name_first__icontains=term)
            | Q(name_middle__icontains=term)
            | Q(name_last__icontains=term)
            | Q(name_suffix__icontains=term)
            | Q(affiliation__icontains=term)
        )
    return scholars


def search(request):
    """Search the catalogue across its principal public record types."""
    query = request.GET.get("q", "").strip()
    context = {
        "active_nav": "search",
        "query": query,
        "searched": bool(query),
    }
    if not query:
        return render(request, "search.html", context)

    dissertations = (
        Dissertation.objects.filter(title__icontains=query)
        .select_related("author", "school")
        .order_by("-year", "title")
    )
    scholars = _matching_scholars(query).order_by(
        "name_last", "name_first", "name_middle"
    )
    schools = (
        School.objects.filter(name__icontains=query)
        .annotate(dissertation_count=Count("dissertation", distinct=True))
        .order_by("-dissertation_count", "name")
    )

    geographic_fields = (
        GeographicEmphasis.objects.filter(name__icontains=query)
        .annotate(dissertation_count=Count("dissertations", distinct=True))
        .filter(dissertation_count__gt=0)
    )
    thematic_fields = (
        ThematicEmphasis.objects.filter(name__icontains=query)
        .annotate(dissertation_count=Count("dissertations", distinct=True))
        .filter(dissertation_count__gt=0)
    )
    fields = sorted(
        [
            {
                "kind": "Geographic",
                "label": field.display_name,
                "url_param": "geographic_emphases",
                "field": field,
            }
            for field in geographic_fields
        ]
        + [
            {
                "kind": "Thematic",
                "label": field.name,
                "url_param": "thematic_emphases",
                "field": field,
            }
            for field in thematic_fields
        ],
        key=lambda item: (-item["field"].dissertation_count, item["label"]),
    )

    search_counts = {
        "dissertations": dissertations.count(),
        "scholars": scholars.count(),
        "schools": schools.count(),
        "fields": len(fields),
    }
    context.update(
        {
            "dissertations": dissertations[:6],
            "scholars": scholars[:6],
            "schools": schools[:6],
            "fields": fields[:6],
            "search_counts": search_counts,
            "total_count": sum(search_counts.values()),
        }
    )
    return render(request, "search.html", context)


def api_docs(request):
    """Human-readable documentation for the public read-only API (v1)."""
    example_diss = Dissertation.objects.order_by("-year", "-id").first()
    example_scholar = (
        Scholar.objects.filter(committeemember__role=CommitteeMember.CHAIR)
        .distinct()
        .first()
        or Scholar.objects.first()
    )
    return render(
        request,
        "api.html",
        {
            "active_nav": "api",
            "example_diss_id": example_diss.pk if example_diss else 1,
            "example_scholar_id": example_scholar.pk if example_scholar else 1,
        },
    )


def about(request):
    return render(request, "about.html", {"active_nav": "about"})


def contributing(request):
    return render(request, "contributing.html", {"active_nav": "contribute"})


def network_viz(request):
    schools = School.objects.all()

    return render(request, "network_viz.html", {"schools": schools})


def get_school_network_data(request, school_id):
    try:
        school = School.objects.get(id=school_id)
    except School.DoesNotExist:
        return JsonResponse({"error": "School not found"}, status=404)

    # 1. Load all dissertations for this school in one query.
    dissertations = Dissertation.objects.filter(school=school).select_related("author")

    if not dissertations.exists():
        return JsonResponse({"nodes": [], "links": []})

    dissertation_ids = [d.id for d in dissertations]

    # 2. Load all committee memberships for those dissertations in one query (avoids N+1).
    committee_members = CommitteeMember.objects.filter(
        dissertation_id__in=dissertation_ids
    ).select_related("scholar", "dissertation__author")

    # 3. Build node registry and link list in memory.
    ROLE_PRIORITY = {"advisor": 3, "author": 2, "committee": 1}

    node_registry = {}  # name_full -> dict
    links = []

    def upsert_node(scholar, group):
        """Add scholar to registry or upgrade their group if higher priority."""
        key = scholar.name_full
        current_priority = (
            ROLE_PRIORITY.get(node_registry[key]["group"], 0)
            if key in node_registry
            else 0
        )
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
            links.append(
                {
                    "source": author.name_full,
                    "target": member.name_full,
                    "relationship": "advisor",
                }
            )
        elif cm.role == CommitteeMember.READER:
            upsert_node(member, "committee")
            links.append(
                {
                    "source": author.name_full,
                    "target": member.name_full,
                    "relationship": "committee member",
                }
            )

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


class FilteredScholarListView(SingleTableMixin, FilterView):
    table_class = ScholarTable
    model = Scholar
    filterset_class = ScholarFilter
    template_name = "dissertations/scholar_filter.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_nav"] = "scholars"
        return context


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
                    "name": getattr(item, "display_name", item.name),
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
        context["active_nav"] = "dissertations"
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_nav"] = "committee"
        return context


def diss_detail_redirect(request, pk):
    """Redirect dissertation detail URLs to the author's scholar profile."""
    diss = get_object_or_404(Dissertation, pk=pk)
    return redirect(diss.author.get_absolute_url())


def department_list_api(request):
    """Return departments filtered by school_id query param."""
    school_id = request.GET.get("school_id")
    if school_id:
        depts = Department.objects.filter(school_id=school_id).order_by("name")
    else:
        depts = Department.objects.select_related("school").order_by(
            "school__name", "name"
        )
    data = [{"id": d.pk, "name": d.name, "school_id": d.school_id} for d in depts]
    return JsonResponse(data, safe=False)


@require_http_methods(["POST"])
def department_create_api(request):
    """Create a new department. Requires authentication."""
    import json as _json

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=403)
    try:
        body = _json.loads(request.body)
    except _json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    name = body.get("name", "").strip()
    school_id = body.get("school_id")
    if not name or not school_id:
        return JsonResponse({"error": "name and school_id are required"}, status=400)
    try:
        school = School.objects.get(pk=school_id)
    except School.DoesNotExist:
        return JsonResponse({"error": "School not found"}, status=404)
    # Check for existing department with same name at same school
    dept, created = Department.objects.get_or_create(name=name, school=school)
    return JsonResponse(
        {"id": dept.pk, "name": dept.name, "school_id": dept.school_id},
        status=201 if created else 200,
    )


class ScholarDetailView(generic.DetailView):
    model = Scholar
    context_object_name = "scholar_detail"
    template_name = "dissertations/scholar_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_nav"] = "scholars"

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
            context["dissertation"] = None
            context["advisors"] = None
            context["readers"] = None

        # Advisees - dissertations this scholar chaired
        advisees = (
            CommitteeMember.objects.filter(role="chair", scholar=scholar.id)
            .select_related("dissertation__author", "dissertation__school")
            .order_by("-dissertation__year")
        )
        context["advisees"] = advisees if advisees.exists() else None
        context["advisee_count"] = advisees.count()

        # Committees served on (as reader)
        committees_served = (
            CommitteeMember.objects.filter(role="reader", scholar=scholar.id)
            .select_related("dissertation__author", "dissertation__school")
            .order_by("-dissertation__year")
        )
        context["committees_served"] = (
            committees_served if committees_served.exists() else None
        )
        context["committee_count"] = committees_served.count()

        # Lineage chain (walk up advisor chain)
        lineage = []
        current = scholar
        visited_ids = set()
        while current and current.pk not in visited_ids:
            visited_ids.add(current.pk)
            try:
                cur_diss = Dissertation.objects.get(author=current)
                advisor_cm = (
                    CommitteeMember.objects.filter(dissertation=cur_diss, role="chair")
                    .select_related("scholar")
                    .first()
                )
                if advisor_cm:
                    lineage.append(advisor_cm.scholar)
                    current = advisor_cm.scholar
                else:
                    break
            except Dissertation.DoesNotExist:
                break
        context["lineage"] = lineage
        context["lineage_depth"] = len(lineage)

        websites = ScholarWebsite.objects.filter(scholar=scholar.id)
        context["websites"] = websites if websites.exists() else None

        # Related dissertations: hybrid scoring (content + structure)
        if context.get("dissertation") and context["dissertation"]:
            from django.contrib.postgres.search import (
                SearchQuery,
                SearchRank,
                SearchVector,
            )

            diss = context["dissertation"]

            # Build sets for structural bonus scoring
            advisor_ids = set()
            if context.get("advisors"):
                advisor_ids = {a.scholar_id for a in context["advisors"]}
            same_advisor_diss_ids = (
                set(
                    CommitteeMember.objects.filter(
                        role="chair", scholar_id__in=advisor_ids
                    )
                    .exclude(dissertation=diss)
                    .values_list("dissertation_id", flat=True)
                )
                if advisor_ids
                else set()
            )

            diss_geo_ids = set(diss.geographic_emphases.values_list("pk", flat=True))
            diss_thematic_ids = set(diss.thematic_emphases.values_list("pk", flat=True))

            # Full-text search on title + abstract
            vector = SearchVector("title", weight="A") + SearchVector(
                "abstract", weight="B"
            )
            query = SearchQuery(diss.title, search_type="websearch")

            candidates = (
                Dissertation.objects.exclude(pk=diss.pk)
                .select_related("author", "school")
                .annotate(
                    text_rank=SearchRank(vector, query),
                )
            )

            # Score in Python so we can combine text rank + structural bonuses
            scored = []
            for c in candidates.filter(text_rank__gt=0.001).order_by("-text_rank")[:50]:
                score = float(c.text_rank)

                # Bonus: same advisor (+0.5)
                if c.pk in same_advisor_diss_ids:
                    score += 0.5

                # Bonus: same school (+0.2)
                if c.school_id == diss.school_id:
                    score += 0.2

                # Bonus: shared emphasis tags (+0.1 each)
                if diss_geo_ids or diss_thematic_ids:
                    c_geo = set(c.geographic_emphases.values_list("pk", flat=True))
                    c_thematic = set(c.thematic_emphases.values_list("pk", flat=True))
                    shared = len(diss_geo_ids & c_geo) + len(
                        diss_thematic_ids & c_thematic
                    )
                    score += shared * 0.1

                scored.append((score, c))

            scored.sort(key=lambda x: -x[0])
            related = [c for _, c in scored[:3]]

            # Fallback if full-text search returned fewer than 3
            if len(related) < 3:
                fallback_exclude = {diss.pk} | {r.pk for r in related}
                # Try same advisor
                if len(related) < 3 and same_advisor_diss_ids:
                    for did in same_advisor_diss_ids - fallback_exclude:
                        if len(related) >= 3:
                            break
                        try:
                            related.append(
                                Dissertation.objects.select_related(
                                    "author", "school"
                                ).get(pk=did)
                            )
                            fallback_exclude.add(did)
                        except Dissertation.DoesNotExist:
                            pass
                # Then same school
                if len(related) < 3:
                    school_fill = (
                        Dissertation.objects.filter(school=diss.school)
                        .exclude(pk__in=fallback_exclude)
                        .select_related("author", "school")
                        .order_by("-year")[: 3 - len(related)]
                    )
                    related.extend(school_fill)

            context["related_dissertations"] = related
        else:
            context["related_dissertations"] = []

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
