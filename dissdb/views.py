from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify
from django.views import generic
from django.views.generic.edit import UpdateView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin, SingleTableView
from rest_framework import generics, permissions, renderers, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from django.core import serializers
from django.http import Http404, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from dissdb.serializers import ScholarCreateSerializer, ScholarSerializer

from .filters import ComMemFilter, DissertationFilter, ScholarFilter
from .forms import CommitteeMemberFormSet, DissertationForm, DissertationLinkFormSet, ScholarForm, ScholarWebsiteFormSet
from .models import CommitteeMember, Dissertation, DissertationLink, Scholar, ScholarWebsite
from .tables import ComMemTable, DissTable, ScholarTable
# import pandas as pd


def index(request):
    return render(request, "index.html")


def about(request):
    return render(request, "about.html")


def contributing(request):
    return render(request, "contributing.html")


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

    # get advisor if scholar has a dissertation
    advisor = None
    if has_dissertation:
        try:
            advisor = CommitteeMember.objects.get(
                dissertation=dissertation,
                role="chair"
            )
        except CommitteeMember.DoesNotExist:
            advisor = None

    advisorData = ""
    # get their advisor
    if advisor != None:
        _collect_url(urls, advisor.scholar)
        data.append(advisor.scholar.name_full + "/")
        advisorData = advisor.scholar.name_full + "/" + scholar.name_full + "/"
        data.append(advisorData)
    else:
        advisorData = scholar.name_full + "/"
        data.append(advisorData)

    # get their advisees
    advisees = CommitteeMember.objects.filter(role="chair", scholar=pk)
    if advisees.exists():
        for advisee in advisees:
            _collect_url(urls, advisee.dissertation.author)
            adviseeData = advisorData + advisee.dissertation.author.name_full
            data.append(adviseeData)

    return JsonResponse({"paths": data, "urls": urls})


def traverse(pk, path, data, urls):
    root = Scholar.objects.get(id=pk)
    _collect_url(urls, root)
    path = path + root.name_full + "/"

    advisees = CommitteeMember.objects.filter(role="chair", scholar=pk)

    if advisees.exists():
        for advisee in advisees:
            if advisee.dissertation and advisee.dissertation.author:
                traverse(advisee.dissertation.author.id, path, data, urls)
    data.append(path[0:-1])

    return root.id, path, data


def get_viz_data_complex(request, pk):
    data = []
    urls = {}
    path = ""

    scholar = Scholar.objects.get(id=pk)

    try:
        dissertation = Dissertation.objects.get(author=scholar.id)
    except Dissertation.DoesNotExist:
        # If no dissertation, scholar is the root
        pk, path, data = traverse(scholar.id, path, data, urls)
        data[-1] = data[-1] + "/"
        return JsonResponse({"paths": data, "urls": urls})

    try:
        advisor = CommitteeMember.objects.get(
            dissertation=dissertation,
            role="chair"
        )
    except CommitteeMember.DoesNotExist:
        advisor = None

    root = ""

    while advisor != None:
        try:
            root = CommitteeMember.objects.get(
                dissertation__author=advisor.scholar,
                role="chair"
            )
        except CommitteeMember.DoesNotExist:
            root = None

        if root != None:
            advisor = root
        else:
            break

    if advisor != None:
        root = advisor.scholar.id
    else:
        root = scholar.id
    pk, path, data = traverse(root, path, data, urls)
    data[-1] = data[-1] + "/"

    return JsonResponse({"paths": data, "urls": urls})


"""@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'scholars': reverse('scholar-list-api', request=request, format=format)
    })"""


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


class FilteredDissertationListView(SingleTableMixin, FilterView):
    table_class = DissTable
    model = Dissertation
    filterset_class = DissertationFilter
    template_name = 'dissertations/dissertation_filter.html'


class FilteredComMemListView(SingleTableMixin, FilterView):
    table_class = ComMemTable
    model = CommitteeMember
    filterset_class = ComMemFilter
    template_name = 'dissertations/committeemember_filter.html'

