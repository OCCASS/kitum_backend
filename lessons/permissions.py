from rest_framework.permissions import BasePermission


class IsLessonOpened(BasePermission):
    def has_object_permission(self, request, view, obj):
        return not obj.is_closed
