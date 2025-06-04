from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
import logging
from .models import FitnessClass, Booking
from .serializers import FitnessClassSerializer, BookingSerializer

logger = logging.getLogger('api')

class ClassListView(APIView):
    """List all upcoming fitness classes."""
    def get(self, request):
        tz_name = request.query_params.get('timezone', 'Asia/Kolkata')
        classes = FitnessClass.objects.filter(date_time__gte=timezone.now())
        serializer = FitnessClassSerializer(classes, many=True, context={'request': request})
        logger.info(f"Retrieved {len(classes)} classes for timezone: {tz_name}")
        return Response(serializer.data)

class BookingCreateView(APIView):
    """Create a new booking for a fitness class."""
    def post(self, request):
        serializer = BookingSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            fitness_class = serializer.validated_data['fitness_class']
            if fitness_class.available_slots > 0:
                fitness_class.available_slots -= 1
                fitness_class.save()
                serializer.save()
                logger.info(f"Booking created for {serializer.validated_data['client_email']} in class {fitness_class.id}")
                return Response({"message": "Booking successful"}, status=status.HTTP_201_CREATED)
            logger.error(f"Booking failed: No slots available for class {fitness_class.id}")
            return Response({"error": "No slots available"}, status=status.HTTP_400_BAD_REQUEST)
        logger.error(f"Booking failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BookingListView(APIView):
    """List all bookings for a given client email."""
    def get(self, request):
        email = request.query_params.get('email')
        if not email:
            logger.error("Booking list failed: Email parameter missing")
            return Response({"error": "Email parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
        bookings = Booking.objects.filter(client_email=email)
        serializer = BookingSerializer(bookings, many=True, context={'request': request})
        logger.info(f"Retrieved {len(bookings)} bookings for {email}")
        return Response(serializer.data)