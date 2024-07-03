from rest_framework.exceptions import APIException


class PasswordResetRequestAlreadyCreated(APIException):
    status_code = 400
    default_detail = "Password reset request already created."


class ConfirmMailTokenIsInvalid(APIException):
    status_code = 400
    default_detail = "Confirm mail token is invalid."
