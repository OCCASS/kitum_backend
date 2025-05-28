from rest_framework.permissions import BasePermission

from subscriptions.models import UserSubscription


class IsLessonOpened(BasePermission):
    def has_object_permission(self, request, view, obj) -> bool:
        return not obj.is_closed


class HaveHomeworkAccess(BasePermission):
    def has_permission(self, request, view) -> bool:
        has_with_home_work = UserSubscription.objects.filter(
            user=request.user,
            status=UserSubscription.ACTIVE,
            subscription__with_home_work=True,
        ).exists()
        return has_with_home_work
