from django.contrib import admin
from .models import Session, SessionUser, Restaurant


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ("code", "latitude", "longitude", "created")
    search_fields = ("code",)


@admin.register(SessionUser)
class SessionUserAdmin(admin.ModelAdmin):
    list_display = ("username", "session_code", "rankings")
    search_fields = ("username", "session__code")
    list_filter = ("session_code",)


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "rating",
        "photo_url",
        "veto",
        "session",
    )
    search_fields = (
        "name",
        "session__code",
    )
    list_filter = ("session", "veto")
