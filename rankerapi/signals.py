from django.db.models.signals import post_save
from django.dispatch import receiver
import requests
import random
from .models import Session, Restaurant
from dotenv import load_dotenv
import os


@receiver(post_save, sender=Session)
def session_post_save(sender, instance, created, **kwargs):
    if created:
        load_dotenv()

        location = {"latitude": instance.latitude, "longitude": instance.longitude}
        api_key = os.getenv("GOOGLE_API_KEY")

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
            "X-Goog-FieldMask": "places.displayName,places.rating,places.priceLevel,places.businessStatus,places.types,places.photos,places.currentOpeningHours",
        }

        try:
            response = requests.post(
                "https://places.googleapis.com/v1/places:searchNearby",
                json=request_payload,
                headers=headers,
                verify=False,
            )

            if response.status_code != 200:
                raise Exception(f"Error: {response.status_code}")

            data = response.json()

            places = data.get("places", [])
            for place in places:
                current_opening_hours = place.get("currentOpeningHours", {})
                open_now = current_opening_hours.get("openNow", False)
                name = place.get("displayName", {}).get("text", "Unnamed Restaurant")
                rating = place.get("rating")
                if (
                    open_now
                    and "photos" in place
                    and len(place["photos"]) > 0
                    and rating > 0
                    and name != "Unnamed Restaurant"
                ):
                    temp_url = place["photos"][0]["name"]
                    index = temp_url.find("photos/")

                    if index != -1:
                        photo_reference = temp_url[index + len("photos/") :]
                    photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_reference}&key={api_key}"

                    restaurant, created = Restaurant.objects.get_or_create(
                        name=name,
                        defaults={
                            "rating": rating,
                            "photo_url": photo_url,
                            "overall_rank": 0,
                        },
                    )

                    instance.restaurants.add(restaurant)
            instance.count = instance.restaurants.count()
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
