from typing import Any

from fastapi import APIRouter, Depends
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep, get_current_active_manager_or_admin
from app.models import User

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/", dependencies=[Depends(get_current_active_manager_or_admin)])
def read_metrics(*, session: SessionDep, current_user: CurrentUser) -> Any:
    """Return basic user metrics for manager/admin views."""
    total_users = session.exec(select(func.count()).select_from(User)).one()
    active_users = session.exec(
        select(func.count()).select_from(User).where(User.is_active.is_(True))
    ).one()
    return {
        "total_users": total_users,
        "active_users": active_users,
        "role": current_user.role.value,
    }