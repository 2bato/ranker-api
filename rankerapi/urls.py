from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SessionViewSet, SessionUserViewSet, RestaurantViewSet

router = DefaultRouter()
router.register(r"sessions", SessionViewSet)
router.register(r"session-users", SessionUserViewSet)
router.register(r"restaurants", RestaurantViewSet)


urlpatterns = [
    path("", include(router.urls)),
]
