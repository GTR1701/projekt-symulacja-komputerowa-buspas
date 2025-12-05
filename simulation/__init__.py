"""
Simulation package - zawiera wszystkie klasy związane z silnikiem symulacji
"""

from .vehicle import Vehicle, VehicleType
from .traffic_light import TrafficLight
from .infrastructure_config import InfrastructureConfig
from .simulation_parameters import SimulationParameters, RoadConfiguration
from .traffic_simulation import TrafficSimulation
from .variant_configs import (
    get_variant_a_parameters,
    get_variant_b_parameters, 
    get_variant_c_parameters,
    get_variant_d_parameters,
    get_default_parameters,
    get_variant_config_description,
    get_variant_short_description,
    create_simulation_with_parameters
)
from .constants import (
    VEHICLE_LENGTH,
    VEHICLE_SPACING,
    VEHICLE_TOTAL_SPACE,
    JAM_THRESHOLD_DISTANCE,
    DETECTION_DISTANCE,
    BASE_VEHICLE_SPEED,
    SLOW_TRAFFIC_THRESHOLD,
    TRAFFIC_LIGHT_STOPPING_DISTANCE,
    MIN_DENSITY_FACTOR,
    DENSITY_REDUCTION_RATE,
    SECONDS_PER_HOUR,
    DEFAULT_SIDE_ROAD_POSITIONS,
    BUS_EFFICIENCY_TIME_WEIGHT,
    BUS_EFFICIENCY_SPEED_WEIGHT
)

__all__ = [
    'Vehicle', 'VehicleType',
    'TrafficLight',
    'InfrastructureConfig',
    'SimulationParameters', 'RoadConfiguration',
    'TrafficSimulation',
    'get_variant_a_parameters',
    'get_variant_b_parameters',
    'get_variant_c_parameters', 
    'get_variant_d_parameters',
    'get_default_parameters',
    'get_variant_config_description',
    'get_variant_short_description',
    'create_simulation_with_parameters'
]