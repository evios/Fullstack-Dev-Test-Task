import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.core.permissions import Permission, UserRole
from tests.utils.item import create_random_item
from tests.utils.user import create_random_user, create_user_with_role
from tests.utils.utils import random_email, random_lower_string

API = settings.API_V1_STR


@pytest.mark.parametrize(
    ("role", "method", "path", "expected_status"),
    [
        (UserRole.ADMIN, "GET", "/users/", 200),
        (UserRole.MANAGER, "GET", "/users/", 200),
        (UserRole.MEMBER, "GET", "/users/", 403),
        (UserRole.MANAGER, "GET", "/users/{user_id}", 200),
        (UserRole.MEMBER, "GET", "/users/{user_id}", 403),
        (UserRole.ADMIN, "GET", "/metrics/", 200),
        (UserRole.MANAGER, "GET", "/metrics/", 200),
        (UserRole.MEMBER, "GET", "/metrics/", 403),
        (UserRole.MANAGER, "POST", "/users/", 403),
        (UserRole.MEMBER, "POST", "/users/", 403),
        (UserRole.MANAGER, "DELETE", "/users/{user_id}", 403),
        (UserRole.MEMBER, "DELETE", "/users/{user_id}", 403),
        (UserRole.ADMIN, "GET", "/items/{item_id}", 200),
        (UserRole.MANAGER, "GET", "/items/{item_id}", 403),
        (UserRole.MANAGER, "POST", "/utils/test-email/?email_to=a@example.com", 403),
    ],
)
def test_role_access(
    client: TestClient,
    db: Session,
    role: UserRole,
    method: str,
    path: str,
    expected_status: int,
) -> None:
    _, headers = create_user_with_role(client=client, db=db, role=role)
    other_user = create_random_user(db)
    item = create_random_item(db)
    # A valid body, so that a 403 can't be hiding a validation error.
    body = (
        {"email": random_email(), "password": random_lower_string()}
        if method == "POST"
        else None
    )
    url = API + path.format(user_id=other_user.id, item_id=item.id)
    r = client.request(method, url, headers=headers, json=body)
    assert r.status_code == expected_status


def test_invalid_sessions_get_401(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    assert client.get(f"{API}/users/me").status_code == 401
    bad_token = {"Authorization": "Bearer not-a-jwt"}
    assert client.get(f"{API}/users/me", headers=bad_token).status_code == 401

    user, headers = create_user_with_role(client=client, db=db, role=UserRole.MEMBER)
    client.delete(f"{API}/users/{user.id}", headers=superuser_token_headers)
    assert client.get(f"{API}/users/me", headers=headers).status_code == 401


@pytest.mark.parametrize(
    ("role", "expected_permissions"),
    [
        (UserRole.ADMIN, sorted(Permission)),
        (UserRole.MANAGER, ["metrics:read", "users:read"]),
        (UserRole.MEMBER, []),
    ],
)
def test_read_user_me_returns_permissions(
    client: TestClient,
    db: Session,
    role: UserRole,
    expected_permissions: list[str],
) -> None:
    _, headers = create_user_with_role(client=client, db=db, role=role)
    r = client.get(f"{API}/users/me", headers=headers)
    assert r.status_code == 200
    assert r.json()["role"] == role
    assert r.json()["permissions"] == expected_permissions


def test_member_cannot_change_own_role(client: TestClient, db: Session) -> None:
    user, headers = create_user_with_role(client=client, db=db, role=UserRole.MEMBER)
    r = client.patch(f"{API}/users/me", headers=headers, json={"role": "admin"})
    assert r.status_code == 200
    db.refresh(user)
    assert user.role == UserRole.MEMBER


def test_signup_always_creates_a_member(client: TestClient) -> None:
    data = {"email": random_email(), "password": random_lower_string()}
    r = client.post(f"{API}/users/signup", json={**data, "role": "admin"})
    assert r.status_code == 200
    assert r.json()["role"] == UserRole.MEMBER


@pytest.mark.parametrize("role", [UserRole.MANAGER, UserRole.MEMBER])
@pytest.mark.parametrize("change", [{"role": "admin"}, {"is_active": False}])
def test_only_admins_change_access(
    client: TestClient, db: Session, role: UserRole, change: dict[str, object]
) -> None:
    _, headers = create_user_with_role(client=client, db=db, role=role)
    target = create_random_user(db)
    r = client.patch(f"{API}/users/{target.id}", headers=headers, json=change)
    assert r.status_code == 403
    db.refresh(target)
    assert target.role == UserRole.MEMBER
    assert target.is_active is True


@pytest.mark.parametrize("change", [{"role": "member"}, {"is_active": False}])
def test_admin_cannot_remove_own_access(
    client: TestClient, db: Session, change: dict[str, object]
) -> None:
    admin, headers = create_user_with_role(client=client, db=db, role=UserRole.ADMIN)
    r = client.patch(f"{API}/users/{admin.id}", headers=headers, json=change)
    assert r.status_code == 403
    db.refresh(admin)
    assert admin.role == UserRole.ADMIN
    assert admin.is_active is True


def test_role_change_applies_to_existing_token(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    manager, headers = create_user_with_role(
        client=client, db=db, role=UserRole.MANAGER
    )
    assert client.get(f"{API}/users/", headers=headers).status_code == 200

    r = client.patch(
        f"{API}/users/{manager.id}",
        headers=superuser_token_headers,
        json={"role": "member"},
    )
    assert r.status_code == 200

    # Same token, new rights: the role is read from the database on each request.
    assert client.get(f"{API}/users/", headers=headers).status_code == 403


def test_deactivation_ends_existing_session(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    member, headers = create_user_with_role(client=client, db=db, role=UserRole.MEMBER)
    assert client.get(f"{API}/users/me", headers=headers).status_code == 200

    r = client.patch(
        f"{API}/users/{member.id}",
        headers=superuser_token_headers,
        json={"is_active": False},
    )
    assert r.status_code == 200

    r = client.get(f"{API}/users/me", headers=headers)
    assert r.status_code == 401
    assert r.headers["www-authenticate"] == "Bearer"


def test_role_cannot_be_set_to_null(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    user = create_random_user(db)
    r = client.patch(
        f"{API}/users/{user.id}", headers=superuser_token_headers, json={"role": None}
    )
    assert r.status_code == 422
