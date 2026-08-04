from django.urls import include, path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

# router = routers.DefaultRouter()
# router.register(r'scholarsapi', views.ScholarViewSet)

urlpatterns = [
    path("", views.index, name="index"),
    path("search/", views.search, name="search"),
    path("about/", views.about, name="about"),
    path("contributing/", views.contributing, name="contributing"),
    path("network_viz/", views.network_viz, name="network_viz"),
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
    path("dissertations/<int:pk>/", views.diss_detail_redirect, name="diss-detail"),
    path(
        "scholar/<int:pk>/edit/", views.ScholarUpdateView.as_view(), name="scholar-edit"
    ),
    path(
        "dissertation/<int:pk>/edit/",
        views.DissertationUpdateView.as_view(),
        name="dissertation-edit",
    ),
    path(
        "scholar/<int:pk>/add-dissertation/",
        views.DissertationCreateView.as_view(),
        name="dissertation-create",
    ),
    path(
        "scholar/<int:pk>/<slug:slug>/",
        views.ScholarDetailView.as_view(),
        name="scholar-detail",
    ),
    path("scholars/", views.FilteredScholarListView.as_view(), name="scholars"),
    path("scholars/create/", views.ScholarCreateView.as_view(), name="scholar-create"),
    path("scholars/api/", views.ScholarListAPI.as_view(), name="scholar-list-api"),
    path(
        "scholars/api/create/",
        views.ScholarCreateAPI.as_view(),
        name="scholar-create-api",
    ),
    path("scholars/api/<int:pk>/", views.ScholarDetailAPI.as_view()),
    path("api/get_viz_data/<int:pk>", views.get_viz_data, name="get_viz_data"),
    path(
        "api/get_viz_data_complex/<int:pk>",
        views.get_viz_data_complex,
        name="get_viz_data_complex",
    ),
    path(
        "api/school-network/<int:school_id>/",
        views.get_school_network_data,
        name="school-network-data",
    ),
    path("api/departments/", views.department_list_api, name="department-list-api"),
    path(
        "api/departments/create/",
        views.department_create_api,
        name="department-create-api",
    ),
    # path("scholarsapi/<int:pk>/", views.ScholarDetail.as_view()),
    # path('', include(router.urls)),
    # path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]

urlpatterns = format_suffix_patterns(urlpatterns)

# Public read-only API (v1) + its human-readable documentation page.
# Kept out of format_suffix_patterns above; the DRF router handles suffixes.
urlpatterns += [
    path("api/", views.api_docs, name="api"),
    path("api/v1/", include("dissdb.api.urls")),
]
