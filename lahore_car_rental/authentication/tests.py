from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status


class AuthenticationTestCase(APITestCase):
    def setUp(self):
        """Set up test data"""
        self.register_url = reverse('register')
        self.login_url = reverse('login')

        # Valid test data
        self.valid_user_data = {
            'username': 'testuser123',
            'email': 'testuser@example.com',
            'password': 'SecurePass123!',
            'password2': 'SecurePass123!'
        }

        # Create an existing user for login tests
        self.existing_user = User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='ExistingPass123!'
        )

    def test_user_registration_success(self):
        """Test successful user registration with valid data"""
        response = self.client.post(
            self.register_url, self.valid_user_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

        # Verify user was created in database
        self.assertTrue(User.objects.filter(username='testuser123').exists())
        user = User.objects.get(username='testuser123')
        self.assertEqual(user.email, 'testuser@example.com')

    def test_user_registration_duplicate_username(self):
        """Test registration fails with duplicate username"""
        duplicate_data = self.valid_user_data.copy()
        duplicate_data['username'] = self.existing_user.username  # Already exists
        duplicate_data['email'] = 'newemail@example.com'

        response = self.client.post(
            self.register_url, duplicate_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)
        self.assertIn('already exists', str(response.data['username']))

    def test_user_registration_duplicate_email(self):
        """Test registration fails with duplicate email"""
        duplicate_data = self.valid_user_data.copy()
        duplicate_data['username'] = 'newuser123'
        duplicate_data['email'] = self.existing_user.email  # Already exists

        response = self.client.post(
            self.register_url, duplicate_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        self.assertIn('already exists', str(response.data['email']))

    def test_user_registration_password_mismatch(self):
        """Test registration fails when passwords don't match"""
        invalid_data = self.valid_user_data.copy()
        invalid_data['password2'] = 'DifferentPassword123!'

        response = self.client.post(
            self.register_url, invalid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)
        self.assertIn("didn't match", str(response.data['password']))

    def test_user_registration_weak_password(self):
        """Test registration fails with weak password"""
        weak_password_data = self.valid_user_data.copy()
        weak_password_data['password'] = '123'  # Too weak
        weak_password_data['password2'] = '123'

        response = self.client.post(
            self.register_url, weak_password_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_user_registration_invalid_email(self):
        """Test registration fails with invalid email format"""
        invalid_email_data = self.valid_user_data.copy()
        invalid_email_data['email'] = 'invalid-email-format'

        response = self.client.post(
            self.register_url, invalid_email_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_user_registration_missing_fields(self):
        """Test registration fails with missing required fields"""
        incomplete_data = {
            'username': 'testuser',
            # Missing email, password, password2
        }

        response = self.client.post(
            self.register_url, incomplete_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        self.assertIn('password', response.data)
        self.assertIn('password2', response.data)

    def test_user_login_success(self):
        """Test successful login with correct credentials"""
        login_data = {
            'username': 'existinguser',
            'password': 'ExistingPass123!'
        }

        response = self.client.post(self.login_url, login_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_user_login_wrong_password(self):
        """Test login fails with incorrect password"""
        login_data = {
            'username': 'existinguser',
            'password': 'WrongPassword123!'
        }

        response = self.client.post(self.login_url, login_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_login_nonexistent_user(self):
        """Test login fails with non-existent username"""
        login_data = {
            'username': 'nonexistentuser',
            'password': 'SomePassword123!'
        }

        response = self.client.post(self.login_url, login_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_login_missing_credentials(self):
        """Test login fails with missing username or password"""
        # Missing password
        incomplete_data = {'username': 'existinguser'}
        response = self.client.post(
            self.login_url, incomplete_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Missing username
        incomplete_data = {'password': 'ExistingPass123!'}
        response = self.client.post(
            self.login_url, incomplete_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_jwt_token_structure(self):
        """Test that JWT tokens are properly formatted"""
        # Register a new user
        response = self.client.post(
            self.register_url, self.valid_user_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify token structure
        access_token = response.data['access']
        refresh_token = response.data['refresh']

        # JWT tokens should have 3 parts separated by dots
        self.assertEqual(len(access_token.split('.')), 3)
        self.assertEqual(len(refresh_token.split('.')), 3)

        # Tokens should be strings and not empty
        self.assertIsInstance(access_token, str)
        self.assertIsInstance(refresh_token, str)
        self.assertGreater(len(access_token), 0)
        self.assertGreater(len(refresh_token), 0)

    def test_username_length_validation(self):
        """Test username length validation (min 3, max 150 characters)"""
        # Test username too short
        short_username_data = self.valid_user_data.copy()
        short_username_data['username'] = 'ab'  # Too short

        response = self.client.post(
            self.register_url, short_username_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test username too long
        long_username_data = self.valid_user_data.copy()
        long_username_data['username'] = 'a' * 151  # Too long

        response = self.client.post(
            self.register_url, long_username_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_case_insensitive_email_validation(self):
        """Test that email validation is case insensitive"""
        # Register user with lowercase email
        user_data = self.valid_user_data.copy()
        user_data['email'] = 'test@example.com'
        response = self.client.post(
            self.register_url, user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Try to register with same email in different case
        duplicate_data = self.valid_user_data.copy()
        duplicate_data['username'] = 'anotheruser'
        # Same email, different case
        duplicate_data['email'] = 'TEST@EXAMPLE.COM'

        response = self.client.post(
            self.register_url, duplicate_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_user_login_case_sensitivity(self):
        """Test login username case sensitivity"""
        # Try login with different case username
        login_data = {
            'username': 'EXISTINGUSER',  # Different case
            'password': 'ExistingPass123!'
        }

        response = self.client.post(self.login_url, login_data, format='json')
        # Django usernames are case sensitive by default
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
