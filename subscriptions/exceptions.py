from rest_framework import status
from rest_framework.exceptions import APIException


class UserAlreadyHaveSubscription(APIException):
    default_code = "user_already_have_subscription"
    default_detail = "У пользователя уже есть подписка."
    status_code = status.HTTP_400_BAD_REQUEST
