from rest_framework import serializers
from .models import Booking
from vehicles.models import Vehicle
from django.contrib.auth.models import User
from .validators import (
    validate_booking_duration,
    validate_date_order
)


class BookingSerializer(serializers.ModelSerializer):
    vehicle = serializers.PrimaryKeyRelatedField(
        queryset=Vehicle.objects.all(),
        error_messages={
            'does_not_exist': 'Vehicle with this id does not exist.',
            'incorrect_type': 'Vehicle id must be an integer.'
        }
    )
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Booking
        fields = ['vehicle', 'user', 'start_date', 'end_date']

    def validate(self, data):
        """
        Custom validation using our validators
        """
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        # Validate date order
        validate_date_order(start_date, end_date)

        # Validate booking duration
        validate_booking_duration(start_date, end_date)

        return data
