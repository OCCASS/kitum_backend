from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.response import Response
from rest_framework.test import APITestCase

User = get_user_model()


class TestJWT(APITestCase):
    _email = "email@email.com"
    _password = "123456789Password!"

    def setUp(self) -> None:
        User.objects.create_user(email=self._email, password=self._password, first_name="First", last_name="Last")

    def _do_login(self) -> Response:
        return self.client.post(reverse("login"), {"email": self._email, "password": self._password})

    def test_token_refresh(self):
        """Test JWT token refresh"""
        login_response = self._do_login()
        refresh_token = login_response.cookies.get("refresh").value

        response = self.client.post(reverse("refresh_token"), {"refresh": refresh_token})
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertNotIn("access", response.cookies)
        self.assertNotIn("refresh", response.data)
        self.assertIn("refresh", response.cookies)

    def test_token_refresh_with_out_refresh_token(self):
        """Test JWT token refresh without refresh token"""
        response = self.client.post(reverse("refresh_token"))
        self.assertEqual(response.status_code, 401)

    def test_token_refresh_token_verification(self):
        """Test valid access token verification"""
        login_response = self._do_login()
        refresh_token = login_response.cookies.get("refresh").value
        response = self.client.post(reverse("verify_token"), {"token": refresh_token})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {})

    def test_token_access_token_verification(self):
        """Test valid refresh token verification"""
        login_response = self._do_login()
        access_token = login_response.data.get("access")
        response = self.client.post(reverse("verify_token"), {"token": access_token})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {})

    def test_token_verification_with_invalid_token(self):
        """Test token verification with invalid token"""
        response = self.client.post(reverse("verify_token"), {"token": "invalid_token"})
        self.assertEqual(response.status_code, 401)

    def test_token_verification_without_token(self):
        """Test token verification without data"""
        response = self.client.post(reverse("verify_token"), {})
        self.assertEqual(response.status_code, 400)
