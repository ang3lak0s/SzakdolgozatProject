from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase


class AuthApiTests(APITestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.valid_user_data = {
            'username': 'arduino_user',
            'password': 'SecureHardwarePassword123!',
            'email': 'user@hardware.local'
        }

    def test_register_user_success(self):
        response = self.client.post(self.register_url, self.valid_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get('message'), 'Sikeres regisztráció!')

        # Verify user is in database with properly hashed password
        user = User.objects.filter(username='arduino_user').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'user@hardware.local')
        self.assertTrue(user.check_password('SecureHardwarePassword123!'))

    def test_register_duplicate_username_fails(self):
        User.objects.create_user(**self.valid_user_data)
        response = self.client.post(self.register_url, self.valid_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_register_missing_required_fields_fails(self):
        response = self.client.post(self.register_url, {'username': 'incomplete_user'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_user_success_returns_token(self):
        User.objects.create_user(**self.valid_user_data)
        login_payload = {
            'username': 'arduino_user',
            'password': 'SecureHardwarePassword123!'
        }
        response = self.client.post(self.login_url, login_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertEqual(response.data.get('message'), 'Sikeres belépés!')

        # Verify token in database
        token = Token.objects.filter(key=response.data['token']).first()
        self.assertIsNotNone(token)
        self.assertEqual(token.user.username, 'arduino_user')

    def test_login_user_invalid_credentials_fails(self):
        User.objects.create_user(**self.valid_user_data)
        login_payload = {
            'username': 'arduino_user',
            'password': 'WrongPassword123'
        }
        response = self.client.post(self.login_url, login_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)

    def test_login_nonexistent_user_fails(self):
        login_payload = {
            'username': 'ghost_user',
            'password': 'SomePassword123'
        }
        response = self.client.post(self.login_url, login_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
