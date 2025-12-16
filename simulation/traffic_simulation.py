"""
Main TrafficSimulation class - główna klasa symulacji ruchu drogowego
"""

import numpy as np
import random
import pandas as pd
import time
import os
from datetime import datetime
from typing import List, Dict, Optional, Any

from .vehicle import Vehicle, VehicleType
from .traffic_light import TrafficLight
from .infrastructure_config import InfrastructureConfig
from .simulation_parameters import SimulationParameters, RoadConfiguration
from .variant_configs import (
    get_variant_a_parameters,
    get_variant_b_parameters,
    get_default_parameters
)
from .constants import (
    CAR_TOTAL_SPACE,
    BUS_TOTAL_SPACE,
    JAM_THRESHOLD_DISTANCE,
    DETECTION_DISTANCE,
    BASE_VEHICLE_SPEED,
    SLOW_TRAFFIC_THRESHOLD,
    TRAFFIC_LIGHT_STOPPING_DISTANCE,
    MIN_DENSITY_FACTOR,
    DENSITY_REDUCTION_RATE,
    SECONDS_PER_HOUR,
    DEFAULT_SIDE_ROAD_POSITIONS
)


class TrafficSimulation:
    """Główna klasa symulacji ruchu drogowego"""
    
    def __init__(self, config: RoadConfiguration, params: SimulationParameters, 
                 infrastructure_config: Optional[InfrastructureConfig] = None):
        self.config = config
        self.params = params
        self.current_time = 0.0
        self.infrastructure_config = infrastructure_config
        
        infra_params = self.get_infrastructure_parameters()
        self.setup_infrastructure(**infra_params)
        
        self.vehicles: List[Vehicle] = []
        self.completed_vehicles: List[Vehicle] = []
        self.vehicle_queue: List[Vehicle] = []
        
        self.statistics = {
            'total_vehicles': 0,
            'avg_travel_time': 0.0,
            'avg_speed': 0.0,
            'avg_waiting_time': 0.0,
            'traffic_jam_length': 0.0,
            'bus_efficiency': 0.0
        }
        
        self.simulation_data = {
            'timesteps': [],
            'vehicles_in_motion': [],
            'average_speeds': [],
            'jam_lengths': [],
            'light_states': [],
            'vehicle_details': [],
            'bus_lane_utilization': [],
            'vehicles_in_queue': []
        }
        
        self.next_vehicle_id = 1
        
    def get_infrastructure_parameters(self) -> Dict[str, Any]:
        """Zwraca parametry infrastruktury na podstawie konfiguracji lub wariantu"""
        if self.infrastructure_config is not None:
            return {
                'num_lanes': self.infrastructure_config.num_lanes,
                'has_bus_lane': self.infrastructure_config.has_bus_lane,
                'traffic_light_positions': self.infrastructure_config.traffic_light_positions,
                'green_ratio': self.infrastructure_config.traffic_light_green_ratio,
                'cycle_duration': getattr(self.infrastructure_config, 'cycle_duration', None)
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
        
        if self.has_bus_lane:
            description_parts.append(f"{self.num_lanes} pasy regularne + buspas")
            description_parts.append(f"Pojemność buspasa: {self.bus_lane_capacity} pojazdów")
        else:
            description_parts.append(f"{self.num_lanes} pasów regularnych")
        
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
    
    def get_vehicle_space(self, vehicle: Vehicle) -> float:
        """Zwraca przestrzeń zajmowaną przez pojazd na podstawie jego typu"""
        if vehicle.vehicle_type == VehicleType.PRIVILEGED:
            return BUS_TOTAL_SPACE
        else:
            return CAR_TOTAL_SPACE
    
    def calculate_bus_lane_capacity(self) -> int:
        """Oblicza teoretyczną pojemność buspasa na podstawie długości drogi i wielkości autobusów"""
        if not self.has_bus_lane:
            return 0

        available_length = self.params.road_length

        theoretical_capacity = int(available_length / BUS_TOTAL_SPACE)
        
        return max(1, theoretical_capacity)
    
    @property
    def bus_lane_capacity(self) -> int:
        """Property zwracające dynamicznie obliczaną pojemność buspasa"""
        return self.calculate_bus_lane_capacity()
        
    def setup_infrastructure(self, num_lanes: int, has_bus_lane: bool, 
                             traffic_light_positions: List[float],
                             green_ratio: float = 0.6, cycle_duration: float = None):
        """Konfiguracja infrastruktury na podstawie przekazanych parametrów"""
        self.num_lanes = num_lanes
        self.has_bus_lane = has_bus_lane
        
        actual_cycle = cycle_duration if cycle_duration is not None else self.params.traffic_light_cycle
            
        self.traffic_lights = [
            TrafficLight(
                position=pos,
                cycle_duration=actual_cycle,
                green_duration=actual_cycle * green_ratio,
                current_phase="green",
                phase_start_time=0.0
            )
            for pos in traffic_light_positions
        ]
    
    def generate_traffic_intensity(self):
        """Generuje natężenie ruchu zgodnie z rozkładem Poissona"""
        mean_intensity = np.mean(self.params.traffic_intensity_range)
        return np.random.poisson(mean_intensity / SECONDS_PER_HOUR)
    
    def should_vehicle_turn(self) -> bool:
        """Określa czy pojazd skręci w boczną drogę"""
        turning_rate = random.uniform(*self.params.turning_percentage_range)
        return random.random() < turning_rate
    
    def assign_turn_position(self) -> float:
        """Przypisuje pozycję skrętu pojazdu"""
        positions = self.params.side_road_positions or DEFAULT_SIDE_ROAD_POSITIONS
        return random.choice(positions)
    
    def process_vehicle_queue(self, max_capacity: int):
        """Przetwarza kolejkę pojazdów oczekujących na wjazd"""
        vehicles_to_remove = []
        
        for vehicle in self.vehicle_queue:
            if len(self.vehicles) < max_capacity and self.can_enter_road_segment(vehicle.lane, vehicle):
                vehicle.entry_time = self.current_time
                self.vehicles.append(vehicle)
                self.record_vehicle_data(vehicle, 'entered_from_queue')
                vehicles_to_remove.append(vehicle)
            else:
                break
        
        for vehicle in vehicles_to_remove:
            self.vehicle_queue.remove(vehicle)
    
    def generate_vehicle(self) -> Vehicle:
        """Generuje nowy pojazd"""
        vehicle_type = (VehicleType.PRIVILEGED 
                       if random.random() < self.params.privileged_percentage 
                       else VehicleType.REGULAR)
        
        will_turn = self.should_vehicle_turn()
        turn_position = self.assign_turn_position() if will_turn else None
        
        if vehicle_type == VehicleType.PRIVILEGED and self.has_bus_lane:
            bus_lane_vehicles = [v for v in self.vehicles if v.lane == -1]
            
            if len(bus_lane_vehicles) < self.bus_lane_capacity:
                lane = -1
            elif self.num_lanes > 0:
                lane = random.randint(0, self.num_lanes - 1)
            else:
                raise ValueError(f"BŁĄD: Buspas przepełniony ({len(bus_lane_vehicles)}/{self.bus_lane_capacity}) i brak pasów regularnych")
        elif self.num_lanes > 0:
            lane = random.randint(0, self.num_lanes - 1)
        else:
            raise ValueError(f"BŁĄD INFRASTRUKTURY: Brak pasów regularnych (num_lanes=0), ale pojazd typu {vehicle_type.value} nie może użyć buspasa. "
                           f"W konfiguracji tylko z buspassem wszystkie pojazdy muszą być typu PRIVILEGED (autobusy).")
        
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
    
    def update_traffic_lights(self):
        """Aktualizuje stan sygnalizacji świetlnej"""
        for light in self.traffic_lights:
            time_in_phase = self.current_time - light.phase_start_time
            
            if light.current_phase == "green" and time_in_phase >= light.green_duration:
                light.current_phase = "red"
                light.phase_start_time = self.current_time
            elif light.current_phase == "red" and time_in_phase >= (light.cycle_duration - light.green_duration):
                light.current_phase = "green"
                light.phase_start_time = self.current_time
    
    def calculate_vehicle_speed(self, vehicle: Vehicle) -> float:
        """Oblicza prędkość pojazdu na podstawie warunków ruchu"""
        base_speed = BASE_VEHICLE_SPEED
        
        for light in self.traffic_lights:
            distance_to_light = light.position - vehicle.current_position
            if 0 < distance_to_light < TRAFFIC_LIGHT_STOPPING_DISTANCE and light.current_phase == "red":
                return 0.0
    
        vehicles_ahead = [other_vehicle for other_vehicle in self.vehicles 
                         if other_vehicle.lane == vehicle.lane
                         and other_vehicle.current_position > vehicle.current_position
                         and other_vehicle.current_position - vehicle.current_position < DETECTION_DISTANCE
                         and other_vehicle.id != vehicle.id]
    
        density_factor = max(MIN_DENSITY_FACTOR, 1.0 - len(vehicles_ahead) * DENSITY_REDUCTION_RATE)
        
        return base_speed * density_factor
    
    def can_enter_road_segment(self, lane: int, new_vehicle: Vehicle = None) -> bool:
        """Sprawdza czy pojazd może wjechać na początkowy segment drogi"""
        if not self.traffic_lights:
            first_segment_end = self.params.road_length
        else:
            first_segment_end = min(light.position for light in self.traffic_lights)
        
        vehicles_in_first_segment = [v for v in self.vehicles 
                                   if v.lane == lane 
                                   and v.current_position <= first_segment_end]
        
        required_space = sum(self.get_vehicle_space(v) for v in vehicles_in_first_segment)

        new_vehicle_space = self.get_vehicle_space(new_vehicle) if new_vehicle else CAR_TOTAL_SPACE
        
        available_space = first_segment_end
        
        return required_space + new_vehicle_space <= available_space
    
    def collect_simulation_data(self):
        """Zbiera szczegółowe dane z aktualnego stanu symulacji"""
        self.simulation_data['timesteps'].append(self.current_time)
        self.simulation_data['vehicles_in_motion'].append(len(self.vehicles))
        
        if self.vehicles:
            avg_speed = np.mean([v.speed for v in self.vehicles])
            self.simulation_data['average_speeds'].append(avg_speed)
        else:
            self.simulation_data['average_speeds'].append(0.0)
        
        self.simulation_data['jam_lengths'].append(self.calculate_traffic_jam_length())
        
        light_states = [light.current_phase for light in self.traffic_lights]
        self.simulation_data['light_states'].append(light_states)
        
        if self.has_bus_lane:
            buses_in_lane = len([v for v in self.vehicles if v.lane == -1])
            self.simulation_data['bus_lane_utilization'].append(buses_in_lane)
        else:
            self.simulation_data['bus_lane_utilization'].append(0)
        
        self.simulation_data['vehicles_in_queue'].append(len(self.vehicle_queue))
    
    def record_vehicle_data(self, vehicle: Vehicle, action: str):
        """Zapisuje szczegółowe dane o pojeździe"""
        vehicle_record = {
            'vehicle_id': vehicle.id,
            'timestamp': self.current_time,
            'action': action,
            'vehicle_type': vehicle.vehicle_type.value,
            'lane': vehicle.lane,
            'position': vehicle.current_position,
            'speed': vehicle.speed,
            'travel_time': vehicle.travel_time,
            'waiting_time': vehicle.waiting_time,
            'will_turn': vehicle.will_turn,
            'turn_position': vehicle.turn_position
        }
        self.simulation_data['vehicle_details'].append(vehicle_record)
    
    def move_vehicles(self):
        """Przesuwa pojazdy i aktualizuje ich stan"""
        vehicles_to_remove = []
        
        for vehicle in self.vehicles:
            vehicle.speed = self.calculate_vehicle_speed(vehicle)
            
            if vehicle.speed == 0:
                vehicle.waiting_time += self.params.time_step
            
            distance = vehicle.speed * (self.params.time_step / 3600)
            vehicle.current_position += distance
            
            if (vehicle.will_turn and vehicle.turn_position and 
                vehicle.current_position >= vehicle.turn_position):
                vehicle.travel_time = self.current_time - vehicle.entry_time
                self.record_vehicle_data(vehicle, 'turned')
                self.completed_vehicles.append(vehicle)
                vehicles_to_remove.append(vehicle)
            
            elif vehicle.current_position >= self.params.road_length:
                vehicle.travel_time = self.current_time - vehicle.entry_time
                self.record_vehicle_data(vehicle, 'exited')
                self.completed_vehicles.append(vehicle)
                vehicles_to_remove.append(vehicle)
        
        for vehicle in vehicles_to_remove:
            self.vehicles.remove(vehicle)
    
    def calculate_traffic_jam_length(self) -> float:
        """Oblicza długość korka (pojazdy o prędkości < 10 km/h)"""
        slow_vehicles = [v for v in self.vehicles if v.speed < SLOW_TRAFFIC_THRESHOLD]
        if not slow_vehicles:
            return 0.0

        vehicle_data = [(v.current_position, v) for v in slow_vehicles]
        vehicle_data.sort(key=lambda x: x[0])
        
        max_jam_length = 0.0
        current_jam_length = 0.0
        
        for i, (position, vehicle) in enumerate(vehicle_data):
            vehicle_space = self.get_vehicle_space(vehicle)
            
            if i == 0:
                current_jam_length = vehicle_space
            else:
                prev_position = vehicle_data[i-1][0]
                gap = position - prev_position
                if gap < JAM_THRESHOLD_DISTANCE:
                    current_jam_length += vehicle_space
                else:
                    max_jam_length = max(max_jam_length, current_jam_length)
                    current_jam_length = vehicle_space
        
        return max(max_jam_length, current_jam_length)
    
    def calculate_bus_efficiency(self) -> float:
        """Oblicza efektywność buspasa porównując z podobnym scenariuszem bez buspasa"""
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
        
        time_efficiency = max(0.0, (avg_regular_time - avg_bus_time) / avg_regular_time * 100)
        
        bus_speed = np.mean([v.current_position / max(v.travel_time, 1) * 3600 
                            for v in bus_vehicles if v.travel_time > 0])
        regular_speed = np.mean([v.current_position / max(v.travel_time, 1) * 3600 
                               for v in regular_vehicles if v.travel_time > 0])
        
        speed_efficiency = max(0.0, (bus_speed - regular_speed) / regular_speed * 100) if regular_speed > 0 else 0.0
        
        return float(time_efficiency * 0.7 + speed_efficiency * 0.3)

    def step(self):
        """Wykonuje jeden krok symulacji"""
        max_capacity = self.params.lane_capacity * self.num_lanes
        if self.has_bus_lane:
            max_capacity += self.bus_lane_capacity
        
        if self.num_lanes == 0 and self.has_bus_lane:
            max_capacity = self.bus_lane_capacity
        
        self.process_vehicle_queue(max_capacity)
        vehicles_to_generate = self.generate_traffic_intensity()
        for _ in range(int(vehicles_to_generate)):
            if len(self.vehicles) < max_capacity:
                try:
                    new_vehicle = self.generate_vehicle()
                    
                    if self.can_enter_road_segment(new_vehicle.lane, new_vehicle):
                        self.vehicles.append(new_vehicle)
                        self.record_vehicle_data(new_vehicle, 'entered')
                    else:
                        self.vehicle_queue.append(new_vehicle)
                        self.record_vehicle_data(new_vehicle, 'queued')
                except ValueError as e:
                    break
            else:
                try:
                    new_vehicle = self.generate_vehicle()
                    self.vehicle_queue.append(new_vehicle)
                    self.record_vehicle_data(new_vehicle, 'queued')
                except ValueError as e:
                    print(f"UWAGA: {e}")
                    break
        
        self.update_traffic_lights()
        
        self.move_vehicles()
        
        self.collect_simulation_data()
        
        self.current_time += self.params.time_step

    def run_simulation(self, save_data: bool = False, data_filename: str | None = None) -> Dict:
        """Uruchamia pełną symulację - zwraca tylko surowe dane"""
        config_name = self.config.value if self.config else "CUSTOM"
        print(f"Uruchamianie symulacji - Wariant {config_name}")
        
        config_desc = self.get_configuration_description()
        print(f"Konfiguracja: {config_desc}")
        
        start_time = time.time()
        steps = int(self.params.simulation_duration / self.params.time_step)
        
        for step in range(steps):
            self.step()
            
            if step % (steps // 10) == 0:
                progress = (step / steps) * 100
                queue_info = f" | Kolejka: {len(self.vehicle_queue)}" if self.vehicle_queue else ""
                print(f"Postęp: {progress:.0f}% - Pojazdy w ruchu: {len(self.vehicles)}{queue_info}")
        
        if save_data:
            print("Zapisywanie surowych danych do CSV...")
            self.save_simulation_data_to_csv(data_filename)
        
        execution_time = time.time() - start_time
        print(f"Symulacja zakończona w {execution_time:.2f} sekund")
        
        if len(self.vehicle_queue) > 0:
            print(f"UWAGA: {len(self.vehicle_queue)} pojazdów pozostało w kolejce (nie mogły wjechać na drogę)")
            print(f"   Pojazdy w kolejce wygenerowane w czasie: {[v.entry_time for v in self.vehicle_queue[:5]]}{'...' if len(self.vehicle_queue) > 5 else ''}")
        
        return {
            'completed_vehicles': len(self.completed_vehicles),
            'vehicles_in_simulation': len(self.vehicles),
            'vehicles_in_queue': len(self.vehicle_queue),
            'simulation_time': execution_time,
            'data_points': len(self.simulation_data['timesteps']),
            'config': self.get_configuration_description(),
            'filename': data_filename if save_data else None
        }
    
    def _calculate_final_statistics(self):
        """Oblicza końcowe statystyki symulacji"""
        if not self.completed_vehicles:
            return
        
        travel_times = [v.travel_time for v in self.completed_vehicles]
        waiting_times = [v.waiting_time for v in self.completed_vehicles]
        speeds = []
        
        for vehicle in self.completed_vehicles:
            if vehicle.travel_time > 0:
                distance = vehicle.turn_position if vehicle.will_turn and vehicle.turn_position else self.params.road_length
                avg_speed = (distance / vehicle.travel_time) * 3600
                speeds.append(avg_speed)
        
        self.statistics = {
            'total_vehicles': len(self.completed_vehicles),
            'avg_travel_time': np.mean(travel_times),
            'avg_speed': np.mean(speeds) if speeds else 0.0,
            'avg_waiting_time': np.mean(waiting_times),
            'traffic_jam_length': self.calculate_traffic_jam_length(),
            'bus_efficiency': self.calculate_bus_efficiency()
        }

    def save_simulation_data_to_csv(self, base_filename: str | None = None):
        """Zapisuje surowe dane symulacji do plików CSV"""
        if base_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = f"simulation_raw_{timestamp}"
        
        data_dir = "simulation_data"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        timeseries_data = pd.DataFrame({
            'timestamp': self.simulation_data['timesteps'],
            'vehicles_in_motion': self.simulation_data['vehicles_in_motion'],
            'average_speed': self.simulation_data['average_speeds'],
            'jam_length': self.simulation_data['jam_lengths'],
            'bus_lane_utilization': self.simulation_data['bus_lane_utilization'],
            'vehicles_in_queue': self.simulation_data['vehicles_in_queue']
        })
        timeseries_file = os.path.join(data_dir, f"{base_filename}_timeseries.csv")
        timeseries_data.to_csv(timeseries_file, index=False)
        print(f"Zapisano dane czasowe do: {timeseries_file}")
        
        if self.simulation_data['vehicle_details']:
            vehicle_data = pd.DataFrame(self.simulation_data['vehicle_details'])
            vehicle_file = os.path.join(data_dir, f"{base_filename}_vehicles.csv")
            vehicle_data.to_csv(vehicle_file, index=False)
            print(f"Zapisano dane o pojazdach do: {vehicle_file}")
        
        config_data = pd.DataFrame([{
            'simulation_id': base_filename,
            'num_lanes': self.num_lanes,
            'has_bus_lane': self.has_bus_lane,
            'bus_lane_capacity': self.bus_lane_capacity,
            'traffic_light_positions': str([light.position for light in self.traffic_lights]),
            'green_ratio': self.traffic_lights[0].green_duration / self.traffic_lights[0].cycle_duration if self.traffic_lights else 0,
            'road_length': self.params.road_length,
            'simulation_duration': self.params.simulation_duration,
            'traffic_intensity_min': self.params.traffic_intensity_range[0],
            'traffic_intensity_max': self.params.traffic_intensity_range[1],
            'privileged_percentage': self.params.privileged_percentage,
            'lane_capacity': self.params.lane_capacity,
            'description': self.get_configuration_description(),
            'timestamp': datetime.now()
        }])
        config_file = os.path.join(data_dir, f"{base_filename}_config.csv")
        config_data.to_csv(config_file, index=False)
        print(f"Zapisano konfigurację do: {config_file}")
        
        lane_utilization = self.calculate_lane_utilization()
        if lane_utilization:
            lane_data_rows = []
            
            for lane_id, stats in lane_utilization.items():
                if lane_id != 'summary':
                    lane_data_rows.append({
                        'simulation_id': base_filename,
                        'lane_id': lane_id,
                        'lane_type': stats['lane_type'],
                        'vehicle_count': stats['vehicle_count'],
                        'actual_capacity_per_km': stats['capacity_per_km'],
                        'theoretical_capacity_per_km': stats['theoretical_capacity'],
                        'utilization_percent': stats['utilization_percent'],
                        'timestamp': datetime.now()
                    })
            
            if 'summary' in lane_utilization:
                summary = lane_utilization['summary']
                lane_data_rows.append({
                    'simulation_id': base_filename,
                    'lane_id': 'SUMMARY',
                    'lane_type': 'summary',
                    'vehicle_count': summary['total_vehicles'],
                    'actual_capacity_per_km': summary['avg_capacity_per_regular_lane'],
                    'theoretical_capacity_per_km': self.params.lane_capacity,
                    'utilization_percent': summary['avg_utilization_regular_lanes'],
                    'timestamp': datetime.now()
                })
            
            if lane_data_rows:
                lane_df = pd.DataFrame(lane_data_rows)
                lane_file = os.path.join(data_dir, f"{base_filename}_lane_capacity.csv")
                lane_df.to_csv(lane_file, index=False)
                print(f"Zapisano pojemność pasów do: {lane_file}")
        
        if self.simulation_data['light_states'] and any(self.simulation_data['light_states']):
            lights_data = []
            for i, states in enumerate(self.simulation_data['light_states']):
                for j, state in enumerate(states):
                    lights_data.append({
                        'timestamp': self.simulation_data['timesteps'][i],
                        'light_id': j,
                        'position': self.traffic_lights[j].position if j < len(self.traffic_lights) else None,
                        'state': state
                    })
            
            if lights_data:
                lights_df = pd.DataFrame(lights_data)
                lights_file = os.path.join(data_dir, f"{base_filename}_traffic_lights.csv")
                lights_df.to_csv(lights_file, index=False)
                print(f"Zapisano stan sygnalizacji do: {lights_file}")
        
        return data_dir
    
    def calculate_lane_utilization(self) -> Dict[str, Any]:
        """Oblicza rzeczywiste wykorzystanie każdego pasa na podstawie danych o pojazdach"""
        if not self.simulation_data['vehicle_details']:
            return {}
            
        vehicle_df = pd.DataFrame(self.simulation_data['vehicle_details'])
        
        entered_vehicles = vehicle_df[vehicle_df['action'].isin(['entered', 'entered_from_queue'])]
        
        if len(entered_vehicles) == 0:
            return {}
        
        lane_stats = {}
        
        for lane in range(self.num_lanes):
            lane_vehicles = entered_vehicles[entered_vehicles['lane'] == lane]
            vehicle_count = len(lane_vehicles)
            
            actual_capacity_per_km = vehicle_count / self.params.road_length if self.params.road_length > 0 else 0
            
            utilization_percent = (actual_capacity_per_km / self.params.lane_capacity * 100) if self.params.lane_capacity > 0 else 0
            
            lane_stats[f'lane_{lane}'] = {
                'vehicle_count': vehicle_count,
                'capacity_per_km': round(actual_capacity_per_km, 1),
                'theoretical_capacity': self.params.lane_capacity,
                'utilization_percent': round(utilization_percent, 1),
                'lane_type': 'regular'
            }
        
        if self.has_bus_lane:
            bus_lane_vehicles = entered_vehicles[entered_vehicles['lane'] == -1]
            bus_count = len(bus_lane_vehicles)
            
            bus_capacity_per_km = bus_count / self.params.road_length if self.params.road_length > 0 else 0
            bus_utilization_percent = (bus_capacity_per_km / self.bus_lane_capacity * 100) if self.bus_lane_capacity > 0 else 0
            
            lane_stats['bus_lane'] = {
                'vehicle_count': bus_count,
                'capacity_per_km': round(bus_capacity_per_km, 1),
                'theoretical_capacity': self.bus_lane_capacity,
                'utilization_percent': round(bus_utilization_percent, 1),
                'lane_type': 'bus'
            }
        
        total_vehicles = len(self.completed_vehicles)
        total_regular_lanes = self.num_lanes
        
        if total_regular_lanes > 0:
            regular_lane_vehicles = len(entered_vehicles[entered_vehicles['lane'] >= 0]) if self.has_bus_lane else total_vehicles
            avg_vehicles_per_regular_lane = regular_lane_vehicles / total_regular_lanes
            avg_capacity_per_regular_lane = avg_vehicles_per_regular_lane / self.params.road_length if self.params.road_length > 0 else 0
            avg_utilization_regular = (avg_capacity_per_regular_lane / self.params.lane_capacity * 100) if self.params.lane_capacity > 0 else 0
        else:
            avg_vehicles_per_regular_lane = 0
            avg_capacity_per_regular_lane = 0
            avg_utilization_regular = 0
        
        lane_stats['summary'] = {
            'total_vehicles': total_vehicles,
            'regular_lanes_count': total_regular_lanes,
            'avg_vehicles_per_regular_lane': round(avg_vehicles_per_regular_lane, 1),
            'avg_capacity_per_regular_lane': round(avg_capacity_per_regular_lane, 1),
            'avg_utilization_regular_lanes': round(avg_utilization_regular, 1),
            'has_bus_lane': self.has_bus_lane
        }
        
        return lane_stats