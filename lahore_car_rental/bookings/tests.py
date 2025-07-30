import json
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from datetime import datetime, timedelta
from unittest.mock import patch

from .models import Booking
from .serializers import BookingSerializer
from vehicles.models import Vehicle


class BookingModelTest(TestCase):
    """Test cases for the Booking model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        self.vehicle = Vehicle.objects.create(
            user=self.user,
            make='Toyota',
            model='Camry',
            year=2020,
            plate='ABC123'
        )
        self.now = timezone.now()
        self.future_start = self.now + timedelta(hours=2)
        self.future_end = self.now + timedelta(hours=4)

    def test_valid_booking_creation(self):
        """Test creating a valid booking"""
        booking = Booking.objects.create(
            vehicle=self.vehicle,
            user=self.user,
            start_date=self.future_start,
            end_date=self.future_end
        )
        self.assertEqual(booking.vehicle, self.vehicle)
        self.assertEqual(booking.user, self.user)
        self.assertEqual(booking.start_date, self.future_start)
        self.assertEqual(booking.end_date, self.future_end)

    def test_end_date_before_start_date_validation(self):
        """Test validation when end date is before start date"""
        with self.assertRaises(ValidationError) as context:
            booking = Booking(
                vehicle=self.vehicle,
                user=self.user,
                start_date=self.future_end,
                end_date=self.future_start
            )
            booking.full_clean()

        self.assertIn('end_date', context.exception.error_dict)
        self.assertIn('End date must be after start date',
                      str(context.exception))

    def test_start_date_in_past_validation(self):
        """Test validation when start date is in the past"""
        past_date = self.now - timedelta(hours=1)
        with self.assertRaises(ValidationError) as context:
            booking = Booking(
                vehicle=self.vehicle,
                user=self.user,
                start_date=past_date,
                end_date=self.future_end
            )
            booking.full_clean()

        self.assertIn('start_date', context.exception.error_dict)
        self.assertIn('at least 1 hour(s) in the future', str(context.exception))

    def test_minimum_duration_validation(self):
        """Test validation for minimum booking duration"""
        start = self.future_start
        end = start + timedelta(minutes=30)  # Less than 1 hour

        with self.assertRaises(ValidationError) as context:
            booking = Booking(
                vehicle=self.vehicle,
                user=self.user,
                start_date=start,
                end_date=end
            )
            booking.full_clean()

        self.assertIn('end_date', context.exception.error_dict)
        self.assertIn('at least 1 hour', str(context.exception))

    def test_maximum_duration_validation(self):
        """Test validation for maximum booking duration"""
        start = self.future_start
        end = start + timedelta(days=35)  # More than 30 days

        with self.assertRaises(ValidationError) as context:
            booking = Booking(
                vehicle=self.vehicle,
                user=self.user,
                start_date=start,
                end_date=end
            )
            booking.full_clean()

        self.assertIn('end_date', context.exception.error_dict)
        self.assertIn('cannot exceed 30 days', str(context.exception))

    def test_overlapping_booking_validation(self):
        """Test validation for overlapping bookings"""
        # Create first booking
        Booking.objects.create(
            vehicle=self.vehicle,
            user=self.user,
            start_date=self.future_start,
            end_date=self.future_end
        )

        # Try to create overlapping booking
        overlapping_start = self.future_start + timedelta(hours=1)
        overlapping_end = self.future_end + timedelta(hours=1)

        with self.assertRaises(ValidationError) as context:
            booking = Booking(
                vehicle=self.vehicle,
                user=self.user2,
                start_date=overlapping_start,
                end_date=overlapping_end
            )
            booking.full_clean()

        self.assertIn('vehicle', context.exception.error_dict)
        self.assertIn('already booked', str(context.exception))

    def test_non_overlapping_booking_valid(self):
        """Test that non-overlapping bookings are valid"""
        # Create first booking
        Booking.objects.create(
            vehicle=self.vehicle,
            user=self.user,
            start_date=self.future_start,
            end_date=self.future_end
        )

        # Create non-overlapping booking (after the first one)
        non_overlapping_start = self.future_end + timedelta(hours=1)
        non_overlapping_end = non_overlapping_start + timedelta(hours=2)

        booking = Booking.objects.create(
            vehicle=self.vehicle,
            user=self.user2,
            start_date=non_overlapping_start,
            end_date=non_overlapping_end
        )

        self.assertEqual(booking.vehicle, self.vehicle)
        self.assertEqual(booking.user, self.user2)

    def test_is_past_property(self):
        """Test the is_past property"""
        past_start = self.now - timedelta(hours=4)
        past_end = self.now - timedelta(hours=2)

        # Create a past booking by bypassing validation
        booking = Booking(
            vehicle=self.vehicle,
            user=self.user,
            start_date=past_start,
            end_date=past_end
        )
        self.assertTrue(booking.is_past)

    def test_is_current_property(self):
        """Test the is_current property"""
        current_start = self.now - timedelta(hours=1)
        current_end = self.now + timedelta(hours=1)

        # Create a current booking by bypassing validation
        booking = Booking(
            vehicle=self.vehicle,
            user=self.user,
            start_date=current_start,
            end_date=current_end
        )
        self.assertTrue(booking.is_current)

    def test_is_future_property(self):
        """Test the is_future property"""
        booking = Booking.objects.create(
            vehicle=self.vehicle,
            user=self.user,
            start_date=self.future_start,
            end_date=self.future_end
        )
        self.assertTrue(booking.is_future)


class BookingSerializerTest(TestCase):
    """Test cases for the BookingSerializer"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.vehicle = Vehicle.objects.create(
            user=self.user,
            make='Toyota',
            model='Camry',
            year=2020,
            plate='ABC123'
        )
        self.now = timezone.now()
        self.future_start = self.now + timedelta(hours=2)
        self.future_end = self.now + timedelta(hours=4)

    def test_valid_serializer_data(self):
        """Test serializer with valid data"""
        data = {
            'vehicle': self.vehicle.id,
            'start_date': self.future_start.isoformat(),
            'end_date': self.future_end.isoformat()
        }
        serializer = BookingSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_vehicle_id(self):
        """Test serializer with invalid vehicle ID"""
        data = {
            'vehicle': 999,  # Non-existent vehicle
            'start_date': self.future_start.isoformat(),
            'end_date': self.future_end.isoformat()
        }
        serializer = BookingSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('vehicle', serializer.errors)
        self.assertIn('does not exist', str(serializer.errors['vehicle']))

    def test_invalid_vehicle_type(self):
        """Test serializer with invalid vehicle type"""
        data = {
            'vehicle': 'invalid',  # Should be integer
            'start_date': self.future_start.isoformat(),
            'end_date': self.future_end.isoformat()
        }
        serializer = BookingSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('vehicle', serializer.errors)

    def test_missing_required_fields(self):
        """Test serializer with missing required fields"""
        data = {}
        serializer = BookingSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('vehicle', serializer.errors)
        self.assertIn('start_date', serializer.errors)
        self.assertIn('end_date', serializer.errors)

    def test_user_field_read_only(self):
        """Test that user field is read-only"""
        data = {
            'vehicle': self.vehicle.id,
            'user': self.user.id,
            'start_date': self.future_start.isoformat(),
            'end_date': self.future_end.isoformat()
        }
        serializer = BookingSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        # User should not be included in validated_data
        self.assertNotIn('user', serializer.validated_data)

    def test_serializer_representation(self):
        """Test serializer representation of booking"""
        booking = Booking.objects.create(
            vehicle=self.vehicle,
            user=self.user,
            start_date=self.future_start,
            end_date=self.future_end
        )
        serializer = BookingSerializer(booking)
        data = serializer.data

        self.assertEqual(data['vehicle'], self.vehicle.id)
        self.assertEqual(data['user'], self.user.id)
        self.assertIn('start_date', data)
        self.assertIn('end_date', data)


