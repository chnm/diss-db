from django.urls import path, include
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

# router = routers.DefaultRouter()
# router.register(r'scholarsapi', views.ScholarViewSet)

urlpatterns = [
    path("", views.index, name="index"),
    path("about/", views.about, name="about"),
    path("contributing/", views.contributing, name="contributing"),
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
    # path("dissertations/<int:pk>", views.DissDetailView.as_view(), name="diss-detail"),
    path('scholar/<int:pk>/edit/', views.ScholarUpdateView.as_view(), name='scholar-edit'),
    path('dissertation/<int:pk>/edit/', views.DissertationUpdateView.as_view(), name='dissertation-edit'),
    path('scholar/<int:pk>/add-dissertation/', views.DissertationCreateView.as_view(), name='dissertation-create'),
    path("scholar/<int:pk>/<slug:slug>/", views.ScholarDetailView.as_view(), name="scholar-detail"),
    path('scholars/', views.FilteredScholarListView.as_view(), name='scholars'),
    path('scholars/create/', views.ScholarCreateView.as_view(), name='scholar-create'),
    path('scholars/api/', views.ScholarListAPI.as_view(), name='scholar-list-api'),
    path('scholars/api/create/', views.ScholarCreateAPI.as_view(), name='scholar-create-api'),
    path('scholars/api/<int:pk>/', views.ScholarDetailAPI.as_view()),
    path('api/get_viz_data/<int:pk>', views.get_viz_data, name="get_viz_data"),
    path('api/get_viz_data_complex/<int:pk>', views.get_viz_data_complex, name="get_viz_data_complex"),
    # path("scholarsapi/<int:pk>/", views.ScholarDetail.as_view()),
    # path('', include(router.urls)),
    # path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]

urlpatterns = format_suffix_patterns(urlpatterns)
