from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

"""urlpatterns = [
    path("", views.index, name="index"),
    path(
        "dissertations/",
        views.DissListView.as_view(),
        name="dissertations",
    ),
]"""

urlpatterns = [
    path("", views.index, name="index"),
    path(
        "dissertations/",
        views.FilteredDissertationListView.as_view(),
        name="dissertations",
    ),
    path(
        "committeemembers/",
        views.FilteredComMemListView.as_view(),
        name="committeemembers",
    ),
    path("dissertations/<int:pk>", views.DissDetailView.as_view(), name="diss-detail"),
    path("scholars/", views.ScholarList.as_view()),
    path("scholars/<int:pk>/", views.ScholarDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
