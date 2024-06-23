import uuid

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

        self.lesson = Lesson(title="Title", content="Content")
        self.lesson.save()
        task = Task(lesson=self.lesson, kim_number=1, cost=1, correct_answer="123")
        task.save()

        self.user_lesson = UserLesson(lesson=self.lesson, user=self.user)
        self.user_lesson.save()
        user_task = UserTask(task=task, lesson=self.user_lesson)
        user_task.save()

    def login(self):
        self.client.force_authenticate(user=self.user)

    def logout(self):
        self.client.force_authenticate(user=None)

    def test_get_as_unauthorized(self):
        response = self.client.get(reverse("my_lesson", kwargs={"pk": self.lesson.pk}))
        self.assertEqual(response.status_code, 401)

    def test_get_closed_as_authorized(self):
        self.login()

        response = self.client.get(reverse("my_lesson", kwargs={"pk": self.lesson.pk}))
        self.assertEqual(response.status_code, 403)

        self.logout()

    def test_get_opened_as_authorized(self):
        self.login()

        self.user_lesson.is_closed = False
        self.user_lesson.save()

        response = self.client.get(reverse("my_lesson", kwargs={"pk": self.lesson.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["tasks"]), 1)

        self.user_lesson.is_closed = True
        self.user_lesson.save()

        self.logout()

    def test_invalid_pk(self):
        self.login()

        random_id = uuid.uuid4()
        response = self.client.get(reverse("my_lesson", kwargs={"pk": random_id}))
        self.assertEqual(response.status_code, 404)

        self.logout()
