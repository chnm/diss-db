from django.shortcuts import render
from django.views import generic
from django_tables2 import SingleTableView, SingleTableMixin
from .models import Dissertation, CommitteeMember, Scholar, DissertationLink, ScholarWebsite
from .tables import DissTable, ComMemTable
from .filters import DissertationFilter, ComMemFilter
from django_filters.views import FilterView
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from dissdb.serializers import ScholarSerializer
from rest_framework import permissions, viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics, renderers
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.reverse import reverse
# import pandas as pd


def index(request):
    return render(request, "index.html")


def about(request):
    return render(request, "about.html")


class ScholarListAPI(generics.ListAPIView):
    queryset = Scholar.objects.all()
    serializer_class = ScholarSerializer


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


def get_viz_data(request, pk):
    data = []
    """stratify format- array of json objects
    # get scholar who's we're centering
    scholar = Scholar.objects.get(aha_scholar_id=pk)
    # get their advisor
    advisor = CommitteeMember.objects.get(dissertation__aha_author_id = pk)
    advisorRoot = {"name": advisor.scholar.name_full, "parent": ""}
    data.append(advisorRoot)
    advisorData = {"name": scholar.name_full, "parent": advisor.scholar.name_full }
    data.append(advisorData)
    #get their advisees
    advisees = CommitteeMember.objects.filter(aha_scholar_id = pk)
    for advisee in advisees:
        adviseeData = {"name": advisee.dissertation.author.name_full, "parent": scholar.name_full}
        data.append(adviseeData)"""
    """Plotly format- array of string literals"""
    # get scholar who's we're centering
    # scholar = Scholar.objects.get(aha_scholar_id=pk)
    scholar = Scholar.objects.get(id=pk)

    # issue- what if scholar does not have a dissertation (only in Db as a Committee Member)
    try:
        dissertation = Dissertation.objects.get(
            author=scholar.id
        )
        has_dissertation = True
    except Dissertation.DoesNotExist:
        dissertation = None
        has_dissertation = False 

    # get advisor if scholar has a dissertation
    advisor = None
    if has_dissertation:
        try:
            #advisor = CommitteeMember.objects.get(dissertation__aha_author_id=pk)
            advisor = CommitteeMember.objects.get(
                dissertation=dissertation,
                role="chair"
            )
        except CommitteeMember.DoesNotExist:
            advisor = None

    advisorData = ""
    # get their advisor
    if advisor != None:
        data.append(advisor.scholar.name_full + "/")
        advisorData = advisor.scholar.name_full + "/" + scholar.name_full + "/"
        data.append(advisorData)
    else:
        # advisorData = '/' + scholar.name_full
        advisorData = scholar.name_full + "/"
        data.append(advisorData)
   
    # get their advisees
    advisees = CommitteeMember.objects.filter(role="chair", scholar=pk)
    if advisees.exists():
        for advisee in advisees:
            adviseeData = advisorData + advisee.dissertation.author.name_full
            data.append(adviseeData)
    
    return JsonResponse(data, safe=False)


def traverse(pk, path, data):
    # root = Scholar.objects.get(aha_scholar_id=pk)
    root = Scholar.objects.get(id=pk)
    path = path + root.name_full + "/"
    
    advisees = CommitteeMember.objects.filter(role="chair", scholar=pk)
    
    if advisees.exists():
        for advisee in advisees:
            if advisee.dissertation and advisee.dissertation.author:
                # traverse(advisee.dissertation.author.aha_scholar_id, path, data)
                traverse(advisee.dissertation.author.id, path, data)
    data.append(path[0:-1])

    # return root.aha_scholar_id, path, data
    return root.id, path, data


def get_viz_data_complex(request, pk):
    data = []
    path = ""
    
    # find root (advisor variable)
    # scholar = Scholar.objects.get(aha_scholar_id=pk)
    scholar = Scholar.objects.get(id=pk)
    
    try:
        # dissertation = Dissertation.objects.get(aha_author_id=scholar.aha_scholar_id)
        dissertation = Dissertation.objects.get(author=scholar.id)
    except Dissertation.DoesNotExist:
        # If no dissertation, scholar is the root
        pk, path, data = traverse(scholar.id, path, data)
        data[-1] = data[-1] + "/"
        return JsonResponse(data, safe=False)
    
    try:
        #advisor = CommitteeMember.objects.get(dissertation__aha_author_id=pk)
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
                #dissertation__aha_author_id=advisor.scholar.aha_scholar_id
                dissertation__author=advisor.scholar,
                role="chair"
            )
        except CommitteeMember.DoesNotExist:
            root = None
        
        if root != None:
            advisor = root
        else:
            break

    # append data here?...no but add to path variable
    if advisor != None:
        # root = advisor.aha_scholar_id
        root = advisor.scholar.id
    else:
        # root = scholar.aha_scholar_id
        root = scholar.id
    # call function...how to save data part of return call?
    pk, path, data = traverse(root, path, data)
    data[-1] = data[-1] + "/"

    return JsonResponse(data, safe=False)


"""@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'scholars': reverse('scholar-list-api', request=request, format=format)
    })"""


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        current_scholar = self.get_object()
        '''
        # get the scholar's advisor
        try:
            context["advisor"] = CommitteeMember.objects.get(
                dissertation__aha_author_id=current_scholar.aha_scholar_id
            )
        except:
            context["advisor"] = "information not available"

        # get the scholar's dissertation
        try:
            context["dissertation"] = Dissertation.objects.get(
                aha_author_id=current_scholar.aha_scholar_id
            )
        except:
            context["dissertation"] = "information not available"'''
        
        try:
            dissertation = Dissertation.objects.get(
                author=current_scholar.id
            )
            context["dissertation"] = dissertation

            try:
                context["advisor"] = CommitteeMember.objects.get(
                    dissertation=dissertation,
                    role="chair"  # Assuming chair = advisor
                )
            except CommitteeMember.DoesNotExist:
                context["advisor"] = "information not available"
            
            try:
                context["dissLink"] = DissertationLink.objects.get(
                    dissertation=dissertation
                )
            except DissertationLink.DoesNotExist:
                context["dissLink"] = "information not available"

        except Dissertation.DoesNotExist:
            context["dissertation"] = "information not available"
            context["advisor"] = "information not available"
                  

        # get the scholar's advisees
        advisees = CommitteeMember.objects.filter(
            role="chair", scholar=current_scholar.id
        )
        context["advisees"] = advisees if advisees.exists() else None

        # get the scholar's websites
        websites = ScholarWebsite.objects.filter(
            scholar=current_scholar.id
        )
        context["websites"] = websites if websites.exists() else None


        return context
