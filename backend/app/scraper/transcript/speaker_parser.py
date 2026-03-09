"""Speaker identification and statement separation for FIA press conference transcripts."""

import logging
import re

from app.models.transcript import Speaker, SpeakerRole, Statement

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 2026 reference data for speaker identification
# ---------------------------------------------------------------------------

# Team principals and their teams (2026 season, approximate)
TEAM_PRINCIPALS: dict[str, str] = {
    "Toto Wolff": "Mercedes",
    "Fred Vasseur": "Ferrari",
    "Andrea Stella": "McLaren",
    "Christian Horner": "Red Bull",
    "Oliver Oakes": "Alpine",
    "James Vowles": "Williams",
    "Laurent Mekies": "VCARB",
    "Andy Cowell": "Aston Martin",
    "Ayao Komatsu": "Haas",
    "Mattia Binotto": "Audi",
    "Graeme Lowdon": "Cadillac",
}

# Drivers and their teams (2026 season, placeholder — updated from Task 2.1)
DRIVERS: dict[str, str] = {
    "Lewis Hamilton": "Ferrari",
    "Charles Leclerc": "Ferrari",
    "Max Verstappen": "Red Bull",
    "Liam Lawson": "Red Bull",
    "Lando Norris": "McLaren",
    "Oscar Piastri": "McLaren",
    "George Russell": "Mercedes",
    "Kimi Antonelli": "Mercedes",
    "Pierre Gasly": "Alpine",
    "Jack Doohan": "Alpine",
    "Alexander Albon": "Williams",
    "Carlos Sainz": "Williams",
    "Yuki Tsunoda": "VCARB",
    "Isack Hadjar": "VCARB",
    "Fernando Alonso": "Aston Martin",
    "Lance Stroll": "Aston Martin",
    "Esteban Ocon": "Haas",
    "Oliver Bearman": "Haas",
    "Nico Hulkenberg": "Audi",
    "Gabriel Bortoleto": "Audi",
}

# Build lookup: uppercase last name -> (full_name, team, role)
_SPEAKER_LOOKUP: dict[str, tuple[str, str, SpeakerRole]] = {}

for _name, _team in TEAM_PRINCIPALS.items():
    _last = _name.rsplit(" ", maxsplit=1)[-1].upper()
    _SPEAKER_LOOKUP[_last] = (_name, _team, SpeakerRole.TEAM_PRINCIPAL)
    _SPEAKER_LOOKUP[_name.upper()] = (_name, _team, SpeakerRole.TEAM_PRINCIPAL)

for _name, _team in DRIVERS.items():
    _last = _name.rsplit(" ", maxsplit=1)[-1].upper()
    _SPEAKER_LOOKUP[_last] = (_name, _team, SpeakerRole.DRIVER)
    _SPEAKER_LOOKUP[_name.upper()] = (_name, _team, SpeakerRole.DRIVER)

# Common moderator / journalist markers
_MODERATOR_MARKERS: frozenset[str] = frozenset(
    {
        "Q",
        "Q.",
        "QUESTION",
        "MODERATOR",
    }
)

# ---------------------------------------------------------------------------
# Parsing patterns
# ---------------------------------------------------------------------------

# Pattern: Speaker name in ALL CAPS at the start of a line, optionally followed by colon
# Examples: "VERSTAPPEN:", "MAX VERSTAPPEN:", "Q.", "Q:"
_SPEAKER_LINE_PATTERN = re.compile(r"^([A-Z][A-Z\s.\-']{1,40})\s*[:.]?\s*$")

# Pattern: Inline speaker prefix — "VERSTAPPEN: Some text..." on the same line
_INLINE_SPEAKER_PATTERN = re.compile(r"^([A-Z][A-Z\s.\-']{1,40})\s*[:]\s+(.+)")

# Pattern: "Q. (Name)" format used in FIA transcripts
_QA_PATTERN = re.compile(r"^Q\.\s*(?:\(([^)]+)\))?\s*(.*)", re.IGNORECASE)


