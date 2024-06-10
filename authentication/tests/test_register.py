import itertools

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

User = get_user_model()


class TestRegistration(APITestCase):
    _register_url = reverse("register")
    _email = "email@domen.com"
    _password = "123456789Password!"
    _first_name = "First"
    _last_name = "Last"

    def _get_registrations_data(self, **replace_fields) -> dict:
        d = {
            "email": self._email,
            "password": self._password,
            "first_name": self._first_name,
            "last_name": self._last_name,
        }
        d.update(**replace_fields)
        return d

    def test_correct_register(self):
        """Test registration with valid data"""
        response = self.client.post(self._register_url, self._get_registrations_data())
        self.assertEqual(response.status_code, 201)
        self.assertIn("email", response.data["user"])
        self.assertIn("first_name", response.data["user"])
        self.assertIn("last_name", response.data["user"])
        self.assertNotIn("password", response.data["user"])
        self.assertIn("access", response.data)
        self.assertNotIn("refresh", response.data)
        self.assertIn("refresh", response.cookies)

        user = User.objects.get(email=self._email)
        self.assertEqual(user.first_name, self._first_name)
        self.assertEqual(user.last_name, self._last_name)
        self.assertNotEqual(user.password, self._password)
        self.assertIsNotNone(user.password)

    def test_register_without_some_argument(self):
        """Test if not all arguments for registration was given"""
        response = self.client.post(self._register_url, {})
        self.assertEqual(response.status_code, 400)
        registration_data = self._get_registrations_data()
        for keys_set in itertools.combinations(registration_data.keys(), 3):
            data = {k: registration_data[k] for k in keys_set}
            response = self.client.post(self._register_url, data)
            self.assertEqual(response.status_code, 400)

    def test_registration_email_validation(self):
        """Test registration with invalid email (without @ and domen)"""
        invalid_emails = ("@domen.com", "name", "name@", "name@domen")
        for email in invalid_emails:
            response = self.client.post(
                self._register_url, self._get_registrations_data(email=email)
            )
            self.assertEqual(response.status_code, 400)
            self.assertIn("email", response.data)

    def test_registration_password_validation(self):
        """Test registration with invalid password (short and only digits)"""
        invalid_passwords = ("short", "123456789")
        for password in invalid_passwords:
            response = self.client.post(
                self._register_url, self._get_registrations_data(password=password)
            )
            self.assertEqual(response.status_code, 400)
            self.assertIn("password", response.data)
