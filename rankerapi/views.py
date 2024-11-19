from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db import IntegrityError, transaction
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
    permission_classes = [AllowAny]


class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer


class VetoView(APIView):
    def put(self, request, session_code):
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

        try:
            with transaction.atomic():
                session.restaurants.filter(id__in=vetoed_restaurants).update(veto=True)

            return Response(
                {"detail": "Restaurants successfully vetoed."},
                status=status.HTTP_200_OK,
            )

        except IntegrityError as e:
            return Response(
                {
                    "detail": "Database integrity error occurred. Please try again later."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            return Response(
                {"detail": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
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


class RankingView(APIView):
    def put(self, request, session_code):
        try:
            session = Session.objects.get(code=session_code)
            username = request.data.get("username")
            user = SessionUser.objects.get(session_code=session, username=username)

            rankings_data = request.data.get("rankings", {})

            user.rankings = rankings_data
            user.save()

            for restaurant_id, ranking in rankings_data.items():
                try:
                    restaurant = Restaurant.objects.get(id=restaurant_id)
                    restaurant.overall_rank += ranking
                    restaurant.save()
                except Restaurant.DoesNotExist:
                    return Response(
                        {"error": f"Restaurant with ID {restaurant_id} not found"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            return Response(
                {"message": "Rankings updated successfully."}, status=status.HTTP_200_OK
            )

        except Session.DoesNotExist:
            return Response(
                {"error": "Session not found!"}, status=status.HTTP_404_NOT_FOUND
            )
        except SessionUser.DoesNotExist:
            return Response(
                {"error": "User not found in this session."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ResultView(APIView):
    def get(self, request, session_code):
        try:
            session = Session.objects.get(code=session_code)

            restaurants = session.restaurants.all()

            result = [
                {
                    "name": restaurant.name,
                    "rating": restaurant.rating,
                    "overall_rank": restaurant.overall_rank,
                    "photo_url": restaurant.photo_url,
                }
                for restaurant in restaurants
            ]

            return Response(result, status=status.HTTP_200_OK)

        except Session.DoesNotExist:
            return Response(
                {"error": "Session not found!"}, status=status.HTTP_404_NOT_FOUND
            )
