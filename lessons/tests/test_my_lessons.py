from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

from lessons.models import *

User = get_user_model()


class TestUserLessons(APITestCase):
    _email = "random@email.com"
    _password = "qwerty12345!"

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email=self._email,
            password=self._password,
            first_name="First",
            last_name="Last",
        )
        lesson = Lesson(title="Title", content="Content")
        lesson.save()
        user_lesson = UserLesson(lesson=lesson, user=self.user)
        user_lesson.save()

    def login(self):
        self.client.force_authenticate(user=self.user)

    def logout(self):
        self.client.force_authenticate(user=None)

    def test_unauthorized(self):
        response = self.client.get(reverse("my_lessons"))
        self.assertEqual(response.status_code, 401)

    def test_authorized(self):
        self.login()

        response = self.client.get(reverse("my_lessons"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        self.logout()
