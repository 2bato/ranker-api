from rest_framework import serializers
from .models import Session, SessionUser


class SessionUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionUser
        fields = ["id", "username", "rankings"]


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = [
            "id",
            "created",
            "code",
            "latitude",
            "longitude",
            "count",
            "restaurants",
        ]
