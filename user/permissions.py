from rest_framework.permissions import BasePermission


class IsUserHaveSubscription(BasePermission):
    def has_permission(self, request, view):
        return request.user.subscription.exists()
