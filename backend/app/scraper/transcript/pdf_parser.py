"""PDF to text extraction using pdfplumber."""

import logging
import re
from pathlib import Path

import pdfplumber

logger = logging.getLogger(__name__)

# Patterns for common PDF artifacts to remove
_PAGE_NUMBER_PATTERN = re.compile(r"^\s*(?:Page\s+)?\d+\s*(?:of\s+\d+)?\s*$", re.IGNORECASE)
_HEADER_PATTERN = re.compile(
    r"^\s*(?:FIA\s+)?(?:FORMULA\s+(?:ONE|1)|F1)\s+.*(?:PRESS\s+CONFERENCE|MEDIA)\s*$",
    re.IGNORECASE,
)
_FOOTER_PATTERN = re.compile(
    r"^\s*(?:www\.fia\.com|fia\.com|fiaregulations\.com)\s*$",
    re.IGNORECASE,
)
_EXCESSIVE_WHITESPACE = re.compile(r"\n{3,}")
_TRAILING_SPACES = re.compile(r"[ \t]+$", re.MULTILINE)


def _is_artifact_line(line: str) -> bool:
    """Check whether a line is a common PDF artifact (header, footer, page number)."""
    stripped = line.strip()
    if not stripped:
        return False
    if _PAGE_NUMBER_PATTERN.match(stripped):
        return True
    if _HEADER_PATTERN.match(stripped):
        return True
    if _FOOTER_PATTERN.match(stripped):
        return True
    return False


def _clean_text(raw_text: str) -> str:
    """Clean up extracted PDF text by removing artifacts and normalizing whitespace."""
    lines = raw_text.split("\n")
    cleaned_lines = [line for line in lines if not _is_artifact_line(line)]
    result = "\n".join(cleaned_lines)

    # Normalize whitespace
    result = _TRAILING_SPACES.sub("", result)
    result = _EXCESSIVE_WHITESPACE.sub("\n\n", result)
    return result.strip()


def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extract and clean text from a PDF file.

    Uses pdfplumber to extract text from all pages, then cleans up
    common PDF artifacts like page numbers, headers, and footers.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        Cleaned text content extracted from the PDF.

    Raises:
        FileNotFoundError: If the PDF file does not exist.
        pdfplumber.exceptions.PDFSyntaxError: If the file is not a valid PDF.
    """
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    logger.info("Extracting text from PDF: %s", pdf_path)

    pages_text: list[str] = []

    with pdfplumber.open(pdf_path) as pdf:
        logger.info("PDF has %d pages", len(pdf.pages))

        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                pages_text.append(text)
            else:
                logger.debug("Page %d yielded no text", i + 1)

    if not pages_text:
        logger.warning("No text extracted from PDF: %s", pdf_path)
        return ""

    raw_text = "\n\n".join(pages_text)
    cleaned = _clean_text(raw_text)

    logger.info(
        "Extracted %d characters from %d pages (cleaned to %d characters)",
        len(raw_text),
        len(pages_text),
        len(cleaned),
    )

    return cleaned
