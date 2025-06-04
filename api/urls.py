from django.urls import path
from .views import ClassListView, BookingCreateView, BookingListView

urlpatterns = [
    path('classes/', ClassListView.as_view(), name='class-list'),
    path('book/', BookingCreateView.as_view(), name='book-create'),
    path('bookings/', BookingListView.as_view(), name='booking-list'),
]