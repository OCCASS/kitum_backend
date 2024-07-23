from rest_framework.exceptions import APIException


class TaskAlreadyAnswered(APIException):
    status_code = 400
    default_detail = "Already answered to task."
    default_code = "already_answered"


class TaskAlreadySkipped(APIException):
    status_code = 400
    default_detail = "Task already skipped."
    default_code = "already_skipped"
