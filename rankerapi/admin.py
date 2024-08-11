from django.contrib import admin
from .models import Session, SessionUser

# Register your models here.


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ("code", "latitude", "longitude", "created", "restaurants")
    search_fields = ("code",)


@admin.register(SessionUser)
class SessionUserAdmin(admin.ModelAdmin):
    list_display = ("username", "session_code", "rankings")
    search_fields = ("username", "session__code")
    list_filter = ("session_code",)
