from django.db import models


# Create your models here.
class Session(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    code = models.CharField(primary_key=True, max_length=10, unique=True, blank=False)
    latitude = models.FloatField()
    longitude = models.FloatField()
    restaurants = models.ManyToManyField("Restaurant", blank=True)
    count = models.IntegerField(default=0)

    def __str__(self):
        return self.code

    @property
    def users(self):
        return self.sessionuser_set.all()


class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    photo_url = models.URLField(blank=True)
    rating = models.FloatField()
    veto = models.BooleanField(default=False)
    overall_rank = models.FloatField(default=0)
    def __str__(self):
        return self.name


class SessionUser(models.Model):
    username = models.CharField(max_length=100, blank=False)
    session_code = models.ForeignKey(
        Session, related_name="users", on_delete=models.CASCADE
    )
    rankings = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.username
