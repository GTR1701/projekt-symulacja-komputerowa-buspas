"""
Variant configurations - funkcje definiujące różne warianty infrastruktury
"""

from typing import Dict, Any
from .simulation_parameters import SimulationParameters
from .infrastructure_config import InfrastructureConfig
from .simulation_parameters import RoadConfiguration


def get_variant_a_parameters(params: SimulationParameters) -> Dict[str, Any]:
    """Wariant A: 3 pasy regularne, bez buspasa"""
    return {
        'num_lanes': 3,
        'has_bus_lane': False,
        'traffic_light_positions': params.side_road_positions or [0.5],
        'green_ratio': 0.6
    }


def get_variant_b_parameters(params: SimulationParameters) -> Dict[str, Any]:
    """Wariant B: 2 pasy regularne + buspas"""
    return {
        'num_lanes': 2,
        'has_bus_lane': True,
        'traffic_light_positions': params.side_road_positions or [0.5],
        'green_ratio': 0.6
    }


def get_variant_c_parameters(params: SimulationParameters) -> Dict[str, Any]:
    """Wariant C: 3 pasy regularne + buspas"""
    return {
        'num_lanes': 3,
        'has_bus_lane': True,
        'traffic_light_positions': params.side_road_positions or [0.5],
        'green_ratio': 0.6
    }


def get_variant_d_parameters(params: SimulationParameters) -> Dict[str, Any]:
    """Wariant D: 4 pasy regularne, bez buspasa"""
    return {
        'num_lanes': 4,
        'has_bus_lane': False,
        'traffic_light_positions': params.side_road_positions or [0.5],
        'green_ratio': 0.6
    }


def get_default_parameters(params: SimulationParameters) -> Dict[str, Any]:
    """Domyślna konfiguracja infrastruktury"""
    return {
        'num_lanes': 2,
        'has_bus_lane': False,
        'traffic_light_positions': params.side_road_positions or [0.5],
        'green_ratio': 0.6
    }


def get_variant_config_description(variant_name: str, params: SimulationParameters) -> str:
    """Zwraca opis konfiguracji dla danego wariantu"""
    if variant_name.upper() == 'A':
        infra_params = get_variant_a_parameters(params)
    elif variant_name.upper() == 'B':
        infra_params = get_variant_b_parameters(params)
    elif variant_name.upper() == 'C':
        infra_params = get_variant_c_parameters(params)
    elif variant_name.upper() == 'D':
        infra_params = get_variant_d_parameters(params)
    else:
        infra_params = get_default_parameters(params)
    
    description_parts = []
    
    if infra_params['has_bus_lane']:
        description_parts.append(f"{infra_params['num_lanes']} pasy + buspas")
    else:
        description_parts.append(f"{infra_params['num_lanes']} pasów")
    
    num_lights = len(infra_params['traffic_light_positions'])
    description_parts.append(f"{num_lights} świateł")
    
    green_ratio = infra_params['green_ratio']
    description_parts.append(f"{green_ratio*100:.0f}% zielone")
    
    return " | ".join(description_parts)


def get_variant_short_description(variant_name: str, params: SimulationParameters) -> str:
    """Zwraca krótki opis konfiguracji dla wykresów"""
    if variant_name.upper() == 'A':
        infra_params = get_variant_a_parameters(params)
    elif variant_name.upper() == 'B':
        infra_params = get_variant_b_parameters(params)
    elif variant_name.upper() == 'C':
        infra_params = get_variant_c_parameters(params)
    elif variant_name.upper() == 'D':
        infra_params = get_variant_d_parameters(params)
    else:
        infra_params = get_default_parameters(params)
    
    if infra_params['has_bus_lane']:
        return f"{infra_params['num_lanes']}P+Bus"
    else:
        return f"{infra_params['num_lanes']}P"


def create_simulation_with_parameters(params: SimulationParameters, infra_params: Dict[str, Any]) -> 'TrafficSimulation':
    """Tworzy symulację z podanymi parametrami infrastruktury
    
    Args:
        params: parametry symulacji
        infra_params: parametry infrastruktury (num_lanes, has_bus_lane, etc.)
    
    Returns:
        Skonfigurowana instancja TrafficSimulation
    """
    from .traffic_simulation import TrafficSimulation
    
    config = InfrastructureConfig(
        num_lanes=infra_params.get('num_lanes', 2),
        has_bus_lane=infra_params.get('has_bus_lane', False),
        traffic_light_positions=infra_params.get('traffic_light_positions', [0.5]),
        traffic_light_green_ratio=infra_params.get('green_ratio', 0.6),
        description=f"Konfiguracja: {infra_params.get('num_lanes', 2)} pasów"
    )
    
    if 'cycle_duration' in infra_params:
        config.cycle_duration = infra_params['cycle_duration']
    
    return TrafficSimulation(RoadConfiguration.CUSTOM, params, config)