from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db import IntegrityError, transaction
from django.db.models import F
from .models import Session, SessionUser, Restaurant
from .serializers import (
    SessionSerializer,
    SessionUserSerializer,
    RestaurantSerializer,
)
from rankerapi import serializers


class SessionViewSet(viewsets.ModelViewSet):
    queryset = Session.objects.all().order_by("created")
    serializer_class = SessionSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["code"]
    permission_classes = [AllowAny]
    lookup_field = "code"

    def perform_create(self, serializer):
        session = serializer.save()
        username = self.request.data.get("username")

        if username:
            SessionUser.objects.create(username=username, session_code=session)
        else:
            raise serializers.ValidationError(
                "Username is required to create a SessionUser."
            )


class SessionUserViewSet(viewsets.ModelViewSet):
    queryset = SessionUser.objects.all()
    serializer_class = SessionUserSerializer
    permission_classes = [AllowAny]


class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer


class JoinSessionView(APIView):
    def post(self, request, session_code, *args, **kwargs):
        username = request.data.get("username")

        if not username:
            return Response(
                {"detail": "Username is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        session = get_object_or_404(Session, code=session_code)

        if SessionUser.objects.filter(session_code=session, username=username).exists():
            return Response(
                {"detail": f"User '{username}' is already part of this session."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        session_user = SessionUser.objects.create(
            username=username,
            session_code=session,
        )

        session_data = SessionSerializer(session).data

        session_data["user"] = SessionUserSerializer(session_user).data

        return Response(session_data, status=status.HTTP_201_CREATED)


class VetoView(APIView):
    def put(self, request, session_code):
        session = get_object_or_404(Session, code=session_code)
        username = request.data.get("username")
        session_user = get_object_or_404(SessionUser, username=username)
        vetoed_restaurants = request.data.get("vetoed_restaurants", [])

        if not vetoed_restaurants:
            updated_restaurants = session.restaurants.all()
            updated_restaurant_data = RestaurantSerializer(
                updated_restaurants, many=True
            ).data
            return Response(
                {
                    "detail": "No restaurants were vetoed.",
                    "restaurants": updated_restaurant_data,
                },
                status=status.HTTP_200_OK,
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
                session.restaurants.filter(id__in=vetoed_restaurants).update(
                    veto=F("veto") + 1
                )
                session_user.vetoes.extend(vetoed_restaurants)
                session_user.save()
                updated_restaurants = session.restaurants.all()
                updated_restaurant_data = RestaurantSerializer(
                    updated_restaurants, many=True
                ).data
            return Response(
                {
                    "detail": "Restaurants successfully vetoed.",
                    "restaurants": updated_restaurant_data,
                },
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


class VetoedView(APIView):
    def get(self, request, session_code):
        try:
            session = Session.objects.get(code=session_code)

            vetoed_restaurant_ids = session.restaurants.filter(veto=True).values_list(
                "id", flat=True
            )

            return Response(vetoed_restaurant_ids, status=status.HTTP_200_OK)

        except Session.DoesNotExist:
            return Response(
                {"error": "Session not found!"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class RankingView(APIView):
    def put(self, request, session_code):
        session = get_object_or_404(Session, code=session_code)
        username = request.data.get("username")
        user = get_object_or_404(SessionUser, username=username)

        try:
            rankings_data = request.data.get("restaurants", [])
            max_rank = max([r.get("rank") for r in rankings_data])

            user_rankings = {}

            for r in rankings_data:
                try:
                    restaurant_id = r.get("id")
                    rank = r.get("rank")

                    normalized_rank = rank / max_rank if max_rank else 0

                    restaurant = Restaurant.objects.get(id=restaurant_id)

                    restaurant.overall_rank += normalized_rank
                    restaurant.save()

                    user_rankings[restaurant_id] = rank
                except Restaurant.DoesNotExist:
                    return Response(
                        {"error": f"Restaurant with ID {restaurant_id} not found"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            user.rankings = user_rankings
            user.save()
            session.ranked_count += 1
            session.save()
            return Response(
                {
                    "message": "Rankings updated successfully.",
                },
                status=status.HTTP_200_OK,
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
            restaurants_data = RestaurantSerializer(restaurants, many=True).data
            return Response(
                {"restaurants": restaurants_data, "ranked": session.ranked_count},
                status=status.HTTP_200_OK,
            )

        except Session.DoesNotExist:
            return Response(
                {"error": "Session not found!"}, status=status.HTTP_404_NOT_FOUND
            )
