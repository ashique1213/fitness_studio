from rest_framework import serializers
from .models import FitnessClass, Booking
from django.utils import timezone
import pytz
import re

class FitnessClassSerializer(serializers.ModelSerializer):
    """Serializer for FitnessClass model."""
    date_time = serializers.SerializerMethodField()

    class Meta:
        model = FitnessClass
        fields = ['id', 'name', 'date_time', 'instructor', 'available_slots']

    def get_date_time(self, obj):
        """Convert UTC date_time to requested timezone."""
        request = self.context.get('request')
        tz_name = request.query_params.get('timezone', 'Asia/Kolkata')  # Default to IST
        try:
            tz = pytz.timezone(tz_name)
        except pytz.exceptions.UnknownTimeZoneError:
            raise serializers.ValidationError(f"Invalid timezone: {tz_name}")
        return obj.date_time.astimezone(tz).isoformat()

class BookingSerializer(serializers.ModelSerializer):
    """Serializer for Booking model."""
    class_name = serializers.CharField(source='fitness_class.name', read_only=True)
    class_date_time = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'fitness_class', 'client_name', 'client_email', 'created_at', 'class_name', 'class_date_time']
        read_only_fields = ['created_at', 'class_name', 'class_date_time']

    def get_class_date_time(self, obj):
        """Convert class date_time to requested timezone for bookings."""
        request = self.context.get('request')
        tz_name = request.query_params.get('timezone', 'Asia/Kolkata')
        try:
            tz = pytz.timezone(tz_name)
        except pytz.exceptions.UnknownTimeZoneError:
            raise serializers.ValidationError(f"Invalid timezone: {tz_name}")
        return obj.fitness_class.date_time.astimezone(tz).isoformat()

    def validate(self, data):
        """Validate booking data."""
        fitness_class = data['fitness_class']
        if fitness_class.available_slots <= 0:
            raise serializers.ValidationError("No slots available for this class.")
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', data['client_email']):
            raise serializers.ValidationError("Invalid email format.")
        return data