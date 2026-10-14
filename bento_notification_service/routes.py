import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from .authz import require_view_notifications
from .db import SessionDep
from .models import Notification
from .pydantic_models import NotificationResponse

__all__ = ["notification_router"]

# NOTE: the /service-info endpoint is provided by BentoFastAPI (see app.py), so it isn't defined here.
#  - A malformed notification UUID in the path results in a validation error, which bento_lib's exception handlers
#    turn into a 400 (the Flask version of this service used to return a 404 in that case).
notification_router = APIRouter(prefix="/notifications", dependencies=[Depends(require_view_notifications)])


class NotificationController:
    @staticmethod
    def get_notifications(session: Session) -> list[Notification]:
        return list(session.scalars(select(Notification)).all())

    @staticmethod
    def get_notification_by_id(session: Session, n_id: str | uuid.UUID) -> Notification | None:
        return session.scalars(select(Notification).where(Notification.id == str(n_id))).one_or_none()

    @staticmethod
    def mark_all_notifications_as_read(session: Session):
        session.execute(update(Notification).where(Notification._read == False).values(_read=True))
        session.commit()


def _get_notification_or_404(session: Session, n_id: uuid.UUID) -> Notification:
    notification = NotificationController.get_notification_by_id(session, n_id)
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Notification {n_id} not found")
    return notification


@notification_router.get("", response_model=list[NotificationResponse])
def notification_list(session: SessionDep):
    return [n.to_pydantic() for n in NotificationController.get_notifications(session)]


@notification_router.put("/all-read", status_code=status.HTTP_204_NO_CONTENT)
def notification_all_read(session: SessionDep):
    NotificationController.mark_all_notifications_as_read(session)


@notification_router.get("/{n_id}", response_model=NotificationResponse)
def notification_detail(n_id: uuid.UUID, session: SessionDep):
    return _get_notification_or_404(session, n_id).to_pydantic()


@notification_router.put("/{n_id}/read", status_code=status.HTTP_204_NO_CONTENT)
def notification_read(n_id: uuid.UUID, session: SessionDep):
    notification = _get_notification_or_404(session, n_id)
    notification.is_read()
    session.commit()
