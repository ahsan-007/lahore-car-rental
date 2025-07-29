from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch
from django.utils import timezone
from .models import Vehicle
from .serializers import VehicleSerializer
from .views import VehicleListCreateView, VehicleDetailView


class VehicleSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass')
        self.valid_data = {
            'make': 'Toyota',
            'model': 'Corolla',
            'year': 2020,
            'plate': 'ABC-123',
            'user': self.user.id
        }

    def test_valid_serialization(self):
        serializer = VehicleSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())

    def test_year_validation_future_year(self):
        future_year = timezone.now().year + 2
        data = self.valid_data.copy()
        data['year'] = future_year
        serializer = VehicleSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('year', serializer.errors)
        self.assertEqual(
            serializer.errors['year'][0], "Year cannot be in the future.")

    def test_year_validation_next_year_allowed(self):
        next_year = timezone.now().year + 1
        data = self.valid_data.copy()
        data['year'] = next_year
        serializer = VehicleSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_serializer_fields(self):
        serializer = VehicleSerializer()
        expected_fields = ['id', 'make', 'model', 'year', 'plate']
        self.assertEqual(serializer.Meta.fields, expected_fields)


class VehicleListCreateViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            username='user1', password='pass1')
        self.user2 = User.objects.create_user(
            username='user2', password='pass2')
        self.vehicle1 = Vehicle.objects.create(
            make='Toyota', model='Corolla', year=2020, plate='ABC-123', user=self.user1
        )
        self.vehicle2 = Vehicle.objects.create(
            make='Honda', model='Civic', year=2019, plate='XYZ-789', user=self.user2
        )
        self.url = reverse('vehicle-list-create')

    def test_list_vehicles_authenticated(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.vehicle1.id)

    def test_list_vehicles_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_vehicles_user_isolation(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.vehicle2.id)

    def test_create_vehicle_authenticated(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            'make': 'BMW',
            'model': 'X5',
            'year': 2021,
            'plate': 'BMW-001'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Vehicle.objects.count(), 3)
        created_vehicle = Vehicle.objects.get(plate='BMW-001')
        self.assertEqual(created_vehicle.user, self.user1)

    def test_create_vehicle_unauthenticated(self):
        data = {
            'make': 'BMW',
            'model': 'X5',
            'year': 2021,
            'plate': 'BMW-001'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_vehicle_invalid_year(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            'make': 'BMW',
            'model': 'X5',
            'year': timezone.now().year + 2,
            'plate': 'BMW-001'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('year', response.data)

    def test_create_vehicle_duplicate_plate(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            'make': 'Toyota',
            'model': 'Camry',
            'year': 2021,
            'plate': self.vehicle1.plate  # Duplicate plate
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('plate', response.data)

    def test_swagger_fake_view_returns_empty_queryset(self):
        view = VehicleListCreateView()
        view.swagger_fake_view = True
        queryset = view.get_queryset()
        self.assertEqual(queryset.count(), 0)

    def test_perform_create_assigns_user(self):
        view = VehicleListCreateView()
        view.request = type('MockRequest', (), {'user': self.user1})()
        serializer = VehicleSerializer(data={
            'make': 'Test',
            'model': 'Car',
            'year': 2020,
            'plate': 'TEST-123'
        })
        self.assertTrue(serializer.is_valid())
        view.perform_create(serializer)
        vehicle = Vehicle.objects.get(plate='TEST-123')
        self.assertEqual(vehicle.user, self.user1)


class VehicleDetailViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            username='user1', password='pass1')
        self.user2 = User.objects.create_user(
            username='user2', password='pass2')
        self.vehicle1 = Vehicle.objects.create(
            make='Toyota', model='Corolla', year=2020, plate='ABC-123', user=self.user1
        )
        self.vehicle2 = Vehicle.objects.create(
            make='Honda', model='Civic', year=2019, plate='XYZ-789', user=self.user2
        )
        self.url1 = reverse('vehicle-detail', kwargs={'pk': self.vehicle1.pk})
        self.url2 = reverse('vehicle-detail', kwargs={'pk': self.vehicle2.pk})

    def test_retrieve_vehicle_owner(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.url1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.vehicle1.id)

    def test_retrieve_vehicle_unauthenticated(self):
        response = self.client.get(self.url1)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_vehicle_not_owner(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.url2)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_vehicle_owner(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            'make': 'Toyota',
            'model': 'Camry',
            'year': 2021,
            'plate': 'ABC-123'
        }
        response = self.client.put(self.url1, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.vehicle1.refresh_from_db()
        self.assertEqual(self.vehicle1.model, 'Camry')

    def test_update_vehicle_unauthenticated(self):
        data = {
            'make': 'Toyota',
            'model': 'Camry',
            'year': 2021,
            'plate': 'ABC-123'
        }
        response = self.client.put(self.url1, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_vehicle_not_owner(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            'make': 'Honda',
            'model': 'Accord',
            'year': 2021,
            'plate': 'XYZ-789'
        }
        response = self.client.put(self.url2, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_vehicle_duplicate_plate(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            'make': 'Toyota',
            'model': 'Camry',
            'year': 2021,
            'plate': self.vehicle2.plate  # Duplicate plate
        }
        response = self.client.put(self.url1, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('plate', response.data)

    def test_delete_vehicle_owner(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(self.url1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'],
                         "Vehicle deleted successfully.")
        self.assertFalse(Vehicle.objects.filter(pk=self.vehicle1.pk).exists())

    def test_delete_vehicle_not_owner(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(self.url2)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_vehicle_unauthenticated(self):
        response = self.client.delete(self.url1)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_swagger_fake_view_returns_empty_queryset(self):
        view = VehicleDetailView()
        view.swagger_fake_view = True
        queryset = view.get_queryset()
        self.assertEqual(queryset.count(), 0)

    def test_http_method_names_restriction(self):
        view = VehicleDetailView()
        allowed_methods = ['get', 'put', 'delete']
        self.assertEqual(view.http_method_names, allowed_methods)

    def test_patch_method_not_allowed(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.patch(self.url1, {'model': 'Prius'})
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_post_method_not_allowed(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.url1, {})
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_nonexistent_vehicle_404(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('vehicle-detail', kwargs={'pk': 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class VehiclePermissionTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', password='testpass')
        self.vehicle = Vehicle.objects.create(
            make='Toyota', model='Corolla', year=2020, plate='ABC-123', user=self.user
        )

    def test_list_view_requires_authentication(self):
        view = VehicleListCreateView()
        self.assertIn('IsAuthenticated',
                      [perm.__name__ for perm in view.permission_classes])

    def test_detail_view_requires_authentication(self):
        view = VehicleDetailView()
        self.assertIn('IsAuthenticated',
                      [perm.__name__ for perm in view.permission_classes])

    def test_user_can_only_see_own_vehicles(self):
        # Create another user and vehicle
        other_user = User.objects.create_user(
            username='other', password='pass')
        other_vehicle = Vehicle.objects.create(
            make='Honda', model='Civic', year=2019, plate='XYZ-789', user=other_user
        )

        self.client.force_authenticate(user=self.user)

        # User should see only their own vehicle in list
        list_url = reverse('vehicle-list-create')
        response = self.client.get(list_url)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.vehicle.id)

        # User should not be able to access other user's vehicle
        other_detail_url = reverse(
            'vehicle-detail', kwargs={'pk': other_vehicle.pk})
        response = self.client.get(other_detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
