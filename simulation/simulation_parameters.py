"""
Simulation parameters and road configuration enums
"""

from dataclasses import dataclass
from typing import Tuple, List, Optional
from enum import Enum


class RoadConfiguration(Enum):
    """Konfiguracje dróg do testowania"""
    VARIANT_A = "A"  # Więcej pasów, bez buspasa
    VARIANT_B = "B"  # Mniej pasów + oddzielny buspas
    CUSTOM = "CUSTOM"  # Niestandardowa konfiguracja


@dataclass
class SimulationParameters:
    """Parametry symulacji"""
    traffic_intensity_range: Tuple[int, int] = (500, 1500)  # pojazdy/h
    turning_percentage_range: Tuple[float, float] = (0.05, 0.20)  # 5-20%
    privileged_percentage: float = 0.05  # 3-10%, domyślnie 5%
    
    road_length: float = 5.0  # km
    lane_capacity: int = 75  # pojazdy/km
    traffic_light_cycle: float = 67.5  # sekundy (domyślny, może być nadpisany)
    green_light_range: Tuple[float, float] = (45.0, 90.0)
    
    simulation_duration: float = 3600.0  # 1 godzina w sekundach
    time_step: float = 1.0  # sekunda
    
    side_road_positions: Optional[List[float]] = None
    
    def __post_init__(self):
        if self.side_road_positions is None:
            self.side_road_positions = [1.0, 2.5, 4.0]