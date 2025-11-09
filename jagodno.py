"""
Symulacja Problemu Jagodzińskiego - Ruch drogowy na ulicy buforowej
Autor: Dawid Kowal
"""

import os
import numpy as np
import random
import matplotlib.pyplot as plt
import pandas as pd
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Any
from enum import Enum
import time

# Stałe symulacji ruchu drogowego
VEHICLE_LENGTH = 0.0045  # km - średnia długość pojazdu (4.5m)
VEHICLE_SPACING = 0.0005  # km - minimalna odległość między pojazdami (0.5m) 
VEHICLE_TOTAL_SPACE = VEHICLE_LENGTH + VEHICLE_SPACING  # 5m całkowite zajęcie drogi
JAM_THRESHOLD_DISTANCE = 0.050  # km - odległość < 50m = korek (zatłoczony ruch miejski)
DETECTION_DISTANCE = 0.500  # km - odległość sprawdzania pojazdów z przodu (500m)

class VehicleType(Enum):
    """Typy pojazdów w symulacji"""
    REGULAR = "regular"
    PRIVILEGED = "privileged"  # autobusy, karetki, etc.

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

@dataclass
class TrafficLight:
    """Klasa reprezentująca sygnalizację świetlną"""
    position: float
    cycle_duration: float
    green_duration: float
    current_phase: str  # "green" lub "red"
    phase_start_time: float

@dataclass
class InfrastructureConfig:
    """Konfiguracja infrastruktury drogowej"""
    num_lanes: int = 2
    has_bus_lane: bool = False
    bus_lane_capacity: int = 0
    traffic_light_positions: List[float] = field(default_factory=lambda: [1.0, 2.5, 4.0])
    traffic_light_green_ratio: float = 0.6  # procent czasu na zielonym świetle
    description: str = "Standardowa konfiguracja"

# Funkcje pomocnicze do tworzenia predefiniowanych konfiguracji
def create_wide_road_config() -> InfrastructureConfig:
    """Tworzy konfigurację szerokiej drogi bez buspasa"""
    return InfrastructureConfig(
        num_lanes=3,
        has_bus_lane=False,
        bus_lane_capacity=0,
        traffic_light_positions=[1.0, 2.5, 4.0],
        traffic_light_green_ratio=0.6,
        description="Szeroka droga - 3 pasy, bez buspasa"
    )

def create_bus_lane_config(lane_capacity: int = 75) -> InfrastructureConfig:
    """Tworzy konfigurację z buspassem"""
    return InfrastructureConfig(
        num_lanes=2,
        has_bus_lane=True,
        bus_lane_capacity=lane_capacity,
        traffic_light_positions=[1.0, 2.5, 4.0],
        traffic_light_green_ratio=0.6,
        description="Droga z buspassem - 2 pasy + buspas"
    )

def create_optimized_config(lane_capacity: int = 75) -> InfrastructureConfig:
    """Tworzy zoptymalizowaną konfigurację z dłuższym zielonym światłem"""
    return InfrastructureConfig(
        num_lanes=3,
        has_bus_lane=True,
        bus_lane_capacity=lane_capacity,
        traffic_light_positions=[1.5, 3.0],  # Mniej sygnalizacji
        traffic_light_green_ratio=0.7,  # Dłuższe zielone światło
        description="Konfiguracja zoptymalizowana - 3 pasy + buspas, mniej świateł"
    )

def create_heavy_traffic_config(lane_capacity: int = 75) -> InfrastructureConfig:
    """Tworzy konfigurację dla intensywnego ruchu"""
    return InfrastructureConfig(
        num_lanes=4,
        has_bus_lane=True,
        bus_lane_capacity=lane_capacity,
        traffic_light_positions=[0.8, 1.8, 2.8, 3.8],  # Więcej świateł
        traffic_light_green_ratio=0.65,
        description="Konfiguracja dla intensywnego ruchu - 4 pasy + buspas"
    )

class RoadConfiguration(Enum):
    """Konfiguracje dróg do testowania"""
    VARIANT_A = "A"  # Więcej pasów, bez buspasa
    VARIANT_B = "B"  # Mniej pasów + oddzielny buspas
    CUSTOM = "CUSTOM"  # Niestandardowa konfiguracja

@dataclass
class SimulationParameters:
    """Parametry symulacji"""
    # Parametry ruchu
    traffic_intensity_range: Tuple[int, int] = (500, 1500)  # pojazdy/h
    turning_percentage_range: Tuple[float, float] = (0.05, 0.20)  # 5-20%
    privileged_percentage: float = 0.05  # 3-10%, domyślnie 5%
    
    # Parametry infrastruktury
    road_length: float = 5.0  # km
    lane_capacity: int = 75  # pojazdy/km
    traffic_light_cycle: float = 67.5  # sekundy
    
    # Parametry czasowe
    simulation_duration: float = 3600.0  # 1 godzina w sekundach
    time_step: float = 1.0  # sekunda
    
    # Pozycje skrzyżowań/odgałęzień (jako procent długości drogi)
    side_road_positions: Optional[List[float]] = None
    
    def __post_init__(self):
        if self.side_road_positions is None:
            # Pozycje bocznych dróg (co około 1km)
            self.side_road_positions = [1.0, 2.5, 4.0]

# Funkcje definiujące warianty infrastruktury
def get_variant_a_parameters(params: SimulationParameters) -> Dict[str, Any]:
    """Wariant A: Droga poszerzona o dodatkowe pasy, bez buspasa"""
    return {
        'num_lanes': 3,
        'has_bus_lane': False,
        'bus_lane_capacity': 0,
        'traffic_light_positions': params.side_road_positions or [1.0, 2.5, 4.0],
        'green_ratio': 0.6
    }

def get_variant_b_parameters(params: SimulationParameters) -> Dict[str, Any]:
    """Wariant B: Droga jednopasmowa z oddzielnym buspassem"""
    return {
        'num_lanes': 2,
        'has_bus_lane': True,
        'bus_lane_capacity': params.lane_capacity,
        'traffic_light_positions': params.side_road_positions or [1.0, 2.5, 4.0],
        'green_ratio': 0.6
    }

