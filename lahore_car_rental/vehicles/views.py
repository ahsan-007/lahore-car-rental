from rest_framework import generics
from rest_framework.exceptions import ValidationError
from .models import Vehicle
from .serializers import VehicleSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import IntegrityError


class VehicleListCreateView(generics.ListCreateAPIView):
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'user_id',
                openapi.IN_QUERY,
                description="User ID to filter vehicles (required)",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
            openapi.Parameter(
                'year',
                openapi.IN_QUERY,
                description="Filter vehicles by year (e.g., 2019)",
                type=openapi.TYPE_INTEGER,
                required=False
            ),
            openapi.Parameter(
                'make',
                openapi.IN_QUERY,
                description="Filter vehicles by make (case-insensitive, e.g., Honda)",
                type=openapi.TYPE_STRING,
                required=False
            ),
        ],
        operation_description="Get list of vehicles for a user with optional filtering by year and make. 'user' query parameter is required.",
        security=[{'Bearer': []}]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Vehicle.objects.none()

        user_id = self.request.query_params.get('user_id')
        if not user_id:
            raise ValidationError(
                {"user": "This query parameter is required."})

        queryset = Vehicle.objects.filter(user_id=user_id)

        # Filter by year if provided
        year = self.request.query_params.get('year')
        if year:
            queryset = queryset.filter(year=year)

        # Filter by make if provided
        make = self.request.query_params.get('make')
        if make:
            queryset = queryset.filter(make__icontains=make)

        return queryset

    def perform_create(self, serializer):
        try:
            serializer.save(user=self.request.user)
        except IntegrityError:
            raise ValidationError(
                {"plate": "A vehicle with this license plate already exists."})


class VehicleDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'put', 'delete']

    @swagger_auto_schema(security=[{'Bearer': []}])
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Vehicle.objects.none()
        # Allow any user to retrieve any vehicle
        return Vehicle.objects.all()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response({"detail": "You do not have permission to update this vehicle."}, status=403)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response({"detail": "You do not have permission to delete this vehicle."}, status=403)
        self.perform_destroy(instance)
        return Response({"detail": "Vehicle deleted successfully."}, status=200)

    def perform_update(self, serializer):
        try:
            serializer.save()
        except IntegrityError:
            raise ValidationError(
                {"plate": "A vehicle with this license plate already exists."})
