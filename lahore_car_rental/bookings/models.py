from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from vehicles.models import Vehicle
from .validators import (
    validate_start_date,
    validate_booking_duration,
    validate_date_order,
    validate_booking_overlap
)


class Booking(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateTimeField(validators=[validate_start_date])
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
        Model-level validation using custom validators
        """
        errors = {}

        # Use custom validators for comprehensive validation
        try:
            # Validate date order
            validate_date_order(self.start_date, self.end_date)
        except ValidationError as e:
            errors.update(e.message_dict if hasattr(
                e, 'message_dict') else {'__all__': e.messages})

        try:
            # Validate booking duration
            validate_booking_duration(self.start_date, self.end_date)
        except ValidationError as e:
            # Only add duration errors if we don't already have date order errors
            if not any(field in errors for field in ['start_date', 'end_date']):
                errors.update(e.message_dict if hasattr(
                    e, 'message_dict') else {'__all__': e.messages})

        try:
            # Validate booking overlap
            validate_booking_overlap(
                self.vehicle, self.start_date, self.end_date, exclude_booking=self)
        except ValidationError as e:
            errors.update(e.message_dict if hasattr(
                e, 'message_dict') else {'__all__': e.messages})

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
