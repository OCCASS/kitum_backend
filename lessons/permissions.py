from rest_framework.permissions import BasePermission


class IsLessonOpened(BasePermission):
    def has_object_permission(self, request, view, obj) -> bool:
        return not obj.is_closed


class HaveHomeworkAccess(BasePermission):
    def has_permission(self, request, view) -> bool:
        user_subscription = request.user.get_subscription()
        if user_subscription:
            return user_subscription.subscription.with_home_work
        return False
