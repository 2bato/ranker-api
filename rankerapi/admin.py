from django.contrib import admin
from .models import Session

# Register your models here.


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ("code", "latitude", "longitude", "created", "restaurants")
    search_fields = ("code",)
