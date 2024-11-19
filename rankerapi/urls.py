from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    JoinSessionView,
    SessionViewSet,
    SessionUserViewSet,
    RestaurantViewSet,
    VetoView,
    VetoedView,
    RankingView,
    ResultView,
)

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
    path(
        "sessions/<str:session_code>/vetoed/",
        VetoedView.as_view(),
        name="vetoed",
    ),
    path(
        "sessions/<str:session_code>/ranking/",
        RankingView.as_view(),
        name="ranking",
    ),
    path("sessions/<str:session_code>/result/", ResultView.as_view(), name="result"),
    path("sessions/<str:session_code>/join/", JoinSessionView.as_view(), name="join"),
]
