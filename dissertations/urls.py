from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path(
        "dissertations/",
        views.DissListView.as_view(),
        name="dissertations",
    ),
    path(
        "dissertation/<int:pk>",
        views.DissDetailView.as_view(),
        name="diss-detail",
    ),
]
