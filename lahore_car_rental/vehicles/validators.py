import re
from datetime import datetime
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


def validate_license_plate(value):
    """
    Validates license plate format and standardizes it.
    Supports multiple formats common in Pakistan and international standards.
    """
    if not value or not value.strip():
        raise ValidationError(_('License plate cannot be empty.'))

    # Remove spaces and convert to uppercase for validation
    cleaned_plate = re.sub(r'\s+', '', value.upper().strip())

    # Common Pakistan license plate patterns
    pakistan_patterns = [
        r'^[A-Z]{2,3}-\d{2,4}$',  # e.g., ABC-1234, AB-123
        r'^[A-Z]{2,3}\d{2,4}$',   # e.g., ABC1234, AB123
        r'^[A-Z]{3}-\d{2}-\d{2,4}$',  # e.g., ABC-12-3456
        r'^[A-Z]{2}\d{2}[A-Z]{2}\d{4}$',  # e.g., LH12AB1234 (Lahore format)
    ]

    # International patterns
    international_patterns = [
        r'^[A-Z0-9]{3,8}$',  # Generic alphanumeric
        r'^[A-Z]{1,3}\d{1,4}[A-Z]{0,3}$',  # Mixed format
        r'^[A-Z]{1,2}\d{1,4}[A-Z]{1,3}$',  # Another mixed format
    ]

    all_patterns = pakistan_patterns + international_patterns

    # Check if plate matches any valid pattern
    is_valid = any(re.match(pattern, cleaned_plate)
                   for pattern in all_patterns)

    if not is_valid:
        raise ValidationError(
            _('Invalid license plate format. Please use formats like ABC-1234, ABC1234, LH12AB1234, or AB-123.')
        )

    # Check for offensive or reserved patterns
    reserved_patterns = ['ADMIN', 'GOVT', 'POLICE', 'TEST']
    if any(pattern in cleaned_plate for pattern in reserved_patterns):
        raise ValidationError(
            _('This license plate contains reserved words and cannot be used.'))


def validate_vehicle_year(value):
    """
    Validates vehicle year with business rules.
    """
    current_year = timezone.now().year

    # Allow next year for new models
    max_year = current_year + 1

    # Minimum year for practical vehicles
    min_year = 1950

    if value > max_year:
        raise ValidationError(
            _('Vehicle year cannot be in the future. Year cannot be more than %(max_year)s.') % {
                'max_year': max_year}
        )

    if value < min_year:
        raise ValidationError(
            _('Vehicle year must be %(min_year)s or later.') % {
                'min_year': min_year}
        )


def validate_vehicle_make(value):
    """
    Validates vehicle make/manufacturer.
    """
    if not value or not value.strip():
        raise ValidationError(_('Vehicle make cannot be empty.'))

    cleaned_make = value.strip()
    
    # Check for valid characters (letters, numbers, spaces, hyphens)
    if not re.match(r'^[a-zA-Z0-9\s\-&\.]+$', cleaned_make):
        raise ValidationError(
            _('Vehicle make contains invalid characters. Only letters, numbers, spaces, hyphens, ampersands, and periods are allowed.')
        )

    # Check for known invalid patterns
    invalid_patterns = ['UNKNOWN', 'N/A', 'NULL', 'NONE', 'TEST']
    if cleaned_make.upper() in invalid_patterns:
        raise ValidationError(_('Please provide a valid vehicle make.'))


def validate_vehicle_model(value):
    """
    Validates vehicle model.
    """
    if not value or not value.strip():
        raise ValidationError(_('Vehicle model cannot be empty.'))

    cleaned_model = value.strip()

    # Check for valid characters (letters, numbers, spaces, hyphens, periods)
    if not re.match(r'^[a-zA-Z0-9\s\-&\./]+$', cleaned_model):
        raise ValidationError(
            _('Vehicle model contains invalid characters. Only letters, numbers, spaces, hyphens, ampersands, periods, and forward slashes are allowed.')
        )

    # Check for known invalid patterns
    invalid_patterns = ['UNKNOWN', 'N/A', 'NULL', 'NONE', 'TEST']
    if cleaned_model.upper() in invalid_patterns:
        raise ValidationError(_('Please provide a valid vehicle model.'))


def validate_make_model_combination(make, model):
    """
    Cross-field validation for make and model combination.
    This can be used in clean() method for additional business logic.
    """
    if not make or not model:
        return  # Individual field validation will handle empty values

    make_clean = make.strip().upper()
    model_clean = model.strip().upper()

    # Check if make and model are the same (usually invalid)
    if make_clean == model_clean:
        raise ValidationError({
            'model': _('Vehicle make and model cannot be identical.')
        })

    # You can add specific make-model validations here
    # For example, checking if a model actually exists for a specific make
    # This would require a database of valid make-model combinations

    # Example: Basic validation for some common inconsistencies
    common_inconsistencies = {
        'TOYOTA': ['CIVIC', 'ACCORD', 'F150'],  # Honda and Ford models
        'HONDA': ['COROLLA', 'CAMRY', 'MUSTANG'],  # Toyota and Ford models
        'FORD': ['CIVIC', 'COROLLA', 'ALTIMA'],  # Honda, Toyota, Nissan models
    }

    if make_clean in common_inconsistencies:
        invalid_models = common_inconsistencies[make_clean]
        if model_clean in invalid_models:
            raise ValidationError({
                'model': _('%(model)s is not a valid model for %(make)s.') % {
                    'model': model, 'make': make
                }
            })
