from django.db import models
from django.core.validators import EmailValidator

class FitnessClass(models.Model):
    """Model representing a fitness class."""
    name = models.CharField(max_length=100)
    date_time = models.DateTimeField()  # Stored in UTC
    instructor = models.CharField(max_length=100)
    total_slots = models.PositiveIntegerField()
    available_slots = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.name} at {self.date_time}"

class Booking(models.Model):
    """Model representing a booking for a fitness class."""
    fitness_class = models.ForeignKey(FitnessClass, on_delete=models.CASCADE, related_name='bookings')
    client_name = models.CharField(max_length=100)
    client_email = models.EmailField(validators=[EmailValidator()])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.client_name} booked {self.fitness_class.name}"