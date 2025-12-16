"""
Simulation parameters and road configuration enums
"""

from dataclasses import dataclass
from typing import Tuple, List, Optional
from enum import Enum


class RoadConfiguration(Enum):
    """Konfiguracje dróg do testowania"""
    VARIANT_A = "A"
    VARIANT_B = "B"
    CUSTOM = "CUSTOM"


@dataclass
class SimulationParameters:
    """Parametry symulacji"""
    traffic_intensity_range: Tuple[int, int] = (500, 1500)
    turning_percentage_range: Tuple[float, float] = (0.05, 0.20)
    privileged_percentage: float = 0.05
    
    road_length: float = 1.0
    lane_capacity: int = 75
    traffic_light_cycle: float = 67.5
    green_light_range: Tuple[float, float] = (45.0, 90.0)
    
    simulation_duration: float = 3600.0
    time_step: float = 1.0
    
    side_road_positions: Optional[List[float]] = None
    
    def __post_init__(self):
        if self.side_road_positions is None:
            self.side_road_positions = [0.5]