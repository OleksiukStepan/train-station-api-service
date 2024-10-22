from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.request import Request
from rest_framework.views import View


class IsAdminOrIfAuthenticatedReadOnly(BasePermission):
    def has_permission(self, request: Request, view: View) -> bool:
        return (
            request.method in SAFE_METHODS
            and request.user.is_authenticated
        ) or request.user.is_staff
