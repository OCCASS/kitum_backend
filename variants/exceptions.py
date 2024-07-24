from rest_framework.exceptions import APIException


class VariantAlreadyCompleted(APIException):
    status_code = 400
    default_detail = "Variant already completed."


class VariantAlreadyStarted(APIException):
    status_code = 400
    default_detail = "Variant already started."


class VariantNotStarted(APIException):
    status_code = 400
    default_detail = "Variant not started."


class VariantCompleted(APIException):
    status_code = 400
    default_detail = "Variant completed."


class VariantNotIncludesTask(APIException):
    status_code = 400
    default_detail = "Variant not includes this task."


class AnswerIsEmptyError(APIException):
    status_code = 400
    default_detail = "Answer is empty."
