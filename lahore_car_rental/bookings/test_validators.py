from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import timedelta
from vehicles.models import Vehicle
from .validators import (
    validate_future_datetime,
    validate_start_date,
    validate_booking_duration,
    validate_date_order,
    validate_booking_overlap
)


class ValidatorTestCase(TestCase):

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
            year=2022,
            plate='ABC-1234'
        )

        self.now = timezone.now()
        self.future_start = self.now + timedelta(hours=2)
        self.future_end = self.future_start + timedelta(hours=3)

    def test_validate_future_datetime_valid(self):
        """Test that future datetime validation passes for valid dates"""
        future_time = self.now + timedelta(hours=2)
        # Should not raise exception
        result = validate_future_datetime(future_time)
        self.assertEqual(result, future_time)

    def test_validate_future_datetime_invalid(self):
        """Test that future datetime validation fails for past dates"""
        past_time = self.now - timedelta(hours=1)
        with self.assertRaises(ValidationError):
            validate_future_datetime(past_time)

    def test_validate_start_date_valid(self):
        """Test that start date validation passes for valid dates"""
        future_time = self.now + timedelta(hours=2)
        # Should not raise exception
        result = validate_start_date(future_time)
        self.assertEqual(result, future_time)

    def test_validate_start_date_invalid(self):
        """Test that start date validation fails for dates too close to now"""
        near_time = self.now + timedelta(minutes=30)  # Less than 1 hour
        with self.assertRaises(ValidationError):
            validate_start_date(near_time)

    def test_validate_booking_duration_valid(self):
        """Test that booking duration validation passes for valid durations"""
        start = self.future_start
        end = start + timedelta(hours=2)  # 2 hours duration
        # Should not raise exception
        validate_booking_duration(start, end)

    def test_validate_booking_duration_too_short(self):
        """Test that booking duration validation fails for too short durations"""
        start = self.future_start
        end = start + timedelta(minutes=30)  # 30 minutes - too short
        with self.assertRaises(ValidationError):
            validate_booking_duration(start, end)

    def test_validate_booking_duration_too_long(self):
        """Test that booking duration validation fails for too long durations"""
        start = self.future_start
        end = start + timedelta(days=35)  # 35 days - too long
        with self.assertRaises(ValidationError):
            validate_booking_duration(start, end)

    def test_validate_date_order_valid(self):
        """Test that date order validation passes when end > start"""
        start = self.future_start
        end = start + timedelta(hours=2)
        # Should not raise exception
        validate_date_order(start, end)

    def test_validate_date_order_invalid(self):
        """Test that date order validation fails when end <= start"""
        start = self.future_start
        end = start - timedelta(hours=1)  # End before start
        with self.assertRaises(ValidationError):
            validate_date_order(start, end)

    def test_validate_booking_overlap_no_conflict(self):
        """Test that overlap validation passes when no conflicts exist"""
        # Should not raise exception
        validate_booking_overlap(
            self.vehicle, self.future_start, self.future_end)
