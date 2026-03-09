"""2026 F1 season master data — teams and drivers."""

from app.models.team import Driver, Team

# ---------------------------------------------------------------------------
# 11 Teams for 2026
# ---------------------------------------------------------------------------

_TEAMS: list[Team] = [
    Team(
        team_id="mercedes",
        name="Mercedes",
        full_name="Mercedes-AMG PETRONAS F1 Team",
        power_unit="Mercedes",
        country="Germany",
        team_principal="Toto Wolff",
        constructor_id="mercedes",
    ),
    Team(
        team_id="ferrari",
        name="Ferrari",
        full_name="Scuderia Ferrari HP",
        power_unit="Ferrari",
        country="Italy",
        team_principal="Frederic Vasseur",
        constructor_id="ferrari",
    ),
    Team(
        team_id="mclaren",
        name="McLaren",
        full_name="McLaren F1 Team",
        power_unit="Mercedes",
        country="United Kingdom",
        team_principal="Andrea Stella",
        constructor_id="mclaren",
    ),
    Team(
        team_id="red_bull",
        name="Red Bull",
        full_name="Oracle Red Bull Racing",
        power_unit="RBPT (Ford)",
        country="Austria",
        team_principal="Christian Horner",
        constructor_id="red_bull",
    ),
    Team(
        team_id="alpine",
        name="Alpine",
        full_name="BWT Alpine F1 Team",
        power_unit="Mercedes",
        country="France",
        team_principal="Oliver Oakes",
        constructor_id="alpine",
    ),
    Team(
        team_id="williams",
        name="Williams",
        full_name="Williams Racing",
        power_unit="Mercedes",
        country="United Kingdom",
        team_principal="James Vowles",
        constructor_id="williams",
    ),
    Team(
        team_id="vcarb",
        name="Racing Bulls",
        full_name="Visa Cash App Racing Bulls",
        power_unit="RBPT (Ford)",
        country="Italy",
        team_principal="Laurent Mekies",
        constructor_id="vcarb",
    ),
    Team(
        team_id="aston_martin",
        name="Aston Martin",
        full_name="Aston Martin Aramco F1 Team",
        power_unit="Honda",
        country="United Kingdom",
        team_principal="Andy Cowell",
        constructor_id="aston_martin",
    ),
    Team(
        team_id="haas",
        name="Haas",
        full_name="MoneyGram Haas F1 Team",
        power_unit="Ferrari",
        country="United States",
        team_principal="Ayao Komatsu",
        constructor_id="haas",
    ),
    Team(
        team_id="audi",
        name="Audi",
        full_name="Audi F1 Team",
        power_unit="Audi",
        country="Germany",
        team_principal="Mattia Binotto",
        constructor_id="audi",
    ),
    Team(
        team_id="cadillac",
        name="Cadillac",
        full_name="Cadillac F1 Team",
        power_unit="Ferrari",
        country="United States",
        team_principal="Graeme Lowdon",
        constructor_id="cadillac",
    ),
]

# ---------------------------------------------------------------------------
# ~22 Drivers for 2026 (expected lineup, approximate)
# ---------------------------------------------------------------------------

