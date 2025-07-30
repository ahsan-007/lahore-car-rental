from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from .validators import (
    validate_license_plate,
    validate_vehicle_year,
    validate_vehicle_make,
    validate_vehicle_model,
    validate_make_model_combination
)

User = get_user_model()


class Vehicle(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='vehicles')
    make = models.CharField(
        max_length=100,
        validators=[MinLengthValidator(2), validate_vehicle_make],
        help_text="Vehicle manufacturer (e.g., Toyota, Honda, Ford)"
    )
    model = models.CharField(
        max_length=100,
        validators=[MinLengthValidator(2), validate_vehicle_model],
        help_text="Vehicle model (e.g., Corolla, Civic, Mustang)"
    )
    year = models.PositiveIntegerField(
        validators=[validate_vehicle_year],
        help_text="Vehicle manufacturing year"
    )
    plate = models.CharField(
        max_length=20,
        unique=True,
        validators=[MinLengthValidator(3),validate_license_plate],
        help_text="Vehicle license plate number"
    )

    class Meta:
        ordering = ['-year', 'make', 'model']
        indexes = [
            models.Index(fields=['user', 'make']),
            models.Index(fields=['year']),
            models.Index(fields=['plate']),
        ]

    def clean(self):
        """
        Model-level validation for cross-field validation.
        """
        super().clean()

        # Validate make and model combination
        if self.make and self.model:
            validate_make_model_combination(self.make, self.model)

    def save(self, *args, **kwargs):
        """
        Override save to ensure validation is run and normalize data.
        """
        # Normalize data before saving
        if self.make:
            self.make = self.make.strip().title()
        if self.model:
            self.model = self.model.strip().title()
        if self.plate:
            # Normalize plate to uppercase and remove extra spaces
            self.plate = ' '.join(self.plate.strip().upper().split())

        # Run full validation
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.make} {self.model} ({self.plate})"