def get_variant_c_parameters(params: SimulationParameters) -> Dict[str, Any]:
    """Wariant C: Konfiguracja zoptymalizowana - więcej pasów + buspas, mniej świateł"""
    return {
        'num_lanes': 3,
        'has_bus_lane': True,
        'bus_lane_capacity': params.lane_capacity,
        'traffic_light_positions': [1.5, 3.0],  # Mniej sygnalizacji
        'green_ratio': 0.7  # Dłuższe zielone światło
    }

def get_variant_d_parameters(params: SimulationParameters) -> Dict[str, Any]:
    """Wariant D: Konfiguracja dla intensywnego ruchu - 4 pasy + buspas"""
    return {
        'num_lanes': 4,
        'has_bus_lane': True,
        'bus_lane_capacity': params.lane_capacity,
        'traffic_light_positions': [0.8, 1.8, 2.8, 3.8],  # Więcej świateł
        'green_ratio': 0.65
    }

def get_default_parameters(params: SimulationParameters) -> Dict[str, Any]:
    """Domyślna konfiguracja infrastruktury"""
    return {
        'num_lanes': 2,
        'has_bus_lane': False,
        'bus_lane_capacity': 0,
        'traffic_light_positions': params.side_road_positions or [1.0, 2.5, 4.0],
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
    
    # Tworzenie opisu
    description_parts = []
    
    # Podstawowa informacja o pasach
    if infra_params['has_bus_lane']:
        description_parts.append(f"{infra_params['num_lanes']} pasy + buspas")
    else:
        description_parts.append(f"{infra_params['num_lanes']} pasów")
    
    # Liczba świateł
    num_lights = len(infra_params['traffic_light_positions'])
    description_parts.append(f"{num_lights} świateł")
    
    # Czas zielonego
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
    
    # Krótki opis
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
    config = InfrastructureConfig(
        num_lanes=infra_params.get('num_lanes', 2),
        has_bus_lane=infra_params.get('has_bus_lane', False),
        bus_lane_capacity=infra_params.get('bus_lane_capacity', 0),
        traffic_light_positions=infra_params.get('traffic_light_positions', [1.0, 2.5, 4.0]),
        traffic_light_green_ratio=infra_params.get('green_ratio', 0.6),
        description=f"Konfiguracja: {infra_params.get('num_lanes', 2)} pasów"
    )
    return TrafficSimulation(RoadConfiguration.CUSTOM, params, config)

class TrafficSimulation:
    """Główna klasa symulacji ruchu drogowego"""
    
    def __init__(self, config: RoadConfiguration, params: SimulationParameters, 
                 infrastructure_config: Optional[InfrastructureConfig] = None):
        self.config = config
        self.params = params
        self.current_time = 0.0
        
        # Konfiguracja infrastruktury
        self.infrastructure_config = infrastructure_config
        
        # Uzyskaj parametry konfiguracji infrastruktury
        infra_params = self._get_infrastructure_parameters()
        
        # Inicjalizacja infrastruktury
        self._setup_infrastructure(**infra_params)
        
        # Listy pojazdów
        self.vehicles: List[Vehicle] = []
        self.completed_vehicles: List[Vehicle] = []
        
        # Statystyki
        self.statistics = {
            'total_vehicles': 0,
            'avg_travel_time': 0.0,
            'avg_speed': 0.0,
            'avg_waiting_time': 0.0,
            'traffic_jam_length': 0.0,
            'bus_efficiency': 0.0
        }
        
        # generator ID
        self.next_vehicle_id = 1
        
    def _get_infrastructure_parameters(self) -> Dict[str, Any]:
        """Zwraca parametry infrastruktury na podstawie konfiguracji lub wariantu
        
        Returns:
            Dict: num_lanes, has_bus_lane, bus_lane_capacity, 
            traffic_light_positions, green_ratio
        """

        if self.infrastructure_config is not None:
            return {
                'num_lanes': self.infrastructure_config.num_lanes,
                'has_bus_lane': self.infrastructure_config.has_bus_lane,
                'bus_lane_capacity': self.infrastructure_config.bus_lane_capacity,
                'traffic_light_positions': self.infrastructure_config.traffic_light_positions,
                'green_ratio': self.infrastructure_config.traffic_light_green_ratio
            }
        elif self.config == RoadConfiguration.VARIANT_A:
            return get_variant_a_parameters(self.params)
        elif self.config == RoadConfiguration.VARIANT_B:
            return get_variant_b_parameters(self.params)
        else:
            return get_default_parameters(self.params)
    
    def get_configuration_description(self) -> str:
        """Zwraca szczegółowy opis konfiguracji infrastruktury"""
        description_parts = []
        
        # Podstawowa informacja o pasach
        if self.has_bus_lane:
            description_parts.append(f"{self.num_lanes} pasy regularne + buspas")
            description_parts.append(f"Pojemność buspasa: {self.bus_lane_capacity} pojazdy/km")
        else:
            description_parts.append(f"{self.num_lanes} pasów regularnych")
        
        # Informacje o sygnalizacji
        light_positions = [light.position for light in self.traffic_lights]
        description_parts.append(f"Sygnalizacja na km: {light_positions}")
        
        if self.traffic_lights:
            green_ratio = self.traffic_lights[0].green_duration / self.traffic_lights[0].cycle_duration
            description_parts.append(f"Czas zielonego: {green_ratio*100:.0f}% cyklu")
            description_parts.append(f"Cykl świateł: {self.traffic_lights[0].cycle_duration:.0f}s")
        
        return " | ".join(description_parts)
    
    def get_short_configuration_description(self) -> str:
        """Zwraca krótki opis konfiguracji do wykresów"""
        if self.has_bus_lane:
            return f"{self.num_lanes}P+Bus, {len(self.traffic_lights)}S"
        else:
            return f"{self.num_lanes}P, {len(self.traffic_lights)}S"
        
    def _setup_infrastructure(self, num_lanes: int, has_bus_lane: bool, 
                             bus_lane_capacity: int, traffic_light_positions: List[float],
                             green_ratio: float = 0.6):
        """Konfiguracja infrastruktury na podstawie przekazanych parametrów
        
        Args:
            num_lanes: liczba pasów regularnych
            has_bus_lane: czy istnieje oddzielny buspas
            bus_lane_capacity: pojemność buspasa w pojazdach/km
            traffic_light_positions: pozycje sygnalizacji świetlnej w km
            green_ratio: procent czasu cyklu na zielonym świetle (0.0-1.0)
        """
        self.num_lanes = num_lanes
        self.has_bus_lane = has_bus_lane
        self.bus_lane_capacity = bus_lane_capacity
            
        # Sygnalizacja świetlna na głównych skrzyżowaniach
        self.traffic_lights = [
            TrafficLight(
                position=pos,
                cycle_duration=self.params.traffic_light_cycle,
                green_duration=self.params.traffic_light_cycle * green_ratio,
                current_phase="green",
                phase_start_time=0.0
            )
            for pos in traffic_light_positions
        ]
    
    def _generate_traffic_intensity(self):
        """Generuje natężenie ruchu zgodnie z rozkładem Poissona"""
        # Średnie natężenie z zakresu
        mean_intensity = np.mean(self.params.traffic_intensity_range)
        # Rozkład Poissona dla natężenia ruchu
        return np.random.poisson(mean_intensity / 3600)  # pojazdy na sekundę
    
    def _should_vehicle_turn(self) -> bool:
        """Określa czy pojazd skręci w boczną drogę"""
        turning_rate = random.uniform(*self.params.turning_percentage_range)
        return random.random() < turning_rate
    
    def _assign_turn_position(self) -> float:
        """Przypisuje pozycję skrętu pojazdu"""
        positions = self.params.side_road_positions or [1.0, 2.5, 4.0]
        return random.choice(positions)
    
    def _generate_vehicle(self) -> Vehicle:
        """Generuje nowy pojazd"""
        vehicle_type = (VehicleType.PRIVILEGED 
                       if random.random() < self.params.privileged_percentage 
                       else VehicleType.REGULAR)
        
        will_turn = self._should_vehicle_turn()
        turn_position = self._assign_turn_position() if will_turn else None
        
        # Przypisanie pasa
        if vehicle_type == VehicleType.PRIVILEGED and self.has_bus_lane:
            lane = -1  # Buspas oznaczamy jako pas -1
        else:
            lane = random.randint(0, self.num_lanes - 1)
        
        vehicle = Vehicle(
            id=self.next_vehicle_id,
            vehicle_type=vehicle_type,
            entry_time=self.current_time,
            current_position=0.0,
            speed=0.0,
            lane=lane,
            will_turn=will_turn,
            turn_position=turn_position
        )
        
        self.next_vehicle_id += 1
        return vehicle
    
    def _update_traffic_lights(self):
        """Aktualizuje stan sygnalizacji świetlnej"""
        for light in self.traffic_lights:
            time_in_phase = self.current_time - light.phase_start_time
            
            if light.current_phase == "green" and time_in_phase >= light.green_duration:
                light.current_phase = "red"
                light.phase_start_time = self.current_time
            elif light.current_phase == "red" and time_in_phase >= (light.cycle_duration - light.green_duration):
                light.current_phase = "green"
                light.phase_start_time = self.current_time
    
    def _calculate_vehicle_speed(self, vehicle: Vehicle) -> float:
        """Oblicza prędkość pojazdu na podstawie warunków ruchu"""
        base_speed = 50.0  # km/h - prędkość bazowa
        
        # Sprawdź czy pojazd jest blokowany przez sygnalizację
        for light in self.traffic_lights:
            distance_to_light = light.position - vehicle.current_position
            if 0 < distance_to_light < 0.1 and light.current_phase == "red":
                return 0.0  # Zatrzymanie przed czerwonym światłem
    
        # Sprawdź gęstość ruchu na pasie
        vehicles_ahead = [other_vehicle for other_vehicle in self.vehicles 
                         if other_vehicle.lane == vehicle.lane
                         and other_vehicle.current_position > vehicle.current_position
                         and other_vehicle.current_position - vehicle.current_position < DETECTION_DISTANCE
                         and other_vehicle.id != vehicle.id]
    
        # Redukcja prędkości w zależności od gęstości
        density_factor = max(0.1, 1.0 - len(vehicles_ahead) * 0.15)
        
        # Dodatkowy bonus dla buspasa
        if vehicle.lane == -1:  # Buspas
            density_factor = min(1.0, density_factor * 1.2)
        
        return base_speed * density_factor
    
    def _move_vehicles(self):
        """Przesuwa pojazdy i aktualizuje ich stan"""
        vehicles_to_remove = []
        
        for vehicle in self.vehicles:
            # Oblicz prędkość
            vehicle.speed = self._calculate_vehicle_speed(vehicle)
            
            # Jeśli pojazd się zatrzymał, zwiększ czas oczekiwania
            if vehicle.speed == 0:
                vehicle.waiting_time += self.params.time_step
            
            # Przesuń pojazd
            distance = vehicle.speed * (self.params.time_step / 3600)  # konwersja na km
            vehicle.current_position += distance
            
            # Sprawdź czy pojazd skręca
            if (vehicle.will_turn and vehicle.turn_position and 
                vehicle.current_position >= vehicle.turn_position):
                vehicle.travel_time = self.current_time - vehicle.entry_time
                self.completed_vehicles.append(vehicle)
                vehicles_to_remove.append(vehicle)
            
            # Sprawdź czy pojazd dojechał do końca
            elif vehicle.current_position >= self.params.road_length:
                vehicle.travel_time = self.current_time - vehicle.entry_time
                self.completed_vehicles.append(vehicle)
                vehicles_to_remove.append(vehicle)
        
        # Usuń pojazdy, które zakończyły podróż
        for vehicle in vehicles_to_remove:
            self.vehicles.remove(vehicle)
    
    def _calculate_traffic_jam_length(self) -> float:
        """Oblicza długość korka (pojazdy o prędkości < 10 km/h)
        
        Realistyczne założenia:
        - Średnia długość pojazdu: 4.5m (osobowy)
        - Minimalna odległość między pojazdami w korku: 0.5m
        - Całkowite zajęcie drogi na pojazd: 5m = 0.005km
        - Korek = pojazdy w odległości < 50m od siebie
        """
        slow_vehicles = [v for v in self.vehicles if v.speed < 10.0]
        if not slow_vehicles:
            return 0.0
        
        # Znajdź najdłuższy ciągły odcinek wolno jadących pojazdów
        positions = sorted([v.current_position for v in slow_vehicles])
        
        max_jam_length = 0.0
        current_jam_length = 0.0
        
        for i in range(len(positions)):
            if i == 0:
                current_jam_length = VEHICLE_TOTAL_SPACE  # Pierwszy pojazd: długość + odstęp
            else:
                gap = positions[i] - positions[i-1]
                if gap < JAM_THRESHOLD_DISTANCE:  # Jeśli odległość < 50m, to ciągły korek (zatłoczony ruch miejski)
                    current_jam_length += VEHICLE_TOTAL_SPACE  # Dodaj długość kolejnego pojazdu
                else:
                    max_jam_length = max(max_jam_length, current_jam_length)
                    current_jam_length = VEHICLE_TOTAL_SPACE  # Rozpocznij nowy segment korka
        
        return max(max_jam_length, current_jam_length)
    
    def _calculate_bus_efficiency(self) -> float:
        """Oblicza efektywność buspasa (tylko dla wariantu B)"""
        if not self.has_bus_lane:
            return 0.0
        
        bus_vehicles = [v for v in self.completed_vehicles 
                       if v.vehicle_type == VehicleType.PRIVILEGED]
        regular_vehicles = [v for v in self.completed_vehicles 
                          if v.vehicle_type == VehicleType.REGULAR]
        
        if not bus_vehicles or not regular_vehicles:
            return 0.0
        
        avg_bus_time = np.mean([v.travel_time for v in bus_vehicles])
        avg_regular_time = np.mean([v.travel_time for v in regular_vehicles])
        
        # Efektywność jako stosunek czasu przejazdu
        return max(0.0, (avg_regular_time - avg_bus_time) / avg_regular_time * 100)
    
    def step(self):
        """Wykonuje jeden krok symulacji"""
        # Generuj nowe pojazdy
        vehicles_to_generate = self._generate_traffic_intensity()
        for _ in range(int(vehicles_to_generate)):
            if len(self.vehicles) < self.params.lane_capacity * self.num_lanes:
                self.vehicles.append(self._generate_vehicle())
        
        # Aktualizuj sygnalizację
        self._update_traffic_lights()
        
        # Przesuń pojazdy
        self._move_vehicles()
        
        # Zwiększ czas
        self.current_time += self.params.time_step
    
    def run_simulation(self) -> Dict:
        """Uruchamia pełną symulację"""
        print(f"Uruchamianie symulacji - Wariant {self.config.value}")
        
        # Wyświetl szczegółową konfigurację
        config_desc = self.get_configuration_description()
        print(f"Konfiguracja: {config_desc}")
        
        start_time = time.time()
        steps = int(self.params.simulation_duration / self.params.time_step)
        
        for step in range(steps):
            self.step()
            
            # Raportowanie postępu co 10% symulacji
            if step % (steps // 10) == 0:
                progress = (step / steps) * 100
                print(f"Postęp: {progress:.0f}% - Pojazdy w ruchu: {len(self.vehicles)}")
        
        # Oblicz końcowe statystyki
        self._calculate_final_statistics()
        
        execution_time = time.time() - start_time
        print(f"Symulacja zakończona w {execution_time:.2f} sekund")
        
        return self.statistics
    
    def _calculate_final_statistics(self):
        """Oblicza końcowe statystyki symulacji"""
        if not self.completed_vehicles:
            return
        
        travel_times = [v.travel_time for v in self.completed_vehicles]
        waiting_times = [v.waiting_time for v in self.completed_vehicles]
        speeds = []
        
        for vehicle in self.completed_vehicles:
            if vehicle.travel_time > 0:
                # Prędkość średnia = dystans / czas
                distance = vehicle.turn_position if vehicle.will_turn and vehicle.turn_position else self.params.road_length
                avg_speed = (distance / vehicle.travel_time) * 3600  # km/h
                speeds.append(avg_speed)
        
        self.statistics = {
            'total_vehicles': len(self.completed_vehicles),
            'avg_travel_time': np.mean(travel_times),
            'avg_speed': np.mean(speeds) if speeds else 0.0,
            'avg_waiting_time': np.mean(waiting_times),
            'traffic_jam_length': self._calculate_traffic_jam_length(),
            'bus_efficiency': self._calculate_bus_efficiency()
        }

def run_comparison_study():
    """Uruchamia porównawczą analizę wszystkich wariantów"""
    print("="*60)
    print("SYMULACJA PROBLEMU JAGODZIŃSKIEGO")
    print("Analiza porównawcza wariantów infrastruktury")
    print("="*60)
    
    params = SimulationParameters()
    
    # Wyświetl opisy wszystkich konfiguracji
    print("\nKONFIGURACJE TESTOWANYCH WARIANTÓW:")
    print("-" * 60)
    for variant in ['A', 'B', 'C', 'D']:
        config_desc = get_variant_config_description(variant, params)
        print(f"Wariant {variant}: {config_desc}")
    print("-" * 60)
    
    # Wyniki dla wszystkich wariantów
    results = {}
    
    # Wariant A: Więcej pasów, bez buspasa (używając bezpośrednio funkcji wariantów)
    print("\n" + "="*40)
    print("WARIANT A: Droga poszerzona, bez buspasa")
    config_a = get_variant_config_description('A', params)
    print(f"Konfiguracja: {config_a}")
    print("="*40)
    sim_a = TrafficSimulation(RoadConfiguration.VARIANT_A, params)
    results['A'] = sim_a.run_simulation()
    
    # Wariant B: Mniej pasów + buspas (używając bezpośrednio funkcji wariantów)
    print("\n" + "="*40)
    print("WARIANT B: Droga z oddzielnym buspassem")
    config_b = get_variant_config_description('B', params)
    print(f"Konfiguracja: {config_b}")
    print("="*40)
    sim_b = TrafficSimulation(RoadConfiguration.VARIANT_B, params)
    results['B'] = sim_b.run_simulation()
    
    # Wariant C: Konfiguracja zoptymalizowana (używając funkcji zewnętrznej)
    print("\n" + "="*40)
    print("WARIANT C: Konfiguracja zoptymalizowana")
    config_c = get_variant_config_description('C', params)
    print(f"Konfiguracja: {config_c}")
    print("="*40)
    variant_c_params = get_variant_c_parameters(params)
    sim_c = create_simulation_with_parameters(params, variant_c_params)
    results['C'] = sim_c.run_simulation()
    
    # Wariant D: Konfiguracja dla intensywnego ruchu (używając funkcji zewnętrznej)
    print("\n" + "="*40)
    print("WARIANT D: Konfiguracja dla intensywnego ruchu")
    config_d = get_variant_config_description('D', params)
    print(f"Konfiguracja: {config_d}")
    print("="*40)
    variant_d_params = get_variant_d_parameters(params)
    sim_d = create_simulation_with_parameters(params, variant_d_params)
    results['D'] = sim_d.run_simulation()
    
    # Analiza wyników
    print("\n" + "="*60)
    print("PODSUMOWANIE WYNIKÓW")
    print("="*60)
    
    # Tworzenie rozszerzonej tabeli porównawczej
    comparison_data = {
        'Wskaźnik': [
            'Łączna liczba pojazdów',
            'Średni czas przejazdu [s]',
            'Średnia prędkość [km/h]',
            'Średni czas postoju [s]',
            'Długość korka [km]',
            'Efektywność buspasa [%]'
        ],
        f'Wariant A\n({get_variant_short_description("A", params)})': [
            results['A']['total_vehicles'],
            f"{results['A']['avg_travel_time']:.1f}",
            f"{results['A']['avg_speed']:.1f}",
            f"{results['A']['avg_waiting_time']:.1f}",
            f"{results['A']['traffic_jam_length']:.2f}",
            "N/A"
        ],
        f'Wariant B\n({get_variant_short_description("B", params)})': [
            results['B']['total_vehicles'],
            f"{results['B']['avg_travel_time']:.1f}",
            f"{results['B']['avg_speed']:.1f}",
            f"{results['B']['avg_waiting_time']:.1f}",
            f"{results['B']['traffic_jam_length']:.2f}",
            f"{results['B']['bus_efficiency']:.1f}"
        ],
        f'Wariant C\n({get_variant_short_description("C", params)})': [
            results['C']['total_vehicles'],
            f"{results['C']['avg_travel_time']:.1f}",
            f"{results['C']['avg_speed']:.1f}",
            f"{results['C']['avg_waiting_time']:.1f}",
            f"{results['C']['traffic_jam_length']:.2f}",
            f"{results['C']['bus_efficiency']:.1f}"
        ],
        f'Wariant D\n({get_variant_short_description("D", params)})': [
            results['D']['total_vehicles'],
            f"{results['D']['avg_travel_time']:.1f}",
            f"{results['D']['avg_speed']:.1f}",
            f"{results['D']['avg_waiting_time']:.1f}",
            f"{results['D']['traffic_jam_length']:.2f}",
            f"{results['D']['bus_efficiency']:.1f}"
        ]
    }
    
    df = pd.DataFrame(comparison_data)
    print(df.to_string(index=False))
    
    # Analiza i ranking
    print("\n" + "="*60)
    print("RANKING WARIANTÓW")
    print("="*60)
    
    # Ranking po najkrótszym czasie przejazdu
    travel_time_ranking = sorted(results.items(), key=lambda x: x[1]['avg_travel_time'])
    print("\n🏁 Ranking po czasie przejazdu (najlepszy → najgorszy):")
    for i, (variant, data) in enumerate(travel_time_ranking, 1):
        print(f"   {i}. Wariant {variant}: {data['avg_travel_time']:.1f}s")
    
    # Ranking po najwyższej średniej prędkości
    speed_ranking = sorted(results.items(), key=lambda x: x[1]['avg_speed'], reverse=True)
    print("\n🚗 Ranking po średniej prędkości (najlepszy → najgorszy):")
    for i, (variant, data) in enumerate(speed_ranking, 1):
        print(f"   {i}. Wariant {variant}: {data['avg_speed']:.1f} km/h")
    
    # Ranking po najkrótszych korkach
    jam_ranking = sorted(results.items(), key=lambda x: x[1]['traffic_jam_length'])
    print("\n🚦 Ranking po długości korków (najlepszy → najgorszy):")
    for i, (variant, data) in enumerate(jam_ranking, 1):
        print(f"   {i}. Wariant {variant}: {data['traffic_jam_length']:.2f} km")
    
    # Analiza hipotez
    print("\n" + "="*60)
    print("WERYFIKACJA HIPOTEZ BADAWCZYCH")
    print("="*60)
    
    print("\n1. Hipoteza: Buspas usprawnia ruch komunikacji miejskiej, ale nie wpływa znacząco na zmniejszenie korków.")
    
    variants_with_bus = [(k, v) for k, v in results.items() if v['bus_efficiency'] > 0]
    if variants_with_bus:
        avg_bus_efficiency = sum(v['bus_efficiency'] for _, v in variants_with_bus) / len(variants_with_bus)
        print(f"   - Średnia efektywność buspasa: {avg_bus_efficiency:.1f}%")
        
        bus_variants_jams = [v['traffic_jam_length'] for _, v in variants_with_bus]
        no_bus_variants_jams = [v['traffic_jam_length'] for k, v in results.items() if k == 'A']
        
        if no_bus_variants_jams and bus_variants_jams:
            jam_difference = ((no_bus_variants_jams[0] - min(bus_variants_jams)) / no_bus_variants_jams[0] * 100)
            print(f"   - Redukcja korków przez buspas: {jam_difference:+.1f}%")
    
    # Rekomendacje
    print("\n" + "="*60)
    print("REKOMENDACJE")
    print("="*60)
    
    best_travel_time = travel_time_ranking[0]
    best_speed = speed_ranking[0]
    best_jam = jam_ranking[0]
    
    print(f"🏆 NAJLEPSZY OGÓLNIE: Wariant {best_travel_time[0]} (najkrótszy czas przejazdu)")
    print(f"� NAJSZYBSZY: Wariant {best_speed[0]} (najwyższa średnia prędkość)")
    print(f"🚦 NAJMNIEJ KORKÓW: Wariant {best_jam[0]} (najkrótsze korki)")
    
    # Sprawdź czy wariant C (zoptymalizowany) jest najlepszy w jakiejś kategorii
    if 'C' in [best_travel_time[0], best_speed[0], best_jam[0]]:
        print("\n✅ Konfiguracja zoptymalizowana (Wariant C) wykazuje najlepsze wyniki!")
    
    return results

def test_custom_configuration():
    """Testuje niestandardową konfigurację infrastruktury"""
    print("="*60)
    print("TEST NIESTANDARDOWEJ KONFIGURACJI")
    print("="*60)
    
    params = SimulationParameters()
    
    # Przykład definicji niestandardowej konfiguracji poprzez parametry
    custom_variant_params = {
        'num_lanes': 5,  # Bardzo szeroka droga
        'has_bus_lane': True,
        'bus_lane_capacity': params.lane_capacity,
        'traffic_light_positions': [2.0, 4.0],  # Tylko dwie sygnalizacje
        'green_ratio': 0.8  # Bardzo długie zielone światło
    }
    
    print(f"Konfiguracja niestandardowa:")
    print(f"- Liczba pasów: {custom_variant_params['num_lanes']}")
    print(f"- Buspas: {'Tak' if custom_variant_params['has_bus_lane'] else 'Nie'}")
    print(f"- Pozycje świateł: {custom_variant_params['traffic_light_positions']}")
    print(f"- Czas zielonego: {custom_variant_params['green_ratio']*100:.0f}%")
    
    # Tworzymy symulację używając parametrów bezpośrednio
    sim = create_simulation_with_parameters(params, custom_variant_params)
    results = sim.run_simulation()
    
    print(f"\nWyniki:")
    print(f"- Pojazdy obsłużone: {results['total_vehicles']}")
    print(f"- Średni czas przejazdu: {results['avg_travel_time']:.1f}s")
    print(f"- Średnia prędkość: {results['avg_speed']:.1f} km/h")
    print(f"- Długość korka: {results['traffic_jam_length']:.2f} km")
    print(f"- Efektywność buspasa: {results['bus_efficiency']:.1f}%")
    
    # Wygeneruj wizualizację dla tego pojedynczego wariantu
    print("\nGenerowanie wizualizacji...")
    single_result = {'CUSTOM': results}
    create_visualization(single_result, "niestandardowa")
    
    return results

def test_direct_parameter_approach():
    """Demonstracja bezpośredniego wywołania metody z parametrami"""
    print("="*60)
    print("TEST BEZPOŚREDNIEGO PODEJŚCIA Z PARAMETRAMI")
    print("="*60)
    
    params = SimulationParameters()
    
    # Przykład bezpośredniego wywołania z konkretnymi parametrami
    print("Testowanie różnych konfiguracji poprzez bezpośrednie parametry...")
    
    # Konfiguracja 1: Minimalistyczna
    print("\n--- Konfiguracja minimalistyczna ---")
    minimal_params = {
        'num_lanes': 1,
        'has_bus_lane': False,
        'bus_lane_capacity': 0,
        'traffic_light_positions': [2.5],
        'green_ratio': 0.5
    }
    
    sim1 = create_simulation_with_parameters(params, minimal_params)
    results1 = sim1.run_simulation()
    print(f"Wynik: {results1['avg_travel_time']:.1f}s średni czas, {results1['avg_speed']:.1f} km/h")
    
    # Konfiguracja 2: Maksymalna
    print("\n--- Konfiguracja maksymalna ---")
    maximal_params = {
        'num_lanes': 6,
        'has_bus_lane': True,
        'bus_lane_capacity': params.lane_capacity * 2,
        'traffic_light_positions': [1.0, 2.0, 3.0, 4.0],
        'green_ratio': 0.9
    }
    
    sim2 = create_simulation_with_parameters(params, maximal_params)
    results2 = sim2.run_simulation()
    print(f"Wynik: {results2['avg_travel_time']:.1f}s średni czas, {results2['avg_speed']:.1f} km/h")
    
    # Porównanie
    print(f"\nPorównanie:")
    print(f"Konfiguracja minimalistyczna: {results1['avg_travel_time']:.1f}s")
    print(f"Konfiguracja maksymalna: {results2['avg_travel_time']:.1f}s")
    improvement = ((results1['avg_travel_time'] - results2['avg_travel_time']) / results1['avg_travel_time'] * 100)
    print(f"Poprawa: {improvement:+.1f}%")
    
    # Wygeneruj wizualizację porównawczą
    print("\nGenerowanie wizualizacji porównawczej...")
    comparison_results = {'minimal': results1, 'maximal': results2}
    create_visualization(comparison_results, "porownanie_parametrow")
    
    return {'minimal': results1, 'maximal': results2}

def create_visualization(results: Dict, filename_suffix: str = "wyniki"):
    """Tworzy wizualizację wyników symulacji dla wszystkich dostępnych wariantów
    
    Args:
        results: słownik z wynikami symulacji
        filename_suffix: sufiks dla nazwy pliku (domyślnie "wyniki")
    """
    try:
        import matplotlib.pyplot as plt
        import numpy as np
        
        # Sprawdź które warianty są dostępne
        available_variants = list(results.keys())
        n_variants = len(available_variants)
        
        if n_variants == 0:
            print("Brak wyników do wizualizacji")
            return
        
        # Tworzenie etykiet z opisami konfiguracji
        params = SimulationParameters()  # Domyślne parametry do opisu
        
        # Mapowanie nazw wariantów na czytelne etykiety z konfiguracją
        variant_labels = {}
        for var in available_variants:
            base_name = {
                'A': 'Wariant A\n(poszerzenie)',
                'B': 'Wariant B\n(buspas)', 
                'C': 'Wariant C\n(zoptymalizowany)',
                'D': 'Wariant D\n(intensywny ruch)',
                'CUSTOM': 'Konfiguracja\nniestandardowa',
                'minimal': 'Konfiguracja\nminimalistyczna',
                'maximal': 'Konfiguracja\nmaksymalna'
            }.get(var, f'Wariant {var}')
            
            # Dodaj krótki opis konfiguracji
            config_desc = get_variant_short_description(var, params)
            variant_labels[var] = f"{base_name}\n{config_desc}"
        
        # Tworzenie etykiet dla dostępnych wariantów
        labels = [variant_labels[var] for var in available_variants]
        
        # Paleta kolorów dla różnej liczby wariantów
        if n_variants == 2:
            bar_colors = ['lightblue', 'lightgreen']
        elif n_variants == 3:
            bar_colors = ['lightblue', 'lightgreen', 'lightcoral']
        elif n_variants == 4:
            bar_colors = ['lightblue', 'lightgreen', 'lightcoral', 'lightyellow']
        else:
            # Dla innych liczb wariantów użyj standardowej palety
            base_colors = ['lightblue', 'lightgreen', 'lightcoral', 'lightyellow', 'lightpink', 'lightgray']
            bar_colors = (base_colors * ((n_variants // len(base_colors)) + 1))[:n_variants]
        
        # Utwórz subplot - zawsze używaj układu 3x2 dla wszystkich wariantów
        fig, ((ax1, ax2), (ax3, ax4), (ax5, ax6)) = plt.subplots(3, 2, figsize=(14, 15))
        fig.suptitle('Porównanie wariantów rozwiązania Problemu Jagodzińskiego', fontsize=16)
        
        # Średni czas przejazdu
        travel_times = [results[var]['avg_travel_time'] for var in available_variants]
        bars1 = ax1.bar(labels, travel_times, color=bar_colors[:n_variants])
        ax1.set_ylabel('Czas [s]')
        ax1.set_title('Średni czas przejazdu')
        ax1.tick_params(axis='x', rotation=45)
        
        # Dodaj wartości na słupkach
        for bar, value in zip(bars1, travel_times):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'{value:.0f}s', ha='center', va='bottom', fontsize=9)
        
        # Średnia prędkość
        speeds = [results[var]['avg_speed'] for var in available_variants]
        bars2 = ax2.bar(labels, speeds, color=bar_colors[:n_variants])
        ax2.set_ylabel('Prędkość [km/h]')
        ax2.set_title('Średnia prędkość pojazdu')
        ax2.tick_params(axis='x', rotation=45)
        
        # Dodaj wartości na słupkach
        for bar, value in zip(bars2, speeds):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'{value:.2f}', ha='center', va='bottom', fontsize=9)
        
        # Długość korka
        jam_lengths = [results[var]['traffic_jam_length'] for var in available_variants]
        bars3 = ax3.bar(labels, jam_lengths, color=bar_colors[:n_variants])
        ax3.set_ylabel('Długość [km]')
        ax3.set_title('Długość korka')
        ax3.tick_params(axis='x', rotation=45)
        
        # Dodaj wartości na słupkach
        for bar, value in zip(bars3, jam_lengths):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'{value:.3f}', ha='center', va='bottom', fontsize=9)
        
        # Czas postoju
        waiting_times = [results[var]['avg_waiting_time'] for var in available_variants]
        bars4 = ax4.bar(labels, waiting_times, color=bar_colors[:n_variants])
        ax4.set_ylabel('Czas [s]')
        ax4.set_title('Średni czas postoju')
        ax4.tick_params(axis='x', rotation=45)
        
        # Dodaj wartości na słupkach
        for bar, value in zip(bars4, waiting_times):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'{value:.0f}s', ha='center', va='bottom', fontsize=9)
        
        # Liczba pojazdów obsłużonych
        total_vehicles = [results[var]['total_vehicles'] for var in available_variants]
        bars5 = ax5.bar(labels, total_vehicles, color=bar_colors[:n_variants])
        ax5.set_ylabel('Liczba pojazdów')
        ax5.set_title('Łączna liczba obsłużonych pojazdów')
        ax5.tick_params(axis='x', rotation=45)
        
        # Dodaj wartości na słupkach
        for bar, value in zip(bars5, total_vehicles):
            height = bar.get_height()
            ax5.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'{value}', ha='center', va='bottom', fontsize=9)
        
        # Efektywność buspasa (tylko dla wariantów z buspasem)
        bus_variants = [var for var in available_variants if results[var]['bus_efficiency'] > 0]
        if bus_variants:
            bus_labels = [variant_labels.get(var, f'Wariant {var}') for var in bus_variants]
            bus_efficiency = [results[var]['bus_efficiency'] for var in bus_variants]
            bus_colors = [bar_colors[available_variants.index(var)] for var in bus_variants]
            
            bars6 = ax6.bar(bus_labels, bus_efficiency, color=bus_colors)
            ax6.set_ylabel('Efektywność [%]')
            ax6.set_title('Efektywność buspasa')
            ax6.tick_params(axis='x', rotation=45)
            
            # Dodaj wartości na słupkach
            for bar, value in zip(bars6, bus_efficiency):
                height = bar.get_height()
                ax6.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                        f'{value:.1f}%', ha='center', va='bottom', fontsize=9)
        else:
            # Jeśli brak wariantów z buspasem, ukryj ten subplot
            ax6.text(0.5, 0.5, 'Brak wariantów\nz buspasem', 
                    ha='center', va='center', transform=ax6.transAxes, 
                    fontsize=12, style='italic')
            ax6.set_xticks([])
            ax6.set_yticks([])
        
        plt.tight_layout()
        
        # Generuj nazwę pliku z sufiksem
        filename = f'{os.getcwd()}problem_jagodzinski_{filename_suffix}.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        
        print(f"\nWykres dla {n_variants} wariantów zapisano jako: problem_jagodzinski_{filename_suffix}.png")
        
    except ImportError:
        print("Matplotlib nie jest dostępny - pomijam tworzenie wykresów")

