from django.shortcuts import render
from django.views import generic
from django_tables2 import SingleTableView, SingleTableMixin
from .models import Dissertation, CommitteeMember, Scholar
from .tables import DissTable, ComMemTable
from .filters import DissertationFilter, ComMemFilter
from django_filters.views import FilterView
from django.http import Http404, JsonResponse
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from dissertations.serializers import ScholarSerializer
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics


def index(request):
    return render(request, "index.html")


"""class DissListView(SingleTableView):
    model = Dissertation
    table_class = DissTable """


class FilteredDissertationListView(SingleTableMixin, FilterView):
    table_class = DissTable
    model = Dissertation
    filterset_class = DissertationFilter


"""class CommMemListView(SingleTableView):
    model = CommitteeMember
    table_class = ComMemTable"""


class FilteredComMemListView(SingleTableMixin, FilterView):
    table_class = ComMemTable
    model = CommitteeMember
    filterset_class = ComMemFilter


class DissDetailView(generic.DetailView):
    model = Dissertation
    name = "diss-detail"


class ScholarList(generics.ListCreateAPIView):
    """List all scholars or create a new scholar"""

    queryset = Scholar.objects.all()
    serializer_class = ScholarSerializer


class ScholarDetail(generics.RetrieveUpdateDestroyAPIView):
    """retrieve, update, or delete a scholar"""

    queryset = Scholar.objects.all()
    serializer_class = ScholarSerializer
