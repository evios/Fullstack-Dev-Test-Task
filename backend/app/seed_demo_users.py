"""Create demo accounts for trying the three access levels locally."""

import logging

from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.core.db import engine, init_db
from app.core.permissions import UserRole
from app.models import UserCreate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# The admin is FIRST_SUPERUSER, created by init_db. Every demo account uses
# FIRST_SUPERUSER_PASSWORD.
DEMO_USERS = {
    "manager@example.com": UserRole.MANAGER,
    "member@example.com": UserRole.MEMBER,
}


def main() -> None:
    if settings.FASTAPI_ENV != "development":
        raise SystemExit("Demo users can only be created with FASTAPI_ENV=development")
    with Session(engine) as session:
        init_db(session)
        for email, role in DEMO_USERS.items():
            if crud.get_user_by_email(session=session, email=email):
                logger.info("%s already exists", email)
                continue
            user_in = UserCreate(
                email=email,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                full_name=f"Demo {role.title()}",
                role=role,
            )
            crud.create_user(session=session, user_create=user_in)
            logger.info("Created %s (%s)", email, role)


if __name__ == "__main__":
    main()
