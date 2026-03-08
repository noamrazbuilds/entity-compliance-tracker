"""Background scheduler that checks upcoming filings and sends reminders."""

from __future__ import annotations

import logging
from datetime import date, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session

from ect_app.config import settings
from ect_app.database import SessionLocal
from ect_app.models.entity import Entity
from ect_app.models.filing import FilingDeadline
from ect_app.models.notification import NotificationLog, NotificationSetting
from ect_app.notifications.email_sender import send_reminder_email
from ect_app.notifications.slack_sender import send_slack_reminder

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler()


def _already_sent(db: Session, filing_id: int, channel: str, days_before: int) -> bool:
    """Return True if a reminder has already been logged for this combination."""
    return (
        db.query(NotificationLog)
        .filter(
            NotificationLog.filing_deadline_id == filing_id,
            NotificationLog.channel == channel,
            NotificationLog.reminder_days_before == days_before,
            NotificationLog.status == "sent",
        )
        .first()
        is not None
    )


def _log_notification(
    db: Session,
    filing_id: int,
    channel: str,
    days_before: int,
    success: bool,
    error_message: str | None = None,
) -> None:
    """Write a notification log entry."""
    log = NotificationLog(
        filing_deadline_id=filing_id,
        channel=channel,
        reminder_days_before=days_before,
        status="sent" if success else "failed",
        error_message=error_message,
    )
    db.add(log)
    db.commit()


def _get_effective_settings(db: Session, entity_id: int) -> list[NotificationSetting]:
    """Return per-entity settings if any exist; otherwise return global defaults."""
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


def _send_for_channel(
    channel: str,
    recipients: str | None,
    entity_name: str,
    filing_type: str,
    jurisdiction: str,
    due_date_str: str,
    days_until_due: int,
) -> bool:
    """Dispatch to the appropriate sender. Returns True on success."""
    if channel == "email":
        if not recipients:
            logger.warning("No email recipients configured; skipping email send")
            return False
        to_addresses = [r.strip() for r in recipients.split(",") if r.strip()]
        if not to_addresses:
            return False
        return send_reminder_email(
            to_addresses=to_addresses,
            entity_name=entity_name,
            filing_type=filing_type,
            jurisdiction=jurisdiction,
            due_date=due_date_str,
            days_until_due=days_until_due,
            smtp_host=settings.smtp_host,
            smtp_port=settings.smtp_port,
            smtp_user=settings.smtp_user,
            smtp_password=settings.smtp_password,
            from_email=settings.smtp_from_email,
        )
    elif channel == "slack":
        webhook = recipients or settings.slack_webhook_url
        if not webhook:
            logger.warning("No Slack webhook configured; skipping Slack send")
            return False
        return send_slack_reminder(
            webhook_url=webhook,
            entity_name=entity_name,
            filing_type=filing_type,
            jurisdiction=jurisdiction,
            due_date=due_date_str,
            days_until_due=days_until_due,
        )
    else:
        logger.warning("Unknown notification channel: %s", channel)
        return False


def check_and_send_reminders() -> None:
    """Check all upcoming filings and send reminders as needed."""
    db: Session = SessionLocal()
    try:
        # Determine the maximum look-ahead window from all enabled settings
        all_settings = (
            db.query(NotificationSetting)
            .filter(NotificationSetting.enabled.is_(True))
            .all()
        )
        if not all_settings:
            logger.debug("No enabled notification settings found; nothing to do")
            return

        all_days: set[int] = set()
        for ns in all_settings:
            all_days.update(ns.reminder_days_list)
        if not all_days:
            return

        max_days = max(all_days)
        today = date.today()
        window_end = today + timedelta(days=max_days)

        # Query unfiled filings within the window
        filings = (
            db.query(FilingDeadline)
            .filter(
                FilingDeadline.status != "filed",
                FilingDeadline.due_date >= today,
                FilingDeadline.due_date <= window_end,
            )
            .all()
        )

        for filing in filings:
            days_until_due = (filing.due_date - today).days
            effective_settings = _get_effective_settings(db, filing.entity_id)

            # Load entity for display fields
            entity: Entity | None = filing.entity

            for ns in effective_settings:
                if days_until_due not in ns.reminder_days_list:
                    continue

                channels: list[str] = (
                    ["email", "slack"] if ns.channel == "both" else [ns.channel]
                )

                for channel in channels:
                    if _already_sent(db, filing.id, channel, days_until_due):
                        continue

                    success = _send_for_channel(
                        channel=channel,
                        recipients=ns.recipients,
                        entity_name=entity.name if entity else "Unknown",
                        filing_type=filing.filing_type,
                        jurisdiction=filing.jurisdiction,
                        due_date_str=filing.due_date.isoformat(),
                        days_until_due=days_until_due,
                    )

                    _log_notification(
                        db,
                        filing_id=filing.id,
                        channel=channel,
                        days_before=days_until_due,
                        success=success,
                        error_message=None if success else "Send failed; see logs",
                    )

        logger.info("Reminder check completed")

    except Exception:
        logger.exception("Error during reminder check")
    finally:
        db.close()


def start_scheduler() -> None:
    """Start the background scheduler. Call from FastAPI lifespan."""
    scheduler.add_job(
        check_and_send_reminders,
        "cron",
        hour=8,
        minute=0,
        id="reminder_check",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Notification scheduler started")


def stop_scheduler() -> None:
    """Stop the background scheduler."""
    scheduler.shutdown(wait=False)
    logger.info("Notification scheduler stopped")
