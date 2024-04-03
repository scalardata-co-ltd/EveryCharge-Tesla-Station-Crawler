from dataclasses import dataclass
from enum import Enum, auto
from typing import List


class ChargerType(Enum):
    SUPERCHARGER = auto()
    DESTINATION = auto()


@dataclass
class Coordinate:
    latitude: float
    longitude: float


@dataclass
class Address:
    road_name_address: str
    lot_number_address: str


@dataclass
class Charger:
    charging_speed: float  # kW단위
    charger_count: int


@dataclass
class Station:
    coordinate: Coordinate
    name: str
    charger_type: ChargerType
    chargers: List[Charger]
    is_always: bool
    # address: Address

    def __str__(self) -> str:
        return (
            "===============\n"
            + f"충전소 이름: {self.name}\n"
            + f"충전기 타입: {self.charger_type}\n"
            + f"좌표: {self.coordinate}\n"
            + f"충전기 정보: {self.chargers}\n"
            + f"연중 무휴: {self.is_always}\n"
            + "\n"
        )