class BookingViewTest(APITestCase):
    """Test cases for the BookingListCreateView"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        self.vehicle = Vehicle.objects.create(
            user=self.user,
            make='Toyota',
            model='Camry',
            year=2020,
            plate='ABC123'
        )
        self.vehicle2 = Vehicle.objects.create(
            user=self.user2,
            make='Honda',
            model='Civic',
            year=2019,
            plate='XYZ789'
        )
        self.client = APIClient()
        self.url = reverse('booking-list-create')
        self.now = timezone.now()
        self.future_start = self.now + timedelta(hours=2)
        self.future_end = self.now + timedelta(hours=4)

    def test_list_bookings_unauthenticated(self):
        """Test that unauthenticated users cannot list bookings"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_booking_unauthenticated(self):
        """Test that unauthenticated users cannot create bookings"""
        data = {
            'vehicle': self.vehicle.id,
            'start_date': self.future_start.isoformat(),
            'end_date': self.future_end.isoformat()
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_user_bookings(self):
        """Test listing bookings for authenticated user"""
        self.client.force_authenticate(user=self.user)

        # Create bookings for both users
        Booking.objects.create(
            vehicle=self.vehicle,
            user=self.user,
            start_date=self.future_start,
            end_date=self.future_end
        )

        user2_start = self.future_start + timedelta(days=1)
        user2_end = self.future_end + timedelta(days=1)
        Booking.objects.create(
            vehicle=self.vehicle2,
            user=self.user2,
            start_date=user2_start,
            end_date=user2_end
        )

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only user1's booking
        self.assertEqual(response.data[0]['vehicle'], self.vehicle.id)

    def test_create_valid_booking(self):
        """Test creating a valid booking"""
        self.client.force_authenticate(user=self.user)

        data = {
            'vehicle': self.vehicle.id,
            'start_date': self.future_start.isoformat(),
            'end_date': self.future_end.isoformat()
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify booking was created
        booking = Booking.objects.get(id=response.data['vehicle'])
        self.assertEqual(booking.user, self.user)
        self.assertEqual(booking.vehicle, self.vehicle)

    def test_create_overlapping_booking(self):
        """Test creating overlapping booking returns error"""
        self.client.force_authenticate(user=self.user)

        # Create first booking
        Booking.objects.create(
            vehicle=self.vehicle,
            user=self.user,
            start_date=self.future_start,
            end_date=self.future_end
        )

        # Try to create overlapping booking
        overlapping_start = self.future_start + timedelta(hours=1)
        overlapping_end = self.future_end + timedelta(hours=1)

        data = {
            'vehicle': self.vehicle.id,
            'start_date': overlapping_start.isoformat(),
            'end_date': overlapping_end.isoformat()
        }
        
        

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('already booked', str(response.data))

    def test_create_booking_invalid_data(self):
        """Test creating booking with invalid data"""
        self.client.force_authenticate(user=self.user)

        data = {
            'vehicle': 999,  # Non-existent vehicle
            'start_date': self.future_start.isoformat(),
            'end_date': self.future_end.isoformat()
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('vehicle', response.data)

    def test_filter_bookings_by_from_date(self):
        """Test filtering bookings by from date"""
        self.client.force_authenticate(user=self.user)

        # Create bookings on different dates
        early_start = self.future_start
        early_end = self.future_end
        Booking.objects.create(
            vehicle=self.vehicle,
            user=self.user,
            start_date=early_start,
            end_date=early_end
        )

        late_start = self.future_start + timedelta(days=2)
        late_end = self.future_end + timedelta(days=2)
        Booking.objects.create(
            vehicle=self.vehicle2,
            user=self.user,
            start_date=late_start,
            end_date=late_end
        )

        # Filter by from date (should only return later booking)
        filter_date = (self.future_start + timedelta(days=1)).date()
        response = self.client.get(self.url, {'from': filter_date.isoformat()})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['vehicle'], self.vehicle2.id)

    def test_filter_bookings_by_to_date(self):
        """Test filtering bookings by to date"""
        self.client.force_authenticate(user=self.user)

        # Create bookings on different dates
        early_start = self.future_start
        early_end = self.future_end
        Booking.objects.create(
            vehicle=self.vehicle,
            user=self.user,
            start_date=early_start,
            end_date=early_end
        )

        late_start = self.future_start + timedelta(days=2)
        late_end = self.future_end + timedelta(days=2)
        Booking.objects.create(
            vehicle=self.vehicle2,
            user=self.user,
            start_date=late_start,
            end_date=late_end
        )

        # Filter by to date (should only return earlier booking)
        filter_date = (self.future_end + timedelta(days=1)).date()
        response = self.client.get(self.url, {'to': filter_date.isoformat()})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['vehicle'], self.vehicle.id)

    def test_filter_bookings_invalid_date_format(self):
        """Test filtering with invalid date format"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url, {'from': 'invalid-date'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Invalid date format', str(response.data))

    def test_filter_bookings_invalid_date(self):
        """Test filtering with invalid date"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url, {'from': '2025-10-99'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Invalid date format', str(response.data))

    def test_filter_bookings_date_range(self):
        """Test filtering bookings by date range"""
        self.client.force_authenticate(user=self.user)

        # Create bookings on different dates
        early_start = self.future_start
        early_end = self.future_end
        Booking.objects.create(
            vehicle=self.vehicle,
            user=self.user,
            start_date=early_start,
            end_date=early_end
        )

        middle_start = self.future_start + timedelta(days=1)
        middle_end = self.future_end + timedelta(days=1)
        Booking.objects.create(
            vehicle=self.vehicle2,
            user=self.user,
            start_date=middle_start,
            end_date=middle_end
        )

        late_start = self.future_start + timedelta(days=3)
        late_end = self.future_end + timedelta(days=3)
        vehicle3 = Vehicle.objects.create(
            user=self.user,
            make='Ford',
            model='Focus',
            year=2018,
            plate='DEF456'
        )
        Booking.objects.create(
            vehicle=vehicle3,
            user=self.user,
            start_date=late_start,
            end_date=late_end
        )

        # Filter by date range (should only return middle booking)
        from_date = middle_start.date()
        to_date = middle_end.date()

        response = self.client.get(self.url, {
            'from': from_date.isoformat(),
            'to': to_date.isoformat()
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['vehicle'], self.vehicle2.id)


class BookingIntegrationTest(APITestCase):
    """Integration tests for the booking workflow"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.vehicle = Vehicle.objects.create(
            user=self.user,
            make='Toyota',
            model='Camry',
            year=2020,
            plate='ABC123'
        )
        self.client = APIClient()
        self.url = reverse('booking-list-create')
        self.now = timezone.now()

    def test_complete_booking_workflow(self):
        """Test the complete booking workflow"""
        self.client.force_authenticate(user=self.user)

        # 1. List bookings (should be empty initially)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

        # 2. Create a booking
        future_start = self.now + timedelta(hours=2)
        future_end = self.now + timedelta(hours=4)

        booking_data = {
            'vehicle': self.vehicle.id,
            'start_date': future_start.isoformat(),
            'end_date': future_end.isoformat()
        }

        response = self.client.post(self.url, booking_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 3. List bookings again (should have one booking)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        # 4. Try to create overlapping booking (should fail)
        overlapping_data = {
            'vehicle': self.vehicle.id,
            'start_date': (future_start + timedelta(hours=1)).isoformat(),
            'end_date': (future_end + timedelta(hours=1)).isoformat()
        }

        response = self.client.post(self.url, overlapping_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # 5. Create non-overlapping booking (should succeed)
        non_overlapping_data = {
            'vehicle': self.vehicle.id,
            'start_date': (future_end + timedelta(hours=1)).isoformat(),
            'end_date': (future_end + timedelta(hours=3)).isoformat()
        }

        response = self.client.post(self.url, non_overlapping_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 6. Final list should have two bookings
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_booking_validation_edge_cases(self):
        """Test booking validation edge cases"""
        self.client.force_authenticate(user=self.user)

        # Test booking exactly 1 hour in the future (should pass)
        start_time = self.now + \
            timedelta(hours=1, minutes=1)  # Just over 1 hour
        end_time = start_time + timedelta(hours=1)

        data = {
            'vehicle': self.vehicle.id,
            'start_date': start_time.isoformat(),
            'end_date': end_time.isoformat()
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Test booking exactly 30 days duration (should pass)
        long_start = self.now + timedelta(hours=2)
        long_end = long_start + timedelta(days=30)

        vehicle2 = Vehicle.objects.create(
            user=self.user,
            make='Honda',
            model='Civic',
            year=2019,
            plate='XYZ789'
        )

        long_data = {
            'vehicle': vehicle2.id,
            'start_date': long_start.isoformat(),
            'end_date': long_end.isoformat()
        }

        response = self.client.post(self.url, long_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
