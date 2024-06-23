from rest_framework.exceptions import APIException


class VariantAlreadyCompleted(APIException):
    status_code = 400
    default_detauil = "Variant already completed."


class VariantAlreadyStarted(APIException):
    status_code = 400
    default_detauil = "Variant already started."
