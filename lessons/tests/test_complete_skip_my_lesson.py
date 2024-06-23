import uuid

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, force_authenticate

from lessons.models import *

User = get_user_model()


class TestCompleteSkipUserLesson(APITestCase):
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

        self.user_lesson = UserLesson(lesson=self.lesson, user=self.user)
        self.user_lesson.save()

    def get_user_lesson(self) -> UserLesson:
        return UserLesson.objects.get(lesson__pk=self.lesson.pk, user=self.user)

    def login(self):
        self.client.force_authenticate(user=self.user)

    def logout(self):
        self.client.force_authenticate(user=None)

    def test_complete_skip_as_unauthorized(self):
        response = self.client.post(
            reverse("complete_my_lesson", kwargs={"pk": self.lesson.pk})
        )
        self.assertEqual(response.status_code, 401)

        response = self.client.post(
            reverse("skip_my_lesson", kwargs={"pk": self.lesson.pk})
        )
        self.assertEqual(response.status_code, 401)

    def test_complete_skip_closed_as_authorized(self):
        self.login()

        response = self.client.post(
            reverse("complete_my_lesson", kwargs={"pk": self.lesson.pk})
        )
        self.assertEqual(response.status_code, 403)

        response = self.client.post(
            reverse("skip_my_lesson", kwargs={"pk": self.lesson.pk})
        )
        self.assertEqual(response.status_code, 403)

        self.logout()

    def test_invalid_pk(self):
        self.login()

        random_id = uuid.uuid4()
        response = self.client.post(
            reverse("complete_my_lesson", kwargs={"pk": random_id})
        )
        self.assertEqual(response.status_code, 404)

        response = self.client.post(reverse("skip_my_lesson", kwargs={"pk": random_id}))
        self.assertEqual(response.status_code, 404)

        self.logout()

    def test_complete(self):
        self.login()

        self.user_lesson.is_closed = False
        self.user_lesson.save()

        response = self.client.post(
            reverse("complete_my_lesson", kwargs={"pk": self.lesson.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.get_user_lesson().is_completed)

        self.logout()

    def test_complete_already_completed(self):
        self.login()

        self.user_lesson.is_closed = False
        self.user_lesson.is_completed = True
        self.user_lesson.save()

        response = self.client.post(
            reverse("complete_my_lesson", kwargs={"pk": self.lesson.pk})
        )
        self.assertEqual(response.status_code, 400)

        self.logout()

    def test_complete_already_skipped(self):
        self.login()

        self.user_lesson.is_closed = False
        self.user_lesson.is_skipped = True
        self.user_lesson.save()

        response = self.client.post(
            reverse("complete_my_lesson", kwargs={"pk": self.lesson.pk})
        )
        self.assertEqual(response.status_code, 400)

        self.logout()

    def test_skip(self):
        self.login()

        self.user_lesson.is_closed = False
        self.user_lesson.save()

        response = self.client.post(
            reverse("skip_my_lesson", kwargs={"pk": self.lesson.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.get_user_lesson().is_skipped)

        self.logout()

    def test_skip_already_skip(self):
        self.login()

        self.user_lesson.is_closed = False
        self.user_lesson.is_skipped = True
        self.user_lesson.save()

        response = self.client.post(
            reverse("skip_my_lesson", kwargs={"pk": self.lesson.pk})
        )
        self.assertEqual(response.status_code, 400)

        self.logout()

    def test_skip_already_completed(self):
        self.login()

        self.user_lesson.is_closed = False
        self.user_lesson.is_completed = True
        self.user_lesson.save()

        response = self.client.post(
            reverse("skip_my_lesson", kwargs={"pk": self.lesson.pk})
        )
        self.assertEqual(response.status_code, 400)

        self.logout()
