"""F1 terminology glossary for English-to-Korean translation consistency."""

from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# Team names
# ---------------------------------------------------------------------------

TEAM_GLOSSARY: dict[str, str] = {
    "Mercedes": "메르세데스",
    "Ferrari": "페라리",
    "McLaren": "맥라렌",
    "Red Bull": "레드불",
    "Red Bull Racing": "레드불 레이싱",
    "Aston Martin": "애스턴 마틴",
    "Alpine": "알파인",
    "Williams": "윌리엄스",
    "Haas": "하스",
    "RB": "RB",
    "Kick Sauber": "킥 자우버",
    "Sauber": "자우버",
}

# ---------------------------------------------------------------------------
# Technical terms
# ---------------------------------------------------------------------------

TECHNICAL_GLOSSARY: dict[str, str] = {
    "DRS": "DRS",
    "ERS": "ERS",
    "pit stop": "피트 스톱",
    "pit lane": "피트 레인",
    "qualifying": "예선",
    "pole position": "폴 포지션",
    "podium": "포디움",
    "grid": "그리드",
    "safety car": "세이프티카",
    "virtual safety car": "버추얼 세이프티카",
    "red flag": "레드 플래그",
    "yellow flag": "옐로 플래그",
    "blue flag": "블루 플래그",
    "checkered flag": "체커드 플래그",
    "front wing": "프론트 윙",
    "rear wing": "리어 윙",
    "sidepod": "사이드포드",
    "diffuser": "디퓨저",
    "downforce": "다운포스",
    "drag": "드래그",
    "undercut": "언더컷",
    "overcut": "오버컷",
    "tire degradation": "타이어 열화",
    "soft tire": "소프트 타이어",
    "medium tire": "미디엄 타이어",
    "hard tire": "하드 타이어",
    "intermediate tire": "인터미디어트 타이어",
    "wet tire": "웨트 타이어",
    "championship": "챔피언십",
    "constructor": "컨스트럭터",
    "Grand Prix": "그랑프리",
    "sprint race": "스프린트 레이스",
    "sprint": "스프린트",
    "parc fermé": "파르크 페르메",
    "power unit": "파워 유닛",
    "team principal": "팀 대표",
    "race director": "레이스 디렉터",
    "steward": "스튜어드",
    "penalty": "페널티",
    "time penalty": "타임 페널티",
    "grid penalty": "그리드 페널티",
    "fastest lap": "패스티스트 랩",
    "lap time": "랩 타임",
    "sector": "섹터",
    "apex": "에이펙스",
    "overtake": "오버테이크",
    "slipstream": "슬립스트림",
    "tow": "토우",
    "halo": "할로",
    "cockpit": "콕핏",
    "monocoque": "모노코크",
    "ground effect": "그라운드 이펙트",
    "porpoising": "포포이징",
    "aero": "에어로",
    "wind tunnel": "풍동",
    "simulator": "시뮬레이터",
    "setup": "셋업",
    "ride height": "라이드 하이트",
    "suspension": "서스펜션",
}

# ---------------------------------------------------------------------------
# Session types
# ---------------------------------------------------------------------------

SESSION_GLOSSARY: dict[str, str] = {
    "FP1": "1차 자유연습",
    "FP2": "2차 자유연습",
    "FP3": "3차 자유연습",
    "Free Practice 1": "1차 자유연습",
    "Free Practice 2": "2차 자유연습",
    "Free Practice 3": "3차 자유연습",
    "Q1": "Q1",
    "Q2": "Q2",
    "Q3": "Q3",
    "Race": "결승",
    "Sprint Qualifying": "스프린트 예선",
    "Sprint Shootout": "스프린트 슛아웃",
}

# ---------------------------------------------------------------------------
# Combined glossary (longest keys first for greedy matching)
# ---------------------------------------------------------------------------

FULL_GLOSSARY: dict[str, str] = {
    **SESSION_GLOSSARY,
    **TECHNICAL_GLOSSARY,
    **TEAM_GLOSSARY,
}

# Pre-compile a regex for glossary-based post-processing.
# Sort by key length descending so longer terms match before shorter substrings
# (e.g., "Red Bull Racing" before "Red Bull").
_SORTED_KEYS = sorted(FULL_GLOSSARY.keys(), key=len, reverse=True)
_GLOSSARY_PATTERN = re.compile(
    "|".join(re.escape(k) for k in _SORTED_KEYS),
    flags=re.IGNORECASE,
)


def apply_glossary(text: str) -> str:
    """Post-process a Korean translation to enforce glossary-consistent terminology.

    Replaces any English F1 terms that survived translation with their canonical
    Korean equivalents. Terms already translated correctly are unaffected because
    the regex only matches English originals.
    """

    def _replace(match: re.Match[str]) -> str:
        matched = match.group(0)
        # Try exact case first, then case-insensitive lookup
        if matched in FULL_GLOSSARY:
            return FULL_GLOSSARY[matched]
        for key, value in FULL_GLOSSARY.items():
            if key.lower() == matched.lower():
                return value
        return matched  # pragma: no cover — defensive fallback

    return _GLOSSARY_PATTERN.sub(_replace, text)


def get_glossary_reference() -> str:
    """Return a formatted glossary string for inclusion in LLM prompts.

    Provides a compact reference of key F1 terms and their Korean equivalents.
    """
    lines: list[str] = []
    # Select the most important terms to include in the prompt
    important_terms = {
        **TEAM_GLOSSARY,
        **SESSION_GLOSSARY,
        # Only the most common technical terms to keep the prompt concise
        "pit stop": "피트 스톱",
        "qualifying": "예선",
        "pole position": "폴 포지션",
        "podium": "포디움",
        "safety car": "세이프티카",
        "Grand Prix": "그랑프리",
        "championship": "챔피언십",
        "constructor": "컨스트럭터",
        "sprint race": "스프린트 레이스",
        "fastest lap": "패스티스트 랩",
        "grid": "그리드",
        "team principal": "팀 대표",
        "DRS": "DRS",
        "ERS": "ERS",
    }
    for eng, kor in sorted(important_terms.items()):
        lines.append(f"  {eng} → {kor}")
    return "\n".join(lines)
