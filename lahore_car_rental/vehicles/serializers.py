from rest_framework import serializers
from .models import Vehicle


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['id', 'make', 'model', 'year', 'plate']

    def validate(self, data):
        """
        Cross-field validation using the model's clean method.
        """
        # Create a temporary instance for validation
        instance = Vehicle(**data)

        # If this is an update, copy the existing user
        if self.instance:
            instance.user = self.instance.user
            instance.pk = self.instance.pk

        # Run model-level validation
        try:
            instance.clean()
        except Exception as e:
            if hasattr(e, 'message_dict'):
                raise serializers.ValidationError(e.message_dict)
            else:
                raise serializers.ValidationError(
                    {'non_field_errors': [str(e)]})

        return data
