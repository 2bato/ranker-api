from rest_framework import viewsets, filters
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from .models import Session, SessionUser, Restaurant
from .serializers import SessionSerializer, SessionUserSerializer, RestaurantSerializer


class SessionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows sessions to be viewed or edited.
    """

    queryset = Session.objects.all().order_by("created")
    serializer_class = SessionSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["code"]
    permission_classes = [AllowAny]
    lookup_field = "code"


class SessionUserViewSet(viewsets.ModelViewSet):
    queryset = SessionUser.objects.all()
    serializer_class = SessionUserSerializer


class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
