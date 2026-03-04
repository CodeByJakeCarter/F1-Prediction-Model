from __future__ import annotations

from dataclasses import dataclass
from itertools import count


@dataclass(frozen=True)
class Driver:
    driver_id: int
    code: str
    name: str


@dataclass(frozen=True)
class Constructor:
    constructor_id: int
    name: str


@dataclass(frozen=True)
class Season:
    season: int


@dataclass(frozen=True)
class Race:
    race_id: int
    season: int
    round_number: int
    name: str


@dataclass(frozen=True)
class Result:
    race_id: int
    driver_id: int
    constructor_id: int
    position: int
    points: float


class EntityFactory:
    def __init__(self) -> None:
        self._driver_ids = count(1)
        self._constructor_ids = count(1)
        self._race_ids = count(1)

    def make_driver(self, code: str = "VER", name: str = "Max Verstappen") -> Driver:
        return Driver(driver_id=next(self._driver_ids), code=code, name=name)

    def make_constructor(self, name: str = "Red Bull") -> Constructor:
        return Constructor(constructor_id=next(self._constructor_ids), name=name)

    def make_season(self, season: int = 2024) -> Season:
        return Season(season=season)

    def make_race(self, season: int, round_number: int = 1, name: str = "Bahrain GP") -> Race:
        return Race(
            race_id=next(self._race_ids),
            season=season,
            round_number=round_number,
            name=name,
        )

    def make_result(
        self,
        race_id: int,
        driver_id: int,
        constructor_id: int,
        position: int = 1,
        points: float = 25.0,
    ) -> Result:
        return Result(
            race_id=race_id,
            driver_id=driver_id,
            constructor_id=constructor_id,
            position=position,
            points=points,
        )
