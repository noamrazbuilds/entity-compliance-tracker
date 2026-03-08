"""Email notification sender using aiosmtplib and Jinja2 templates."""

from __future__ import annotations

import asyncio
import logging
from email.message import EmailMessage
from pathlib import Path

from aiosmtplib import send as aiosmtp_send
from jinja2 import Environment, FileSystemLoader, select_autoescape

logger = logging.getLogger(__name__)

TEMPLATE_DIR = Path(__file__).parent / "templates"
jinja_env = Environment(
    loader=FileSystemLoader(str(TEMPLATE_DIR)),
    autoescape=select_autoescape(["html"]),
)


def send_reminder_email(
    to_addresses: list[str],
    entity_name: str,
    filing_type: str,
    jurisdiction: str,
    due_date: str,
    days_until_due: int,
    smtp_host: str,
    smtp_port: int,
    smtp_user: str,
    smtp_password: str,
    from_email: str,
) -> bool:
    """Send a filing reminder email. Returns True on success, False on failure."""
    try:
        template = jinja_env.get_template("reminder_email.html")
        html_body = template.render(
            entity_name=entity_name,
            filing_type=filing_type,
            jurisdiction=jurisdiction,
            due_date=due_date,
            days_until_due=days_until_due,
        )

        msg = EmailMessage()
        msg["Subject"] = (
            f"Filing Reminder: {filing_type} for {entity_name} "
            f"- Due in {days_until_due} day(s)"
        )
        msg["From"] = from_email
        msg["To"] = ", ".join(to_addresses)
        msg.set_content(
            f"Filing reminder: {filing_type} for {entity_name} in "
            f"{jurisdiction} is due on {due_date} ({days_until_due} days remaining)."
        )
        msg.add_alternative(html_body, subtype="html")

        loop: asyncio.AbstractEventLoop | None = None
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        async def _send() -> None:
            await aiosmtp_send(
                msg,
                hostname=smtp_host,
                port=smtp_port,
                username=smtp_user,
                password=smtp_password,
                start_tls=True,
            )

        if loop and loop.is_running():
            # Schedule coroutine from within a running loop (e.g. FastAPI)
            future = asyncio.run_coroutine_threadsafe(_send(), loop)
            future.result(timeout=30)
        else:
            asyncio.run(_send())

        logger.info(
            "Reminder email sent to %s for %s (%s)",
            to_addresses,
            entity_name,
            filing_type,
        )
        return True

    except Exception:
        logger.exception(
            "Failed to send reminder email for %s (%s)", entity_name, filing_type
        )
        return False
