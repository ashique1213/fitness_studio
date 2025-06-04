from django.test import TestCase
from rest_framework.test import APIClient
from django.utils import timezone
import pytz
from .models import FitnessClass, Booking

class APITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.fitness_class = FitnessClass.objects.create(
            name="Yoga",
            date_time=timezone.now() + timezone.timedelta(hours=1),
            instructor="John Doe",
            total_slots=10,
            available_slots=10
        )

    def test_get_classes(self):
        response = self.client.get('/api/classes/?timezone=Asia/Kolkata')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Yoga")
        self.assertEqual(response.data[0]['instructor'], "John Doe")

    def test_create_booking(self):
        data = {
            "fitness_class": self.fitness_class.id,
            "client_name": "Alice",
            "client_email": "alice@example.com"
        }
        response = self.client.post('/api/book/', data, format='json')
        self.assertEqual(response.status_code, 201)
        self.fitness_class.refresh_from_db()
        self.assertEqual(self.fitness_class.available_slots, 9)

    def test_create_booking_no_slots(self):
        self.fitness_class.available_slots = 0
        self.fitness_class.save()
        data = {
            "fitness_class": self.fitness_class.id,
            "client_name": "Bob",
            "client_email": "bob@example.com"
        }
        response = self.client.post('/api/book/', data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("No slots available for this class.", response.data['non_field_errors'][0])

    def test_create_booking_invalid_email(self):
        data = {
            "fitness_class": self.fitness_class.id,
            "client_name": "Bob",
            "client_email": "invalid-email"
        }
        response = self.client.post('/api/book/', data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("Enter a valid email address.", response.data['client_email'][0])

    def test_get_bookings(self):
        Booking.objects.create(
            fitness_class=self.fitness_class,
            client_name="Alice",
            client_email="alice@example.com"
        )
        response = self.client.get('/api/bookings/?email=alice@example.com')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['client_name'], "Alice")
        self.assertEqual(response.data[0]['class_name'], "Yoga")

    def test_get_bookings_no_email(self):
        response = self.client.get('/api/bookings/')
        self.assertEqual(response.status_code, 400)
        self.assertIn("Email parameter is required", response.data['error'])