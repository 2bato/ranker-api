from rest_framework import serializers
from .models import Session, SessionUser, Restaurant


class SessionUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionUser
        fields = ["id", "username", "session", "rankings"]


class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ["id", "name", "rating", "photo_url", "overall_rank", "veto"]


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


class SessionUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionUser
        fields = ["id", "username", "session_code", "rankings"]

    def validate_rankings(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Rankings must be a dictionary.")
        return value