if __name__ == "__main__":
    # Ustawienie seed dla powtarzalności wyników
    np.random.seed(42)
    random.seed(42)
    
    print("="*60)
    print("SYSTEM SYMULACJI PROBLEMU JAGODZIŃSKIEGO")
    print("="*60)
    print("Wybierz rodzaj symulacji:")
    print("1. Porównanie wszystkich wariantów (domyślne)")
    print("2. Test niestandardowej konfiguracji")
    print("3. Test bezpośredniego podejścia z parametrami")
    print("4. Wszystkie powyższe")
    
    try:
        choice = input("\nWybór (1-4, Enter = 1): ").strip()
        if not choice:
            choice = "1"
    except:
        choice = "1"
    
    if choice == "1":
        # Uruchomienie porównania wariantów
        results = run_comparison_study()
        create_visualization(results, "wszystkie_warianty")
    elif choice == "2":
        # Test konfiguracji niestandardowej
        results = test_custom_configuration()
    elif choice == "3":
        # Test bezpośredniego podejścia
        results = test_direct_parameter_approach()
    elif choice == "4":
        # Wszystkie testy
        print("\n" + "="*40)
        print("CZĘŚĆ 1: PORÓWNANIE WARIANTÓW")
        print("="*40)
        results = run_comparison_study()
        create_visualization(results, "wszystkie_warianty")
        
        print("\n" + "="*40)
        print("CZĘŚĆ 2: TEST KONFIGURACJI NIESTANDARDOWEJ")
        print("="*40)
        custom_results = test_custom_configuration()
        
        print("\n" + "="*40)
        print("CZĘŚĆ 3: TEST BEZPOŚREDNIEGO PODEJŚCIA")
        print("="*40)
        direct_results = test_direct_parameter_approach()
    else:
        print("Nieprawidłowy wybór, uruchamiam porównanie wariantów...")
        results = run_comparison_study()
        create_visualization(results, "wszystkie_warianty")
    
    print("\n" + "="*60)
    print("SYMULACJA ZAKOŃCZONA")
    print("="*60)

