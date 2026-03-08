"""Slack notification sender via incoming webhooks."""

from __future__ import annotations

import logging

import requests

logger = logging.getLogger(__name__)


def _urgency_emoji(days_until_due: int) -> str:
    """Return an emoji reflecting urgency based on days remaining."""
    if days_until_due <= 3:
        return "\U0001f6a8"  # rotating light
    if days_until_due <= 7:
        return "\u26a0\ufe0f"  # warning
    if days_until_due <= 14:
        return "\U0001f7e1"  # yellow circle
    return "\u2705"  # check mark


def send_slack_reminder(
    webhook_url: str,
    entity_name: str,
    filing_type: str,
    jurisdiction: str,
    due_date: str,
    days_until_due: int,
) -> bool:
    """Send a filing reminder to Slack via webhook. Returns True on success."""
    try:
        urgency = _urgency_emoji(days_until_due)

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "\U0001f4cb Filing Deadline Reminder",
                    "emoji": True,
                },
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Entity:*\n{entity_name}"},
                    {"type": "mrkdwn", "text": f"*Filing Type:*\n{filing_type}"},
                    {"type": "mrkdwn", "text": f"*Jurisdiction:*\n{jurisdiction}"},
                ],
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Due Date:*\n{due_date}"},
                    {
                        "type": "mrkdwn",
                        "text": f"*Days Remaining:*\n{urgency} {days_until_due} day(s)",
                    },
                ],
            },
            {"type": "divider"},
        ]

        payload = {"blocks": blocks}

        resp = requests.post(webhook_url, json=payload, timeout=15)
        resp.raise_for_status()

        logger.info(
            "Slack reminder sent for %s (%s)", entity_name, filing_type
        )
        return True

    except Exception:
        logger.exception(
            "Failed to send Slack reminder for %s (%s)", entity_name, filing_type
        )
        return False
