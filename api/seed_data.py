from django.utils import timezone
import pytz
from api.models import FitnessClass

def seed_data():
    """Create sample fitness classes for testing."""
    classes = [
        {
            "name": "Yoga",
            "date_time": timezone.now() + timezone.timedelta(days=1),
            "instructor": "John Doe",
            "total_slots": 10,
            "available_slots": 10
        },
        {
            "name": "Zumba",
            "date_time": timezone.now() + timezone.timedelta(days=2),
            "instructor": "Jane Smith",
            "total_slots": 15,
            "available_slots": 15
        },
        {
            "name": "HIIT",
            "date_time": timezone.now() + timezone.timedelta(days=3),
            "instructor": "Mike Brown",
            "total_slots": 8,
            "available_slots": 8
        },
    ]
    for cls in classes:
        FitnessClass.objects.create(**cls)
    print("Seed data created successfully!")