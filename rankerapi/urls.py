from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SessionViewSet, SessionUserViewSet

router = DefaultRouter()
router.register(r"sessions", SessionViewSet)
router.register(r"session-users", SessionUserViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
