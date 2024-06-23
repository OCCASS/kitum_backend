from rest_framework.exceptions import APIException


class TaskAlreadyAnswered(APIException):
    status_code = 400
    default_detail = "Already answered to task."


class TaskAlreadySkipped(APIException):
    status_code = 400
    default_detail = "Task alredy skipped."


class LessonClosed(APIException):
    status_code = 403
    default_detail = "Lesson closed."


class LessonAlreadyCompleted(APIException):
    status_code = 400
    default_detauil = "Lesson already completed."


class LessonTasksAlreadyCompleted(APIException):
    status_code = 400
    default_detauil = "Lesson tasks already completed."


class LessonAlreadySkipped(APIException):
    status_code = 400
    default_detauil = "Lesson already skipped."
