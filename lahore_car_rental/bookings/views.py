from rest_framework import generics, permissions
from .models import Booking
from .serializers import BookingSerializer
from vehicles.models import Vehicle
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.dateparse import parse_date
from django.utils import timezone
from datetime import datetime, time
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .validators import validate_booking_overlap


class BookingListCreateView(generics.ListCreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'from',
                openapi.IN_QUERY,
                description="Filter bookings starting from this date (YYYY-MM-DD format)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                required=False
            ),
            openapi.Parameter(
                'to',
                openapi.IN_QUERY,
                description="Filter bookings ending before this date (YYYY-MM-DD format)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                required=False
            ),
        ],
        operation_description="List bookings for the authenticated user with optional date filtering"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        # Only return bookings for the authenticated user
        queryset = Booking.objects.filter(user=self.request.user)

        # Filter by date range using query parameters
        from_date = self.request.query_params.get('from', None)
        to_date = self.request.query_params.get('to', None)

        if from_date:
            try:
                parsed_from_date = parse_date(from_date)
                if parsed_from_date:
                    # Convert date to timezone-aware datetime (start of day)
                    from_datetime = timezone.make_aware(
                        datetime.combine(parsed_from_date, time.min))
                    queryset = queryset.filter(start_date__gte=from_datetime)
                else:
                    raise DRFValidationError(
                        {'from': 'Invalid date format for from_date. Use YYYY-MM-DD.'})
            except ValueError as ve:
                raise DRFValidationError(
                    {'from': 'Invalid date format for from_date. ' + str(ve)})

        if to_date:
            try:
                parsed_to_date = parse_date(to_date)
                if parsed_to_date:
                    # Convert date to timezone-aware datetime (end of day)
                    to_datetime = timezone.make_aware(
                        datetime.combine(parsed_to_date, time.max))
                    queryset = queryset.filter(end_date__lte=to_datetime)
                else:
                    raise DRFValidationError(
                        {'to': 'Invalid date format for to_date. Use YYYY-MM-DD.'})
            except ValueError as ve:
                raise DRFValidationError(
                    {'to': 'Invalid date format for to_date. ' + str(ve)})

        return queryset

    def perform_create(self, serializer):
        vehicle = serializer.validated_data['vehicle']
        start_date = serializer.validated_data['start_date']
        end_date = serializer.validated_data['end_date']

        # Use custom validator for overlap checking
        try:
            validate_booking_overlap(vehicle, start_date, end_date)
        except DjangoValidationError as e:
            # Convert Django ValidationError to DRF ValidationError
            if hasattr(e, 'message_dict'):
                raise DRFValidationError(e.message_dict)
            else:
                raise DRFValidationError({'detail': str(e)})

        # Save the booking with the current user
        serializer.save(user=self.request.user)
