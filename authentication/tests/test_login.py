from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.response import Response
from rest_framework.test import APITestCase

User = get_user_model()


class LoginTest(APITestCase):
    _login_url = reverse("login")
    _email = "correctemail@domen.com"
    _password = "Test123456789Test!"

    def setUp(self):
        User.objects.create_user(
            email=self._email,
            password=self._password,
            first_name="First",
            last_name="Last"
        )

    def _do_login(self, email: str, password: str) -> Response:
        return self.client.post(self._login_url, {"email": email, "password": password})

    def test_login_with_correct_credentials(self):
        """Test correct login to account"""
        response = self._do_login(self._email, self._password)
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertNotIn("access", response.cookies)
        self.assertNotIn("refresh", response.data)
        self.assertIn("refresh", response.cookies)

    def test_login_without_password(self):
        """Test login if password is not passed"""
        response = self.client.post(self._login_url, {"email": self._email})
        self.assertEqual(response.status_code, 400)
        self.assertIn("password", response.data)

    def test_login_without_email(self):
        """Test login if email is not passed"""
        response = self.client.post(self._login_url, {"password": self._password})
        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.data)

    def test_login_with_incorrect_email(self):
        """Test login with incorrect email"""
        response = self._do_login("incorrectemail@domen.com", self._password)
        self.assertEqual(response.status_code, 401)

    def test_login_with_incorrect_password(self):
        """Test login with incorrect password"""
        response = self._do_login(self._email, "IncorrectPassword")
        self.assertEqual(response.status_code, 401)

    def test_login_with_incorrect_password_and_email(self):
        """Test login with incorrect email and password"""
        response = self._do_login("incorrectemail@domen.com", "IncorrectPassword")
        self.assertEqual(response.status_code, 401)
