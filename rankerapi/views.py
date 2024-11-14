from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from .models import Session, SessionUser, Restaurant
from .serializers import (
    SessionSerializer,
    SessionUserSerializer,
    RestaurantSerializer,
    SessionUserSerializer,
)


class SessionViewSet(viewsets.ModelViewSet):
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


class VetoView(APIView):
    def post(self, request, session_code, *args, **kwargs):
        session = get_object_or_404(Session, code=session_code)

        vetoed_restaurants = request.data.get("vetoed_restaurants", [])

        if not vetoed_restaurants:
            return Response(
                {"detail": "No restaurants were vetoed."},
                status=status.HTTP_204_NO_CONTENT,
            )

        for restaurant_id in vetoed_restaurants:
            restaurant = session.restaurants.get(id=restaurant_id)
            restaurant.veto = True
            restaurant.save()

        return Response(
            {"detail": "Restaurants successfully vetoed."},
            status=status.HTTP_200_OK,
        )