_DRIVERS: list[Driver] = [
    # Mercedes
    Driver(
        driver_id="russell",
        first_name="George",
        last_name="Russell",
        number=63,
        abbreviation="RUS",
        nationality="British",
        team_id="mercedes",
    ),
    Driver(
        driver_id="antonelli",
        first_name="Andrea Kimi",
        last_name="Antonelli",
        number=12,
        abbreviation="ANT",
        nationality="Italian",
        team_id="mercedes",
    ),
    # Ferrari
    Driver(
        driver_id="hamilton",
        first_name="Lewis",
        last_name="Hamilton",
        number=44,
        abbreviation="HAM",
        nationality="British",
        team_id="ferrari",
    ),
    Driver(
        driver_id="leclerc",
        first_name="Charles",
        last_name="Leclerc",
        number=16,
        abbreviation="LEC",
        nationality="Monegasque",
        team_id="ferrari",
    ),
    # McLaren
    Driver(
        driver_id="norris",
        first_name="Lando",
        last_name="Norris",
        number=4,
        abbreviation="NOR",
        nationality="British",
        team_id="mclaren",
    ),
    Driver(
        driver_id="piastri",
        first_name="Oscar",
        last_name="Piastri",
        number=81,
        abbreviation="PIA",
        nationality="Australian",
        team_id="mclaren",
    ),
    # Red Bull
    Driver(
        driver_id="verstappen",
        first_name="Max",
        last_name="Verstappen",
        number=1,
        abbreviation="VER",
        nationality="Dutch",
        team_id="red_bull",
    ),
    Driver(
        driver_id="lawson",
        first_name="Liam",
        last_name="Lawson",
        number=30,
        abbreviation="LAW",
        nationality="New Zealander",
        team_id="red_bull",
    ),
    # Alpine
    Driver(
        driver_id="gasly",
        first_name="Pierre",
        last_name="Gasly",
        number=10,
        abbreviation="GAS",
        nationality="French",
        team_id="alpine",
    ),
    Driver(
        driver_id="doohan",
        first_name="Jack",
        last_name="Doohan",
        number=7,
        abbreviation="DOO",
        nationality="Australian",
        team_id="alpine",
    ),
    # Williams
    Driver(
        driver_id="sainz",
        first_name="Carlos",
        last_name="Sainz",
        number=55,
        abbreviation="SAI",
        nationality="Spanish",
        team_id="williams",
    ),
    Driver(
        driver_id="albon",
        first_name="Alexander",
        last_name="Albon",
        number=23,
        abbreviation="ALB",
        nationality="Thai",
        team_id="williams",
    ),
    # Racing Bulls (VCARB)
    Driver(
        driver_id="tsunoda",
        first_name="Yuki",
        last_name="Tsunoda",
        number=22,
        abbreviation="TSU",
        nationality="Japanese",
        team_id="vcarb",
    ),
    Driver(
        driver_id="hadjar",
        first_name="Isack",
        last_name="Hadjar",
        number=6,
        abbreviation="HAD",
        nationality="French",
        team_id="vcarb",
    ),
    # Aston Martin
    Driver(
        driver_id="alonso",
        first_name="Fernando",
        last_name="Alonso",
        number=14,
        abbreviation="ALO",
        nationality="Spanish",
        team_id="aston_martin",
    ),
    Driver(
        driver_id="stroll",
        first_name="Lance",
        last_name="Stroll",
        number=18,
        abbreviation="STR",
        nationality="Canadian",
        team_id="aston_martin",
    ),
    # Haas
    Driver(
        driver_id="ocon",
        first_name="Esteban",
        last_name="Ocon",
        number=31,
        abbreviation="OCO",
        nationality="French",
        team_id="haas",
    ),
    Driver(
        driver_id="bearman",
        first_name="Oliver",
        last_name="Bearman",
        number=87,
        abbreviation="BEA",
        nationality="British",
        team_id="haas",
    ),
    # Audi
    Driver(
        driver_id="hulkenberg",
        first_name="Nico",
        last_name="Hulkenberg",
        number=27,
        abbreviation="HUL",
        nationality="German",
        team_id="audi",
    ),
    Driver(
        driver_id="bortoleto",
        first_name="Gabriel",
        last_name="Bortoleto",
        number=5,
        abbreviation="BOR",
        nationality="Brazilian",
        team_id="audi",
    ),
    # Cadillac
    Driver(
        driver_id="drugovich",
        first_name="Felipe",
        last_name="Drugovich",
        number=21,
        abbreviation="DRU",
        nationality="Brazilian",
        team_id="cadillac",
    ),
    Driver(
        driver_id="pourchaire",
        first_name="Theo",
        last_name="Pourchaire",
        number=20,
        abbreviation="POU",
        nationality="French",
        team_id="cadillac",
    ),
]


def get_teams() -> list[Team]:
    """Return the list of all 2026 F1 teams."""
    return list(_TEAMS)


def get_drivers() -> list[Driver]:
    """Return the list of all 2026 F1 drivers."""
    return list(_DRIVERS)