def _resolve_speaker(raw_name: str) -> Speaker:
    """Resolve a raw speaker name to a Speaker model using reference data.

    Args:
        raw_name: The raw speaker name string (may be uppercase, abbreviated, etc.)

    Returns:
        A Speaker with resolved name, role, and team if recognized.
    """
    cleaned = raw_name.strip().rstrip(":.")
    upper = cleaned.upper().strip()

    # Check for question/moderator markers
    if upper in _MODERATOR_MARKERS:
        return Speaker(name="Moderator", role=SpeakerRole.JOURNALIST)

    # Try exact match on uppercase full name or last name
    if upper in _SPEAKER_LOOKUP:
        full_name, team, role = _SPEAKER_LOOKUP[upper]
        return Speaker(name=full_name, role=role, team=team)

    # Try partial matching — check if any known last name is in the raw string
    for key, (full_name, team, role) in _SPEAKER_LOOKUP.items():
        if key in upper and len(key) > 3:
            return Speaker(name=full_name, role=role, team=team)

    # Unknown speaker — return with original name, title-cased
    display_name = cleaned.title() if cleaned.isupper() else cleaned
    return Speaker(name=display_name, role=SpeakerRole.OTHER)


def parse_statements(text: str) -> list[Statement]:
    """Parse transcript text into a list of structured statements.

    Identifies speaker changes by looking for uppercase names at the start of lines
    or inline "NAME: text" patterns. Handles Q&A format where questions are prefixed
    with "Q." and answers attributed to the named speaker.

    Args:
        text: The cleaned transcript text.

    Returns:
        A list of Statement objects with speaker attribution.
    """
    if not text.strip():
        return []

    lines = text.split("\n")
    statements: list[Statement] = []
    current_speaker: Speaker | None = None
    current_text_parts: list[str] = []
    current_question: str | None = None

    def _flush() -> None:
        """Save the accumulated text as a statement for the current speaker."""
        nonlocal current_speaker, current_text_parts, current_question
        if current_speaker and current_text_parts:
            combined = " ".join(current_text_parts).strip()
            if combined:
                statements.append(
                    Statement(
                        speaker=current_speaker,
                        text=combined,
                        question=current_question,
                    )
                )
        current_text_parts = []
        current_question = None

    for line in lines:
        stripped = line.strip()

        if not stripped:
            continue

        # Check for Q&A pattern: "Q. (journalist name) question text"
        qa_match = _QA_PATTERN.match(stripped)
        if qa_match:
            _flush()
            journalist_name = qa_match.group(1)
            question_text = qa_match.group(2).strip() if qa_match.group(2) else ""

            if journalist_name:
                current_speaker = Speaker(
                    name=journalist_name.strip(),
                    role=SpeakerRole.JOURNALIST,
                )
            else:
                current_speaker = Speaker(
                    name="Moderator",
                    role=SpeakerRole.JOURNALIST,
                )

            if question_text:
                current_text_parts = [question_text]
            continue

        # Check for standalone speaker line (ALL CAPS name on its own line)
        speaker_match = _SPEAKER_LINE_PATTERN.match(stripped)
        if speaker_match:
            candidate = speaker_match.group(1).strip()
            # Only treat as a speaker if it's a recognized name or looks like one
            # (at least 2 characters, not a common word)
            if len(candidate) >= 2 and candidate.upper() not in {"THE", "AND", "FOR", "BUT"}:
                # Save current question if previous speaker was a journalist
                prev_question = None
                if current_speaker and current_speaker.role == SpeakerRole.JOURNALIST:
                    prev_question = " ".join(current_text_parts).strip() or None

                _flush()

                current_speaker = _resolve_speaker(candidate)

                # If a journalist asked a question, carry it forward to this answer
                if prev_question and current_speaker.role != SpeakerRole.JOURNALIST:
                    current_question = prev_question
                continue

        # Check for inline speaker: "VERSTAPPEN: The car was great today..."
        inline_match = _INLINE_SPEAKER_PATTERN.match(stripped)
        if inline_match:
            candidate = inline_match.group(1).strip()
            rest = inline_match.group(2).strip()

            if len(candidate) >= 2 and candidate.upper() not in {"THE", "AND", "FOR", "BUT"}:
                prev_question = None
                if current_speaker and current_speaker.role == SpeakerRole.JOURNALIST:
                    prev_question = " ".join(current_text_parts).strip() or None

                _flush()

                current_speaker = _resolve_speaker(candidate)

                if prev_question and current_speaker.role != SpeakerRole.JOURNALIST:
                    current_question = prev_question

                current_text_parts = [rest]
                continue

        # Regular content line — append to current speaker's text
        current_text_parts.append(stripped)

    # Flush remaining text
    _flush()

    logger.info("Parsed %d statements from transcript", len(statements))
    return statements
