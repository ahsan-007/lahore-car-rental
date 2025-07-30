from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from datetime import timedelta


def validate_future_datetime(value, hours_ahead=1):
    """
    Validates that a datetime is at least a specified number of hours in the future.
    Default is 1 hour to allow for booking processing time.
    """
    if not value:
        return value

    current_time = timezone.now()
    min_booking_time = current_time + timedelta(hours=hours_ahead)

    if value < min_booking_time:
        raise ValidationError(
            _(f'Booking date must be at least {hours_ahead} hour(s) in the future.')
        )

    return value


def validate_start_date(value):
    """
    Validates that the booking start date is at least 1 hour in the future.
    """
    return validate_future_datetime(value, hours_ahead=1)


def validate_booking_duration(start_date, end_date):
    """
    Validates that booking duration is within acceptable limits.
    Minimum: 1 hour, Maximum: 30 days
    """
    if not start_date or not end_date:
        return

    if end_date <= start_date:
        raise ValidationError({
            'end_date': _('End date must be after start date.')
        })

    duration = end_date - start_date
    min_duration = timedelta(hours=1)
    max_duration = timedelta(days=30)

    if duration < min_duration:
        raise ValidationError({
            'end_date': _('Booking duration must be at least 1 hour.')
        })

    if duration > max_duration:
        raise ValidationError({
            'end_date': _('Booking duration cannot exceed 30 days.')
        })


def validate_date_order(start_date, end_date):
    """
    Validates that end_date is after start_date.
    """
    if start_date and end_date and end_date <= start_date:
        raise ValidationError({
            'end_date': _('End date must be after start date.')
        })


def validate_booking_overlap(vehicle, start_date, end_date, exclude_booking=None):
    """
    Validates that the booking doesn't overlap with existing bookings for the same vehicle.

    Args:
        vehicle: The vehicle being booked
        start_date: Booking start date
        end_date: Booking end date
        exclude_booking: Booking instance to exclude from overlap check (for updates)
    """
    if not vehicle or not start_date or not end_date:
        return

    # Import here to avoid circular import
    from .models import Booking

    overlapping_bookings = Booking.objects.filter(
        vehicle=vehicle,
        end_date__gt=start_date,
        start_date__lt=end_date
    )

    if exclude_booking and exclude_booking.pk:
        overlapping_bookings = overlapping_bookings.exclude(
            pk=exclude_booking.pk)

    if overlapping_bookings.exists():
        raise ValidationError({
            'vehicle': _('This vehicle is already booked for the selected time period.')
        })


def validate_user_concurrent_bookings(user, start_date, end_date, exclude_booking=None, max_concurrent=3):
    """
    Validates that a user doesn't exceed the maximum number of concurrent bookings.

    Args:
        user: The user making the booking
        start_date: Booking start date
        end_date: Booking end date
        exclude_booking: Booking instance to exclude from count (for updates)
        max_concurrent: Maximum number of concurrent bookings allowed
    """
    if not user or not start_date or not end_date:
        return

    # Import here to avoid circular import
    from .models import Booking

    # Find overlapping bookings for this user
    overlapping_bookings = Booking.objects.filter(
        user=user,
        end_date__gt=start_date,
        start_date__lt=end_date
    )

    # Exclude the current booking if we're updating
    if exclude_booking and exclude_booking.pk:
        overlapping_bookings = overlapping_bookings.exclude(
            pk=exclude_booking.pk)

    if overlapping_bookings.count() >= max_concurrent:
        raise ValidationError({
            'user': _(f'You cannot have more than {max_concurrent} concurrent bookings.')
        })
