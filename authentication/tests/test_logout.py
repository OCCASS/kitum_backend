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
        self.user = User.objects.create_user(
            email=self._email,
            password=self._password,
            first_name="First",
            last_name="Last",
        )

    def _do_login(self, email: str, password: str) -> Response:
        return self.client.post(self._login_url, {"email": email, "password": password})

    def test_successfully_logout(self):
        """Test correct user logout"""
        login_response = self._do_login(self._email, self._password)
        self.client.cookies["refresh"] = login_response.cookies.get("refresh")
        response = self.client.post(reverse("logout"))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("refresh", response.cookies)

        # TODO: add private call
        # Try to get private data after logout
        # response = self.client.post(reverse("create_order"),
        # {"title": "Title", "text": "Text", "author": str(self.user.id)})
        # self.assertEqual(response.status_code, 401)
        # self.client.cookies.clear()

    def test_logout_without_refresh_token(self):
        """Testing logout without refresh token"""
        response = self.client.post(reverse("logout"), {})
        self.assertEqual(response.status_code, 401)
