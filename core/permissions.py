from rest_framework.permissions import BasePermission


class IsCustomer(BasePermission):
    """Allows access only to authenticated customers."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == "customer"
        )


class IsTechnician(BasePermission):
    """Allows access only to authenticated technicians."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == "technician"
        )


class IsSupportAgent(BasePermission):
    """Allows access to support agents."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in ("support_agent", "system_admin")
        )


class IsFinanceAdmin(BasePermission):
    """Allows access to finance admins."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in ("finance_admin", "system_admin")
        )


class IsSystemAdmin(BasePermission):
    """Allows access only to system administrators."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.role == "system_admin" or request.user.is_superuser)
        )


class IsStaffOrAdmin(BasePermission):
    """Allows access to any administrative role."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in ("support_agent", "finance_admin", "system_admin")
        )
