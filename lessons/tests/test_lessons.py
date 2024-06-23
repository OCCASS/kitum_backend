from django.urls import reverse
from lessons.models import *
from rest_framework.test import APITestCase


class TestLessons(APITestCase):
    def _create_lesson(self):
        Lesson(title="Title", content="Content").save()

    def test_get_empty_lessons(self):
        response = self.client.get(reverse("lessons"))
        self.assertEqual(len(response.data), 0)

    def test_get_lessons(self):
        self._create_lesson()
        response = self.client.get(reverse("lessons"))
        self.assertEqual(len(response.data), 1)
        self._create_lesson()
        response = self.client.get(reverse("lessons"))
        self.assertEqual(len(response.data), 2)
