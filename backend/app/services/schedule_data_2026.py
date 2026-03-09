"""Hardcoded fallback schedule data for the 2026 F1 season.

Used when FastF1 cannot provide the calendar (e.g., future season).
Dates are approximate and based on the expected 24-race calendar.
Sprint weekends are marked with is_sprint=True.
"""

from datetime import datetime, timezone

# (round, event_name, country, circuit, fri_date, is_sprint)
# fri_date is the Friday of each race weekend (YYYY, M, D).
# Session times are generated from this anchor date in schedule.py.
SEASON_2026: list[tuple[int, str, str, str, tuple[int, int, int], bool]] = [
    (1, "Bahrain Grand Prix", "Bahrain", "Bahrain International Circuit", (2026, 3, 6), False),
    (
        2,
        "Saudi Arabian Grand Prix",
        "Saudi Arabia",
        "Jeddah Corniche Circuit",
        (2026, 3, 13),
        False,
    ),
    (3, "Australian Grand Prix", "Australia", "Albert Park Circuit", (2026, 3, 27), False),
    (4, "Japanese Grand Prix", "Japan", "Suzuka International Racing Course", (2026, 4, 3), True),
    (5, "Chinese Grand Prix", "China", "Shanghai International Circuit", (2026, 4, 17), True),
    (6, "Miami Grand Prix", "United States", "Miami International Autodrome", (2026, 5, 1), True),
    (
        7,
        "Emilia Romagna Grand Prix",
        "Italy",
        "Autodromo Enzo e Dino Ferrari",
        (2026, 5, 15),
        False,
    ),
    (8, "Monaco Grand Prix", "Monaco", "Circuit de Monaco", (2026, 5, 22), False),
    (9, "Spanish Grand Prix", "Spain", "Circuit de Barcelona-Catalunya", (2026, 5, 29), False),
    (10, "Canadian Grand Prix", "Canada", "Circuit Gilles Villeneuve", (2026, 6, 12), False),
    (11, "Austrian Grand Prix", "Austria", "Red Bull Ring", (2026, 6, 26), True),
    (12, "British Grand Prix", "United Kingdom", "Silverstone Circuit", (2026, 7, 3), False),
    (13, "Belgian Grand Prix", "Belgium", "Circuit de Spa-Francorchamps", (2026, 7, 24), False),
    (14, "Hungarian Grand Prix", "Hungary", "Hungaroring", (2026, 7, 31), False),
    (15, "Dutch Grand Prix", "Netherlands", "Circuit Zandvoort", (2026, 8, 28), False),
    (16, "Italian Grand Prix", "Italy", "Autodromo Nazionale Monza", (2026, 9, 4), False),
    (17, "Azerbaijan Grand Prix", "Azerbaijan", "Baku City Circuit", (2026, 9, 18), False),
    (18, "Singapore Grand Prix", "Singapore", "Marina Bay Street Circuit", (2026, 10, 2), False),
    (
        19,
        "United States Grand Prix",
        "United States",
        "Circuit of the Americas",
        (2026, 10, 16),
        True,
    ),
    (20, "Mexico City Grand Prix", "Mexico", "Autodromo Hermanos Rodriguez", (2026, 10, 23), False),
    (21, "Brazilian Grand Prix", "Brazil", "Autodromo Jose Carlos Pace", (2026, 10, 30), True),
    (22, "Las Vegas Grand Prix", "United States", "Las Vegas Strip Circuit", (2026, 11, 20), False),
    (23, "Qatar Grand Prix", "Qatar", "Lusail International Circuit", (2026, 11, 27), False),
    (
        24,
        "Abu Dhabi Grand Prix",
        "United Arab Emirates",
        "Yas Marina Circuit",
        (2026, 12, 4),
        False,
    ),
]


def get_fallback_friday(year: int, month: int, day: int) -> datetime:
    """Return a timezone-aware datetime for the Friday start of a weekend."""
    return datetime(year, month, day, tzinfo=timezone.utc)