# ========================================================================================
# DOKUMENTACJA UŻYCIA UOGÓLNIONEJ SYMULACJI Z PARAMETRAMI
# ========================================================================================
"""
GŁÓWNA KONCEPCJA:
Metoda _setup_infrastructure() jest teraz w pełni sparametryzowana i przyjmuje argumenty:
- num_lanes: liczba pasów regularnych
- has_bus_lane: czy istnieje buspas
- bus_lane_capacity: pojemność buspasa 
- traffic_light_positions: pozycje sygnalizacji
- green_ratio: procent czasu na zielonym świetle

DEFINICJE WARIANTÓW ZNAJDUJĄ SIĘ POZA KLASĄ w funkcjach:
- get_variant_a_parameters() - wariant A
- get_variant_b_parameters() - wariant B  
- get_variant_c_parameters() - wariant C (zoptymalizowany)
- get_variant_d_parameters() - wariant D (intensywny ruch)
- get_default_parameters() - domyślna konfiguracja

PRZYKŁADY UŻYCIA:

1. BEZPOŚREDNIE WYWOŁANIE Z PARAMETRAMI:
   
   params = SimulationParameters()
   
   # Definicja wariantu poza klasą
   my_variant = {
       'num_lanes': 4,
       'has_bus_lane': True,
       'bus_lane_capacity': 100,
       'traffic_light_positions': [1.0, 3.0],
       'green_ratio': 0.7
   }
   
   # Utworzenie symulacji z tymi parametrami
   sim = create_simulation_with_parameters(params, my_variant)
   results = sim.run_simulation()

2. UŻYWANIE PREDEFINIOWANYCH WARIANTÓW:
   
   params = SimulationParameters()
   
   # Pobranie parametrów wariantu
   variant_c_params = get_variant_c_parameters(params)
   
   # Opcjonalna modyfikacja
   variant_c_params['num_lanes'] = 5  # zwiększ liczbę pasów
   
   # Użycie
   sim = create_simulation_with_parameters(params, variant_c_params)

3. PORÓWNANIE WŁASNYCH WARIANTÓW:
   
   params = SimulationParameters()
   
   # Definicje wariantów
   variants = {
       'Mały ruch': {
           'num_lanes': 2, 'has_bus_lane': False, 'bus_lane_capacity': 0,
           'traffic_light_positions': [2.5], 'green_ratio': 0.6
       },
       'Duży ruch': {
           'num_lanes': 4, 'has_bus_lane': True, 'bus_lane_capacity': 75,
           'traffic_light_positions': [1.0, 2.0, 3.0, 4.0], 'green_ratio': 0.8
       }
   }
   
   # Porównanie
   results = {}
   for name, variant_params in variants.items():
       sim = create_simulation_with_parameters(params, variant_params)
       results[name] = sim.run_simulation()

4. TESTOWANIE JEDNEGO PARAMETRU:
   
   # Test wpływu liczby pasów
   base_params = get_variant_a_parameters(params)
   
   for lanes in [2, 3, 4, 5]:
       test_params = base_params.copy()
       test_params['num_lanes'] = lanes
       
       sim = create_simulation_with_parameters(params, test_params)
       result = sim.run_simulation()
       print(f"{lanes} pasów: {result['avg_travel_time']:.1f}s")

ZALETY TEGO PODEJŚCIA:
✅ Metoda _setup_infrastructure() jest czysto funkcyjna
✅ Definicje wariantów są poza klasą - łatwe do zarządzania
✅ Łatwe dodawanie nowych wariantów bez modyfikacji klasy
✅ Bezpośrednia kontrola nad każdym parametrem
✅ Możliwość dynamicznego tworzenia wariantów
✅ Łatwe testowanie wpływu pojedynczych parametrów

STRUKTURA PARAMETRÓW:
{
    'num_lanes': int,              # 1-10 (liczba pasów regularnych)
    'has_bus_lane': bool,          # czy ma buspas
    'bus_lane_capacity': int,      # 0-200 (pojemność buspasa)
    'traffic_light_positions': List[float],  # pozycje w km
    'green_ratio': float           # 0.0-1.0 (procent zielonego)
}
"""
