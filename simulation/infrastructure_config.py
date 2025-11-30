"""
Infrastructure configuration - konfiguracja infrastruktury drogowej
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class InfrastructureConfig:
    """Konfiguracja infrastruktury drogowej"""
    num_lanes: int = 2
    has_bus_lane: bool = False
    bus_lane_capacity: int = 0
    traffic_light_positions: List[float] = field(default_factory=lambda: [1.0, 2.5, 4.0])
    traffic_light_green_ratio: float = 0.6  # procent czasu na zielonym świetle
    description: str = "Standardowa konfiguracja"