"""Transcript service orchestrating PDF download, text extraction, and speaker parsing."""

import logging
from datetime import datetime
from pathlib import Path

from app.models.transcript import SessionType, Transcript
from app.scraper.http_client import ScraperHttpClient
from app.scraper.transcript.pdf_downloader import download_pdf
from app.scraper.transcript.pdf_parser import extract_text_from_pdf
from app.scraper.transcript.speaker_parser import parse_statements

logger = logging.getLogger(__name__)

# Map common session type keywords to SessionType enum
_SESSION_TYPE_KEYWORDS: dict[str, SessionType] = {
    "drivers": SessionType.DRIVERS,
    "team principals": SessionType.TEAM_PRINCIPALS,
    "post qualifying": SessionType.POST_QUALIFYING,
    "post-qualifying": SessionType.POST_QUALIFYING,
    "post race": SessionType.POST_RACE,
    "post-race": SessionType.POST_RACE,
    "post sprint": SessionType.POST_SPRINT,
    "post-sprint": SessionType.POST_SPRINT,
}


def _detect_session_type(text: str, filename: str) -> SessionType:
    """Detect the session type from the transcript text or filename.

    Args:
        text: The extracted transcript text.
        filename: The PDF filename.

    Returns:
        The detected SessionType, or OTHER if unrecognized.
    """
    search_text = f"{filename} {text[:500]}".lower()

    for keyword, session_type in _SESSION_TYPE_KEYWORDS.items():
        if keyword in search_text:
            return session_type

    return SessionType.OTHER


class TranscriptService:
    """Orchestrates the full transcript processing pipeline.

    Pipeline: download PDF -> extract text -> parse speakers -> build Transcript
    """

    def __init__(
        self,
        *,
        http_client: ScraperHttpClient | None = None,
        download_dir: str | None = None,
    ) -> None:
        """Initialize the transcript service.

        Args:
            http_client: HTTP client for downloading PDFs. Created if not provided.
            download_dir: Directory for downloaded PDFs. Uses settings default if not provided.
        """
        self._http_client = http_client or ScraperHttpClient()
        self._owns_client = http_client is None
        self._download_dir = download_dir

    async def process_pdf_url(
        self,
        url: str,
        *,
        gp_name: str,
        session_type: SessionType | None = None,
        date: datetime | None = None,
    ) -> Transcript:
        """Download a PDF from a URL and parse it into a Transcript.

        Args:
            url: URL of the PDF to download.
            gp_name: Name of the Grand Prix (e.g. "Bahrain Grand Prix").
            session_type: Optional session type override. Auto-detected if not provided.
            date: Optional date of the press conference.

        Returns:
            A fully parsed Transcript object.

        Raises:
            httpx.HTTPError: If the PDF download fails.
            FileNotFoundError: If the downloaded file cannot be found.
        """
        logger.info("Processing transcript PDF from %s for %s", url, gp_name)

        # Step 1: Download the PDF
        pdf_path = await download_pdf(
            url,
            http_client=self._http_client,
            download_dir=self._download_dir,
        )

        # Step 2: Extract text and parse
        return self.process_local_pdf(
            pdf_path,
            gp_name=gp_name,
            source_url=url,
            session_type=session_type,
            date=date,
        )

    def process_local_pdf(
        self,
        pdf_path: Path,
        *,
        gp_name: str,
        source_url: str = "",
        session_type: SessionType | None = None,
        date: datetime | None = None,
    ) -> Transcript:
        """Parse a local PDF file into a Transcript.

        Args:
            pdf_path: Path to the local PDF file.
            gp_name: Name of the Grand Prix.
            source_url: Original URL the PDF was downloaded from.
            session_type: Optional session type override. Auto-detected if not provided.
            date: Optional date of the press conference.

        Returns:
            A fully parsed Transcript object.

        Raises:
            FileNotFoundError: If the PDF file does not exist.
        """
        logger.info("Parsing local PDF: %s", pdf_path)

        # Step 1: Extract text from PDF
        raw_text = extract_text_from_pdf(pdf_path)

        if not raw_text:
            logger.warning("No text extracted from PDF: %s", pdf_path)
            return Transcript(
                gp_name=gp_name,
                session_type=session_type or SessionType.OTHER,
                date=date,
                statements=[],
                source_url=source_url,
                pdf_filename=pdf_path.name,
                raw_text="",
            )

        # Step 2: Detect session type if not provided
        detected_type = session_type or _detect_session_type(raw_text, pdf_path.name)

        # Step 3: Parse speaker statements
        statements = parse_statements(raw_text)

        logger.info(
            "Transcript parsed: %s — %s, %d statements",
            gp_name,
            detected_type.value,
            len(statements),
        )

        return Transcript(
            gp_name=gp_name,
            session_type=detected_type,
            date=date,
            statements=statements,
            source_url=source_url,
            pdf_filename=pdf_path.name,
            raw_text=raw_text,
        )

    async def close(self) -> None:
        """Release resources owned by this service."""
        if self._owns_client:
            await self._http_client.close()
