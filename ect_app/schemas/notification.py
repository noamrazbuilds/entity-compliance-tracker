from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificationSettingCreate(BaseModel):
    entity_id: int | None = None
    channel: str  # email, slack
    reminder_days_before: str = "30,14,7"
    enabled: bool = True
    recipients: str | None = None


class NotificationSettingUpdate(BaseModel):
    channel: str | None = None
    reminder_days_before: str | None = None
    enabled: bool | None = None
    recipients: str | None = None


class NotificationSettingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    entity_id: int | None = None
    channel: str
    reminder_days_before: str
    enabled: bool
    recipients: str | None = None
    created_at: datetime


class NotificationLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filing_deadline_id: int
    channel: str
    reminder_days_before: int
    sent_at: datetime
    status: str
    error_message: str | None = None


class TestNotificationRequest(BaseModel):
    channel: str  # email, slack
    recipient: str
