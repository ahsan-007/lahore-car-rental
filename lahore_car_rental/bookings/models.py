from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from vehicles.models import Vehicle


class Booking(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['vehicle', 'start_date', 'end_date']),
            models.Index(fields=['user', 'start_date']),
        ]

    def clean(self):
        """
        Model-level validation for date logic
        """
        errors = {}

        if self.start_date and self.end_date:
            # Validate that end_date is after start_date
            if self.end_date <= self.start_date:
                errors['end_date'] = 'End date must be after start date.'

            # Validate that start_date is not in the past (with 1 hour buffer for current bookings)
            current_time = timezone.now()
            min_booking_time = current_time + timedelta(hours=1)

            if self.start_date < min_booking_time:
                errors['start_date'] = 'Booking start date must be at least 1 hour in the future.'

            # Validate booking duration (minimum 1 hour, maximum 30 days)
            if self.start_date and self.end_date:
                duration = self.end_date - self.start_date
                min_duration = timedelta(hours=1)
                max_duration = timedelta(days=30)

                if duration < min_duration and errors.get('end_date') is None:
                    errors['end_date'] = 'Booking duration must be for at least 1 hour.'

                if duration > max_duration and errors.get('end_date') is None:
                    errors['end_date'] = 'Booking duration cannot exceed 30 days.'

        # Validate that the booking doesn't overlap with existing bookings for the same vehicle
        if self.vehicle and self.start_date and self.end_date:
            overlapping_bookings = Booking.objects.filter(
                vehicle=self.vehicle,
                end_date__gt=self.start_date,
                start_date__lt=self.end_date
            )

            if overlapping_bookings.exists():
                errors['vehicle'] = 'This vehicle is already booked for the selected time period.'

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """
        Override save to ensure validation is run
        """
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def is_past(self):
        """
        Check if the booking is in the past
        """
        return self.end_date < timezone.now() if self.end_date else False

    @property
    def is_current(self):
        """
        Check if the booking is currently active
        """
        now = timezone.now()
        return self.start_date <= now <= self.end_date if self.start_date and self.end_date else False

    @property
    def is_future(self):
        """
        Check if the booking is in the future
        """
        return self.start_date > timezone.now() if self.start_date else False

    def __str__(self):
        return f"{self.user.username} - {self.vehicle.make} {self.vehicle.model} from {self.start_date} to {self.end_date}"
