from django.db import models


# Create your models here.
class Session(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    code = models.CharField(max_length=10, unique=True, blank=False)
    latitude = models.FloatField()
    longitude = models.FloatField()
    restaurants = models.JSONField(default=list)

    def __str__(self):
        return self.code
