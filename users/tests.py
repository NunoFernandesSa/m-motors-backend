from django.test import TestCase
from django.contrib.auth.models import User, Group
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator


class UserRegistrationTest(APITestCase):
    def setUp(self):
        self.register_url = "/api/auth/register/"
        self.valid_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
            "password2": "testpass123"
        }

    def test_register_success(self):
        response = self.client.post(self.register_url, self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        user = User.objects.first()
        self.assertEqual(user.username, "testuser")
        self.assertTrue(user.groups.filter(name='user').exists())

    def test_register_duplicate_email(self):
        User.objects.create_user(username="existing", email=self.valid_data['email'], password="pass")
        response = self.client.post(self.register_url, self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_register_passwords_mismatch(self):
        data = self.valid_data.copy()
        data['password2'] = 'different'
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)


class UserLoginTest(APITestCase):
    def setUp(self):
        self.login_url = "/api/auth/login/"
        self.user = User.objects.create_user(username="loginuser", password="loginpass")

    def test_login_success(self):
        data = {"username": "loginuser", "password": "loginpass"}
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('message' in response.data or 'access' in response.data)

    def test_login_invalid_credentials(self):
        data = {"username": "loginuser", "password": "wrongpass"}
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserProfileTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="profileuser", password="profilepass")
        self.client.force_authenticate(user=self.user)
        self.profile_url = "/api/auth/me/"

    def test_get_profile_authenticated(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], "profileuser")

    def test_get_profile_unauthenticated(self):
        self.client.force_authenticate(user=None)  # désauthentifier
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_profile_patch(self):
        data = {"email": "newemail@example.com"}
        response = self.client.patch(self.profile_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "newemail@example.com")


class UserLogoutTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="logoutuser", password="logoutpass")
        self.client.force_authenticate(user=self.user)
        self.logout_url = "/api/auth/logout/"

    def test_logout(self):
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "Déconnexion réussie")


class PasswordResetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="resetuser", email="reset@example.com", password="oldpass"
        )
        self.reset_url = "/api/auth/password/reset/"
        self.reset_confirm_url = "/api/auth/password/reset/confirm/"

    def test_password_reset_request(self):
        data = {"email": "reset@example.com"}
        response = self.client.post(self.reset_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], "Un email de réinitialisation a été envoyé.")

    def test_password_reset_confirm(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        data = {"uid": uid, "token": token, "new_password": "newpass123"}
        response = self.client.post(self.reset_confirm_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpass123"))

