from rest_framework import serializers
from .models import Session, SessionUser, Restaurant


class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ["id", "name", "rating", "photo_url", "overall_rank", "veto"]


class SessionUserSerializer(serializers.ModelSerializer):
    session_code = serializers.SlugRelatedField(
        slug_field="code", queryset=Session.objects.all()
    )

    class Meta:
        model = SessionUser
        fields = ["id", "username", "session_code", "rankings", "vetoes"]

    def validate_rankings(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Rankings must be a dictionary.")
        return value


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
