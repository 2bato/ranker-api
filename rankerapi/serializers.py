from rest_framework import serializers
from .models import Session, SessionUser, Restaurant


class SessionUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionUser
        fields = ["id", "username", "session", "rankings", "veto"]


class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ["id", "name", "rating", "photo_url"]


class SessionSerializer(serializers.ModelSerializer):
    restaurants = RestaurantSerializer(many=True, read_only=True)

    class Meta:
        model = Session
        fields = [
            "created",
            "code",
            "latitude",
            "longitude",
            "count",
            "restaurants",
        ]
