"""Roles and permissions: the one place that defines who may do what.

Endpoints are guarded by permissions (see `require_permission` in
app/api/deps.py), so changing what a role may do means editing
ROLE_PERMISSIONS. The frontend receives the same permissions from
GET /users/me.
"""

from enum import StrEnum


class UserRole(StrEnum):
    ADMIN = "admin"
    MANAGER = "manager"
    MEMBER = "member"


class Permission(StrEnum):
    USERS_READ = "users:read"
    # Create, update and delete users, including their role and active status.
    USERS_MANAGE = "users:manage"
    METRICS_READ = "metrics:read"
    # Read, update and delete items owned by other users.
    ITEMS_MANAGE_ALL = "items:manage_all"
    # Admin utilities: test email, password-recovery email preview.
    SYSTEM_MANAGE = "system:manage"


ROLE_PERMISSIONS: dict[UserRole, frozenset[Permission]] = {
    UserRole.ADMIN: frozenset(Permission),
    UserRole.MANAGER: frozenset({Permission.USERS_READ, Permission.METRICS_READ}),
    UserRole.MEMBER: frozenset(),
}


def permissions_for(role: UserRole) -> frozenset[Permission]:
    # An unknown role gets no permissions: fail closed.
    return ROLE_PERMISSIONS.get(role, frozenset())


def has_permission(role: UserRole, permission: Permission) -> bool:
    return permission in permissions_for(role)
