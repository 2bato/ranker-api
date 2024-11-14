from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SessionViewSet, SessionUserViewSet, RestaurantViewSet, VetoView

router = DefaultRouter()
router.register(r"sessions", SessionViewSet)
router.register(r"session-users", SessionUserViewSet)
router.register(r"restaurants", RestaurantViewSet)


urlpatterns = [
    path("", include(router.urls)),
    path(
        "sessions/<str:session_code>/veto/",
        VetoView.as_view(),
        name="veto",
    ),
]