'''
class DissDetailView(generic.DetailView):
    model = Dissertation
    context_object_name = "dissertation_detail"
    template_name = 'dissertations/dissertation_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        current_diss = self.get_object()

        try:
            context["advisor"] = CommitteeMember.objects.get(dissertation=current_diss)
        except:
            context["advisor"] = "information not available"
        return context
'''


class ScholarDetailView(generic.DetailView):
    model = Scholar
    context_object_name = "scholar_detail"
    template_name = 'dissertations/scholar_detail.html'

    def get_object(self, queryset=None):
        slug = self.kwargs["slug"]
        for scholar in Scholar.objects.only("pk", "name_last", "name_first"):
            if (slugify(f"{scholar.name_last}-{scholar.name_first}") or "scholar") == slug:
                return Scholar.objects.get(pk=scholar.pk)
        raise Http404

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        scholar = self.object

        try:
            dissertation = Dissertation.objects.get(author=scholar.id)
            context["dissertation"] = dissertation

            try:
                context["advisor"] = CommitteeMember.objects.get(
                    dissertation=dissertation,
                    role="chair",
                )
            except CommitteeMember.DoesNotExist:
                context["advisor"] = "information not available"

            readers = CommitteeMember.objects.filter(
                dissertation=dissertation,
                role="reader",
            )
            context["readers"] = readers if readers.exists() else None

            context["dissLinks"] = DissertationLink.objects.filter(
                dissertation=dissertation
            )

        except Dissertation.DoesNotExist:
            context["dissertation"] = "information not available"
            context["advisor"] = "information not available"
            context["readers"] = None

        advisees = CommitteeMember.objects.filter(role="chair", scholar=scholar.id)
        context["advisees"] = advisees if advisees.exists() else None

        websites = ScholarWebsite.objects.filter(scholar=scholar.id)
        context["websites"] = websites if websites.exists() else None


        return context


class ScholarUpdateView(LoginRequiredMixin, UpdateView):
    model = Scholar
    form_class = ScholarForm
    template_name = "dissertations/scholar_edit.html"
    login_url = "/admin/login/"

    def get_context_data(self, **kwargs):
        if "website_formset" not in kwargs:
            kwargs["website_formset"] = ScholarWebsiteFormSet(instance=self.object)
        return super().get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        website_formset = ScholarWebsiteFormSet(request.POST, instance=self.object)
        if form.is_valid() and website_formset.is_valid():
            self.object = form.save()
            website_formset.instance = self.object
            website_formset.save()
            return redirect(self.object.get_absolute_url())
        return self.render_to_response(
            self.get_context_data(form=form, website_formset=website_formset)
        )


class DissertationUpdateView(LoginRequiredMixin, UpdateView):
    model = Dissertation
    form_class = DissertationForm
    template_name = "dissertations/dissertation_edit.html"
    login_url = "/admin/login/"

    def get_context_data(self, **kwargs):
        if "link_formset" not in kwargs:
            kwargs["link_formset"] = DissertationLinkFormSet(instance=self.object, prefix="links")
        if "cm_formset" not in kwargs:
            kwargs["cm_formset"] = CommitteeMemberFormSet(instance=self.object, prefix="cm")
        return super().get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        link_formset = DissertationLinkFormSet(request.POST, instance=self.object, prefix="links")
        cm_formset = CommitteeMemberFormSet(request.POST, instance=self.object, prefix="cm")
        if form.is_valid() and link_formset.is_valid() and cm_formset.is_valid():
            self.object = form.save()
            link_formset.instance = self.object
            link_formset.save()
            cm_formset.instance = self.object
            cm_formset.save()
            return redirect(self.object.author.get_absolute_url())
        return self.render_to_response(
            self.get_context_data(form=form, link_formset=link_formset, cm_formset=cm_formset)
        )


class DissertationCreateView(LoginRequiredMixin, generic.CreateView):
    model = Dissertation
    form_class = DissertationForm
    template_name = "dissertations/dissertation_create.html"
    login_url = "/admin/login/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["author"] = get_object_or_404(Scholar, pk=self.kwargs["pk"])
        return context

    def form_valid(self, form):
        author = get_object_or_404(Scholar, pk=self.kwargs["pk"])
        form.instance.author = author
        self.object = form.save()
        return redirect(author.get_absolute_url())
