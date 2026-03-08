"""CRUD and helper methods for notification settings and logs."""

from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from ect_app.config import settings
from ect_app.models.notification import NotificationLog, NotificationSetting
from ect_app.notifications.email_sender import send_reminder_email
from ect_app.notifications.slack_sender import send_slack_reminder
from ect_app.schemas.notification import (
    NotificationSettingCreate,
    NotificationSettingUpdate,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# NotificationSetting CRUD
# ---------------------------------------------------------------------------


def list_settings(db: Session) -> list[NotificationSetting]:
    """Return all notification settings, ordered by id."""
    return db.query(NotificationSetting).order_by(NotificationSetting.id).all()


def get_settings(db: Session, setting_id: int) -> NotificationSetting | None:
    """Return a single notification setting by id."""
    return (
        db.query(NotificationSetting)
        .filter(NotificationSetting.id == setting_id)
        .first()
    )


def create_setting(
    db: Session, data: NotificationSettingCreate
) -> NotificationSetting:
    """Create a new notification setting."""
    setting = NotificationSetting(**data.model_dump())
    db.add(setting)
    db.commit()
    db.refresh(setting)
    return setting


def update_setting(
    db: Session, setting_id: int, data: NotificationSettingUpdate
) -> NotificationSetting | None:
    """Update an existing notification setting. Returns None if not found."""
    setting = get_settings(db, setting_id)
    if not setting:
        return None
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(setting, key, value)
    db.commit()
    db.refresh(setting)
    return setting


def delete_setting(db: Session, setting_id: int) -> bool:
    """Delete a notification setting. Returns True if deleted, False if not found."""
    setting = get_settings(db, setting_id)
    if not setting:
        return False
    db.delete(setting)
    db.commit()
    return True


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def get_effective_settings(
    db: Session, entity_id: int
) -> list[NotificationSetting]:
    """Return per-entity settings if they exist, otherwise global defaults."""
    entity_settings = (
        db.query(NotificationSetting)
        .filter(
            NotificationSetting.entity_id == entity_id,
            NotificationSetting.enabled.is_(True),
        )
        .all()
    )
    if entity_settings:
        return entity_settings

    return (
        db.query(NotificationSetting)
        .filter(
            NotificationSetting.entity_id.is_(None),
            NotificationSetting.enabled.is_(True),
        )
        .all()
    )


def get_notification_log(
    db: Session, limit: int = 50
) -> list[NotificationLog]:
    """Return recent notification log entries, newest first."""
    return (
        db.query(NotificationLog)
        .order_by(NotificationLog.sent_at.desc())
        .limit(limit)
        .all()
    )


def send_test_notification(
    db: Session, channel: str, recipient: str
) -> bool:
    """Send a test notification to validate configuration. Returns True on success."""
    entity_name = "Test Entity"
    filing_type = "Annual Report"
    jurisdiction = "Delaware"
    due_date = "2099-12-31"
    days_until_due = 14

    if channel == "email":
        return send_reminder_email(
            to_addresses=[recipient],
            entity_name=entity_name,
            filing_type=filing_type,
            jurisdiction=jurisdiction,
            due_date=due_date,
            days_until_due=days_until_due,
            smtp_host=settings.smtp_host,
            smtp_port=settings.smtp_port,
            smtp_user=settings.smtp_user,
            smtp_password=settings.smtp_password,
            from_email=settings.smtp_from_email,
        )
    elif channel == "slack":
        return send_slack_reminder(
            webhook_url=recipient,
            entity_name=entity_name,
            filing_type=filing_type,
            jurisdiction=jurisdiction,
            due_date=due_date,
            days_until_due=days_until_due,
        )
    else:
        logger.warning("Unknown channel for test notification: %s", channel)
        return False
