import os
import django
import sys

# Setup Django
sys.path.append(
    "/Users/aslan/Desktop/DACNIS/Fielmedina/Developments/fielmedina_web/backend"
)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from guard.models import Ad, Event


def check_duplicates():
    ads = Ad.objects.filter(short_id__isnull=False)
    events = Event.objects.filter(short_id__isnull=False)

    short_ids = {}

    print("Checking Ads...")
    for ad in ads:
        sid = ad.short_id
        if sid in short_ids:
            print(f"DUPLICATE FOUND: {sid} used in Ad ID {ad.id} and {short_ids[sid]}")
        else:
            short_ids[sid] = f"Ad ID {ad.id}"

    print("Checking Events...")
    for event in events:
        sid = event.short_id
        if sid in short_ids:
            print(
                f"DUPLICATE FOUND: {sid} used in Event ID {event.id} and {short_ids[sid]}"
            )
        else:
            short_ids[sid] = f"Event ID {event.id}"

    print("Check complete.")


if __name__ == "__main__":
    check_duplicates()
