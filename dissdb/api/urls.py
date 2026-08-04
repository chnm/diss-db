from rest_framework.routers import DefaultRouter

from . import views

app_name = "apiv1"

router = DefaultRouter()
router.register("dissertations", views.DissertationViewSet, basename="dissertation")
router.register("scholars", views.ScholarViewSet, basename="scholar")

urlpatterns = router.urls
