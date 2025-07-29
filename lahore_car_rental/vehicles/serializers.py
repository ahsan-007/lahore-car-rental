from rest_framework import serializers
from .models import Vehicle
from django.utils import timezone


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['id', 'make', 'model', 'year', 'plate']

    def validate_year(self, value):
        current_year = timezone.now().year
        if value > current_year + 1:  # Allow next year for new models
            raise serializers.ValidationError("Year cannot be in the future.")

        if value < 1950:  # Add minimum year validation
            raise serializers.ValidationError("Year must be 1950 or later.")

        return value

    def validate_plate(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("License plate cannot be empty.")
        return value.strip().upper()  # Normalize plate format

    def validate_make(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Make cannot be empty.")
        return value.strip()

    def validate_model(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Model cannot be empty.")
        return value.strip()
