from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db import transaction
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

        invalid_restaurants = [
            restaurant_id
            for restaurant_id in vetoed_restaurants
            if not session.restaurants.filter(id=restaurant_id).exists()
        ]

        if invalid_restaurants:
            return Response(
                {
                    "detail": f"Invalid restaurant IDs: {', '.join(map(str, invalid_restaurants))}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            session.restaurants.filter(id__in=vetoed_restaurants).update(veto=True)

        return Response(
            {"detail": "Restaurants successfully vetoed."},
            status=status.HTTP_200_OK,
        )


class NonVetoedView(APIView):
    def get(self, request, session_code):
        try:
            session = Session.objects.get(code=session_code)

            non_vetoed_restaurants = session.restaurants.filter(veto=False)

            restaurant_data = [
                {
                    "id": restaurant.id,
                    "name": restaurant.name,
                    "photo_url": restaurant.photo_url,
                    "rating": restaurant.rating,
                }
                for restaurant in non_vetoed_restaurants
            ]

            return Response(restaurant_data, status=status.HTTP_200_OK)

        except Session.DoesNotExist:
            return Response(
                {"error": "Session not found!"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
