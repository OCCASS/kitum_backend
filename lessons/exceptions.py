from rest_framework.exceptions import APIException


class LessonClosed(APIException):
    status_code = 403
    default_detail = "Lesson closed."
    default_code = "lesson_closed"


class LessonAlreadyCompleted(APIException):
    status_code = 400
    default_detail = "Lesson already completed."
    default_code = "already_completed"


class LessonTasksAlreadyCompleted(APIException):
    status_code = 400
    default_detail = "Lesson tasks already completed."
    default_code = "tasks_already_completed"


class LessonAlreadySkipped(APIException):
    status_code = 400
    default_detail = "Lesson already skipped."
    default_code = "already_skipped"


class LessonNotIncludesTask(APIException):
    status_code = 400
    default_detail = "Lesson not includes this task."
