import pytest
from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.seed_demo_users import DEMO_USERS, main


def test_seed_demo_users_creates_each_role(db: Session) -> None:
    main()
    main()  # Running it again must neither fail nor create duplicates.
    for email, role in DEMO_USERS.items():
        user = crud.get_user_by_email(session=db, email=email)
        assert user
        assert user.role == role


def test_seed_demo_users_refuses_outside_development(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "FASTAPI_ENV", None)
    with pytest.raises(SystemExit):
        main()
