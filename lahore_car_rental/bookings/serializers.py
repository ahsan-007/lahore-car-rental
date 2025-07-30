from rest_framework import serializers
from .models import Booking
from vehicles.models import Vehicle
from django.contrib.auth.models import User


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
