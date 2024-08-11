from django.db.models.signals import post_save
from django.dispatch import receiver
import requests
import random
from .models import Session


class Restaurant:
    def __init__(self, display_name, photo_url, rating, success):
        self.display_name = display_name
        self.photo_url = photo_url
        self.rating = rating
        self.success = success


@receiver(post_save, sender=Session)
def session_post_save(sender, instance, created, **kwargs):
    if created:

        location = {"latitude": instance.latitude, "longitude": instance.longitude}
        api_key = "AIzaSyAXpRKeA6lCOiYOwwnJbx7j9GUvBig8MLw"

        request_payload = {
            "includedTypes": ["restaurant"],
            "maxResultCount": 20,
            "locationRestriction": {
                "circle": {
                    "center": {
                        "latitude": location["latitude"],
                        "longitude": location["longitude"],
                    },
                    "radius": 1000,
                }
            },
        }

        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": "places.displayName,places.rating,places.priceLevel,places.businessStatus,places.types,places.photos",
        }

        try:
            response = requests.post(
                "https://places.googleapis.com/v1/places:searchNearby",
                json=request_payload,
                headers=headers,
            )

            if response.status_code != 200:
                raise Exception(f"Error: {response.status_code}")

            data = response.json()

            instance.restaurants = data.get("places", [])
            print(len(instance.restaurants))
            instance.count = len(instance.restaurants)
            instance.save()
            # filtered_data = places_data

            # filtered_data = [
            #     place
            #     for place in filtered_data
            #     if place.get("priceLevel") in ["$", "$$"]
            # ]
            # if not filtered_data:
            #     # No restaurants found, handle accordingly
            #     return

            # random_place = random.choice(places_data)
            # photo_reference = random_place["photos"][0]["photoReference"]
            # image_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_reference}&key={api_key}"

        except Exception as e:
            print(f"Error fetching nearby places: {e}")
