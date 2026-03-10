"""Error alert delivery via Discord and Slack webhooks."""

import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

_DISCORD_COLOR_ERROR = 0xFF0000  # red
_TIMEOUT = 5.0  # seconds


async def send_alert(title: str, message: str, *, level: str = "error") -> None:
    """Send an alert to configured Discord and/or Slack webhooks.

    Silently swips on failure so alerts never crash the main app.

    Args:
        title: Short summary of the alert.
        message: Detailed description.
        level: "error" | "warning" | "info" — affects Discord embed colour.
    """
    tasks = []

    if settings.discord_webhook_url:
        tasks.append(_send_discord(title, message, level=level))

    if settings.slack_webhook_url:
        tasks.append(_send_slack(title, message, level=level))

    for coro in tasks:
        try:
            await coro
        except Exception:
            logger.exception("Failed to send alert notification")


async def _send_discord(title: str, message: str, *, level: str) -> None:
    """Post an embed message to a Discord webhook."""
    color_map = {
        "error": 0xFF0000,
        "warning": 0xFFA500,
        "info": 0x00BFFF,
    }
    payload = {
        "embeds": [
            {
                "title": title,
                "description": message[:4096],
                "color": color_map.get(level, _DISCORD_COLOR_ERROR),
            }
        ]
    }
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.post(settings.discord_webhook_url, json=payload)
        resp.raise_for_status()


async def _send_slack(title: str, message: str, *, level: str) -> None:
    """Post a block message to a Slack webhook."""
    icon_map = {
        "error": ":red_circle:",
        "warning": ":large_yellow_circle:",
        "info": ":large_blue_circle:",
    }
    icon = icon_map.get(level, ":red_circle:")
    payload = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{icon} *{title}*\n{message[:3000]}",
                },
            }
        ]
    }
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.post(settings.slack_webhook_url, json=payload)
        resp.raise_for_status()
