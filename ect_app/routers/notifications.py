"""API endpoints for notification settings and logs."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ect_app.database import get_db
from ect_app.schemas.notification import (
    NotificationLogRead,
    NotificationSettingCreate,
    NotificationSettingRead,
    NotificationSettingUpdate,
    TestNotificationRequest,
)
from ect_app.services import notification_service

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("/settings", response_model=list[NotificationSettingRead])
def list_settings(db: Session = Depends(get_db)) -> list[NotificationSettingRead]:
    return notification_service.list_settings(db)


@router.post("/settings", response_model=NotificationSettingRead, status_code=201)
def create_setting(
    data: NotificationSettingCreate, db: Session = Depends(get_db)
) -> NotificationSettingRead:
    return notification_service.create_setting(db, data)


@router.put("/settings/{setting_id}", response_model=NotificationSettingRead)
def update_setting(
    setting_id: int,
    data: NotificationSettingUpdate,
    db: Session = Depends(get_db),
) -> NotificationSettingRead:
    setting = notification_service.update_setting(db, setting_id, data)
    if not setting:
        raise HTTPException(status_code=404, detail="Notification setting not found")
    return setting


@router.delete("/settings/{setting_id}", status_code=204)
def delete_setting(setting_id: int, db: Session = Depends(get_db)) -> None:
    if not notification_service.delete_setting(db, setting_id):
        raise HTTPException(status_code=404, detail="Notification setting not found")


@router.get("/log", response_model=list[NotificationLogRead])
def get_notification_log(
    limit: int = 50, db: Session = Depends(get_db)
) -> list[NotificationLogRead]:
    return notification_service.get_notification_log(db, limit=limit)


@router.post("/test")
def send_test_notification(
    data: TestNotificationRequest, db: Session = Depends(get_db)
) -> dict[str, bool | str]:
    success = notification_service.send_test_notification(
        db, channel=data.channel, recipient=data.recipient
    )
    if success:
        return {"success": True, "message": "Test notification sent successfully"}
    return {"success": False, "message": "Failed to send test notification; check server logs"}
