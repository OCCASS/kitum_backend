from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

from lessons.models import *

User = get_user_model()


class TestAnswerSkipTask(APITestCase):
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
        self.task = Task(lesson=self.lesson, correct_answer="123")
        self.task.save()

        self.user_lesson = UserLesson(lesson=self.lesson, user=self.user)
        self.user_lesson.save()
        self.user_task = UserTask(task=self.task, lesson=self.user_lesson)
        self.user_task.save()

    def get_url(self, name: str) -> str:
        return reverse(name, kwargs={"pk": self.lesson.pk, "task_pk": self.task.pk})

    def get_user_task(self) -> UserTask:
        return UserTask.objects.get(
            lesson__lesson__pk=self.lesson.pk,
            lesson__user=self.user,
            task__pk=self.task.pk,
        )

    def login(self):
        self.client.force_authenticate(user=self.user)

    def logout(self):
        self.client.force_authenticate(user=None)

    def test_answer_skip_as_unauthorized(self):
        response = self.client.post(self.get_url("answer_task"))
        self.assertEqual(response.status_code, 401)

        response = self.client.post(self.get_url("skip_task"))
        self.assertEqual(response.status_code, 401)

    def test_incorrect_answer(self):
        self.login()

        answer = "incorrect"
        response = self.client.post(self.get_url("answer_task"), {"answer": answer})
        self.assertEqual(response.status_code, 200)

        user_task = self.get_user_task()
        self.assertFalse(user_task.is_correct)
        self.assertEqual(user_task.answer, answer)

        self.logout()

    def test_correct_answer(self):
        self.login()

        answer = self.task.correct_answer
        response = self.client.post(self.get_url("answer_task"), {"answer": answer})
        self.assertEqual(response.status_code, 200)

        user_task = self.get_user_task()
        self.assertTrue(user_task.is_correct)
        self.assertEqual(user_task.answer, answer)

        self.logout()

    def test_answer_to_already_answered(self):
        self.login()

        self.user_task.answer = "some answer"
        self.user_task.save()

        response = self.client.post(self.get_url("answer_task"), {"answer": "answer"})
        self.assertEqual(response.status_code, 400)

        self.user_task.answer = None
        self.user_task.save()

        self.logout()

    def test_skip(self):
        self.login()

        response = self.client.post(self.get_url("skip_task"))
        self.assertEqual(response.status_code, 200)

        user_task = self.get_user_task()
        self.assertTrue(user_task.is_skipped)

        self.logout()

    def test_skip_already_skipped(self):
        self.login()

        self.user_task.is_skipped = True
        self.user_task.save()

        response = self.client.post(self.get_url("skip_task"))
        self.assertEqual(response.status_code, 400)

        self.user_task.is_skipped = False
        self.user_task.save()

        self.logout()
