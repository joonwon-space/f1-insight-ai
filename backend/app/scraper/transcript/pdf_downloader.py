"""PDF download module for FIA press conference transcripts."""

import logging
from pathlib import Path

from app.core.config import settings
from app.scraper.http_client import ScraperHttpClient

logger = logging.getLogger(__name__)


def _ensure_download_dir(download_dir: str) -> Path:
    """Ensure the download directory exists and return it as a Path."""
    path = Path(download_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _filename_from_url(url: str) -> str:
    """Extract a safe filename from a URL.

    Falls back to a hash-based name if no meaningful filename can be extracted.
    """
    # Take the last path segment
    segment = url.rstrip("/").rsplit("/", maxsplit=1)[-1]

    # Strip query parameters
    if "?" in segment:
        segment = segment.split("?", maxsplit=1)[0]

    # Ensure it has a .pdf extension
    if not segment.lower().endswith(".pdf"):
        segment = f"{segment}.pdf"

    # Remove any characters that are unsafe for filenames
    safe_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-")
    sanitized = "".join(c if c in safe_chars else "_" for c in segment)

    return sanitized or "transcript.pdf"


async def download_pdf(
    url: str,
    *,
    http_client: ScraperHttpClient,
    download_dir: str | None = None,
) -> Path:
    """Download a PDF from the given URL and save it to the download directory.

    Args:
        url: The URL of the PDF to download.
        http_client: The HTTP client to use for the download.
        download_dir: Optional directory to save the PDF. Defaults to settings value.

    Returns:
        Path to the downloaded PDF file.

    Raises:
        httpx.HTTPError: If the download fails after retries.
        OSError: If writing the file fails.
    """
    target_dir = _ensure_download_dir(download_dir or settings.transcript_download_dir)
    filename = _filename_from_url(url)
    filepath = target_dir / filename

    # Check if already downloaded
    if filepath.exists() and filepath.stat().st_size > 0:
        logger.info("PDF already exists at %s, skipping download", filepath)
        return filepath

    logger.info("Downloading PDF from %s", url)

    # Use the scraper HTTP client's fetch which returns text,
    # but for binary content we need raw bytes via httpx directly.
    client = await http_client._ensure_client()
    await http_client._throttle()

    from app.scraper.http_client import _random_user_agent

    response = await client.get(url, headers={"User-Agent": _random_user_agent()})
    response.raise_for_status()

    filepath.write_bytes(response.content)
    logger.info("PDF saved to %s (%d bytes)", filepath, len(response.content))

    return filepath
