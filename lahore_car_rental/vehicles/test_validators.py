from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from .models import Vehicle
from django.utils import timezone
from .validators import (
    validate_license_plate,
    validate_vehicle_year,
    validate_vehicle_make,
    validate_vehicle_model,
    validate_make_model_combination
)

User = get_user_model()


class VehicleValidatorTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_validate_license_plate_valid_formats(self):
        """Test valid license plate formats"""
        valid_plates = [
            'ABC-1234',
            'AB-123',
            'ABC1234',
            'LH12AB1234',
            'XYZ-12-3456',
        ]

        for plate in valid_plates:
            try:
                validate_license_plate(plate)
            except ValidationError:
                self.fail(
                    f"validate_license_plate raised ValidationError for valid plate: {plate}")

    def test_validate_license_plate_invalid_formats(self):
        """Test invalid license plate formats"""
        invalid_plates = [
            '',  # Empty
            '   ',  # Whitespace only
            'A',  # Too short
            'ABCDEFGHIJKLMNOP',  # Too long
            'ADMIN123',  # Reserved word
            '!!!@@@',  # Invalid characters
        ]

        for plate in invalid_plates:
            with self.assertRaises(ValidationError):
                validate_license_plate(plate)

    def test_validate_vehicle_year_valid(self):
        """Test valid vehicle years"""
        valid_years = [1950, 1980, 2000, 2024,
                       timezone.now().year, timezone.now().year + 1]

        for year in valid_years:
            try:
                validate_vehicle_year(year)
            except ValidationError:
                self.fail(
                    f"validate_vehicle_year raised ValidationError for valid year: {year}")

    def test_validate_vehicle_year_invalid(self):
        """Test invalid vehicle years"""
        invalid_years = [1949, 1800, timezone.now().year + 3]

        for year in invalid_years:
            with self.assertRaises(ValidationError):
                validate_vehicle_year(year)

    def test_validate_vehicle_make_valid(self):
        """Test valid vehicle makes"""
        valid_makes = ['Toyota', 'Honda', 'Ford',
                       'BMW', 'Mercedes-Benz', 'Hyundai & Co']

        for make in valid_makes:
            try:
                validate_vehicle_make(make)
            except ValidationError:
                self.fail(
                    f"validate_vehicle_make raised ValidationError for valid make: {make}")

    def test_validate_vehicle_make_invalid(self):
        """Test invalid vehicle makes"""
        invalid_makes = ['', '   ', 'A', 'UNKNOWN', 'N/A', 'T@y@ta!']

        for make in invalid_makes:
            with self.assertRaises(ValidationError):
                validate_vehicle_make(make)

    def test_validate_vehicle_model_valid(self):
        """Test valid vehicle models"""
        valid_models = ['Corolla', 'Civic',
                        'F-150', 'X5', 'E-Class', 'Model S']

        for model in valid_models:
            try:
                validate_vehicle_model(model)
            except ValidationError:
                self.fail(
                    f"validate_vehicle_model raised ValidationError for valid model: {model}")

    def test_validate_vehicle_model_invalid(self):
        """Test invalid vehicle models"""
        invalid_models = ['', '   ', 'UNKNOWN', 'N/A', 'M@del!']

        for model in invalid_models:
            with self.assertRaises(ValidationError):
                validate_vehicle_model(model)

    def test_validate_make_model_combination_valid(self):
        """Test valid make-model combinations"""
        valid_combinations = [
            ('Toyota', 'Corolla'),
            ('Honda', 'Civic'),
            ('Ford', 'Mustang'),
            ('BMW', 'X5')
        ]

        for make, model in valid_combinations:
            try:
                validate_make_model_combination(make, model)
            except ValidationError:
                self.fail(
                    f"validate_make_model_combination raised ValidationError for valid combination: {make} {model}")

    def test_validate_make_model_combination_invalid(self):
        """Test invalid make-model combinations"""
        invalid_combinations = [
            ('Toyota', 'Toyota'),  # Same make and model
            ('Toyota', 'Civic'),   # Honda model with Toyota make
            ('Honda', 'Corolla'),  # Toyota model with Honda make
        ]

        for make, model in invalid_combinations:
            with self.assertRaises(ValidationError):
                validate_make_model_combination(make, model)


class VehicleModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_create_valid_vehicle(self):
        """Test creating a valid vehicle"""
        vehicle = Vehicle.objects.create(
            user=self.user,
            make='Toyota',
            model='Corolla',
            year=2020,
            plate='ABC-1234'
        )

        self.assertEqual(vehicle.make, 'Toyota')
        self.assertEqual(vehicle.model, 'Corolla')
        self.assertEqual(vehicle.year, 2020)
        self.assertEqual(vehicle.plate, 'ABC-1234')

    def test_create_vehicle_with_invalid_plate(self):
        """Test creating vehicle with invalid license plate"""
        with self.assertRaises(ValidationError):
            vehicle = Vehicle(
                user=self.user,
                make='Toyota',
                model='Corolla',
                year=2020,
                plate='INVALID_PLATE_FORMAT!!!'
            )
            vehicle.full_clean()

    def test_create_vehicle_with_invalid_year(self):
        """Test creating vehicle with invalid year"""
        with self.assertRaises(ValidationError):
            vehicle = Vehicle(
                user=self.user,
                make='Toyota',
                model='Corolla',
                year=1800,  # Too old
                plate='ABC-1234'
            )
            vehicle.full_clean()

    def test_create_vehicle_with_same_make_model(self):
        """Test creating vehicle with same make and model"""
        with self.assertRaises(ValidationError):
            vehicle = Vehicle(
                user=self.user,
                make='Toyota',
                model='Toyota',  # Same as make
                year=2020,
                plate='ABC-1234'
            )
            vehicle.full_clean()

    def test_vehicle_data_normalization(self):
        """Test that vehicle data is normalized on save"""
        vehicle = Vehicle.objects.create(
            user=self.user,
            make='  toyota  ',  # Will be normalized to 'Toyota'
            model='  corolla  ',  # Will be normalized to 'Corolla'
            year=2020,
            plate='  abc 1234  '  # Will be normalized to 'ABC 1234'
        )

        self.assertEqual(vehicle.make, 'Toyota')
        self.assertEqual(vehicle.model, 'Corolla')
        self.assertEqual(vehicle.plate, 'ABC 1234')
