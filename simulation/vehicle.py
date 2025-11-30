"""
Vehicle class - reprezentuje pojazdy w symulacji
"""

from dataclasses import dataclass
from typing import Optional
from enum import Enum


class VehicleType(Enum):
    """Typy pojazdów w symulacji"""
    REGULAR = "regular"
    PRIVILEGED = "privileged"


@dataclass
class Vehicle:
    """Klasa reprezentująca pojedynczy pojazd"""
    id: int
    vehicle_type: VehicleType
    entry_time: float
    current_position: float
    speed: float
    lane: int
    will_turn: bool
    turn_position: Optional[float] = None
    waiting_time: float = 0.0
    travel_time: float = 0.0