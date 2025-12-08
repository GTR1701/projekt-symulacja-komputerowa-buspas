#!/usr/bin/env python3
"""
Tester scenariuszy z samymi autobusami (100%)
============================================

Ten plik testuje przypadki trywialne gdy mamy 100% autobusów:
1. Test równoważności: 1 pas zwykły vs 1 buspas przy samych autobusach
2. Porównanie różnych konfiguracji infrastruktury z samymi autobusami

Autor: System modularnej symulacji ruchu
Data: 2025-11-30
"""

import random
import numpy as np
from datetime import datetime
from typing import Dict, Any, Optional
import time
import os

from simulation import (
    SimulationParameters, 
    TrafficSimulation,
    VehicleType,
    create_simulation_with_parameters
)


class AllBusTester:
    """Klasa do testowania przypadków z samymi autobusami (100%)"""
    
    def __init__(self, base_seed: int = 42):
        """
        Inicjalizacja testera
        
        Args:
            base_seed: bazowy seed dla generatora losowego (zapewnia powtarzalność)
        """
        self.base_seed = base_seed
        self.results = {}
        self.test_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        random.seed(base_seed)
        np.random.seed(base_seed)
        
        print(f"TESTER SCENARIUSZY Z SAMYMI AUTOBUSAMI")
        print(f"Timestamp: {self.test_timestamp}")
        print(f"Seed: {base_seed}")
        print("="*60)
    
    def get_all_bus_simulation_params(self) -> SimulationParameters:
        """Zwraca parametry symulacji z 100% autobusów"""
        return SimulationParameters(
            road_length=5.0,
            simulation_duration=450.0,
            lane_capacity=100,
            privileged_percentage=1.0,
            traffic_intensity_range=(1800, 3600),
            turning_percentage_range=(0.10, 0.15),
            green_light_range=(50.0, 70.0),
            side_road_positions=[1.0, 2.5, 4.0]
        )
    
    def get_high_traffic_simulation_params(self) -> SimulationParameters:
        """Zwraca parametry symulacji z wysoką intensywnością ruchu"""
        return SimulationParameters(
            road_length=5.0,
            simulation_duration=600.0,  # dłuższy czas dla większej reprezentatywności
            lane_capacity=150,
            privileged_percentage=0.15,  # 15% autobusów domyślnie
            traffic_intensity_range=(3600, 5400),  # wysoka intensywność
            turning_percentage_range=(0.10, 0.20),
            green_light_range=(45.0, 65.0),
            side_road_positions=[1.0, 2.5, 4.0]
        )
    
    def test_all_bus_scenarios(self) -> Dict[str, Any]:
        """
        Testuje różne konfiguracje infrastruktury z 100% autobusów
        """
        print("\nTESTOWANIE SCENARIUSZY Z 100% AUTOBUSÓW")
        print("-"*60)
        
        params = self.get_all_bus_simulation_params()
        results = {}
        
        bus_configs = [
            ('no_buslane', 'Same autobusy bez buspasa', {
                'num_lanes': 3, 'has_bus_lane': False, 'bus_lane_capacity': 0,
                'traffic_light_positions': [1.0, 2.5, 4.0], 'green_ratio': 0.6
            }),
            ('with_buslane', 'Same autobusy z buspassem', {
                'num_lanes': 2, 'has_bus_lane': True, 'bus_lane_capacity': 100,
                'traffic_light_positions': [1.0, 2.5, 4.0], 'green_ratio': 0.6
            }),
            ('big_buslane', 'Same autobusy z dużym buspassem', {
                'num_lanes': 1, 'has_bus_lane': True, 'bus_lane_capacity': 200,
                'traffic_light_positions': [2.5], 'green_ratio': 0.8
            })
        ]
        
        for config_name, config_desc, config_params in bus_configs:
            print(f"\n   {config_desc}")
            random.seed(self.base_seed)
            np.random.seed(self.base_seed)
            
            try:
                sim = create_simulation_with_parameters(params, config_params)
                raw_results = sim.run_simulation(save_data=True, data_filename=f"all_bus_{config_name}_{self.test_timestamp}")
                sim_results = self._calculate_statistics_from_simulation(sim)
                sim_results['config_name'] = config_name
                sim_results['config_description'] = config_desc
                sim_results['raw_data'] = raw_results
                
                results[config_name] = sim_results
                
                print(f"      Pojazdy: {sim_results['total_vehicles']} (100% autobusów)")
                print(f"      Czas przejazdu: {sim_results['avg_travel_time']:.1f}s")
                print(f"      Prędkość: {sim_results['avg_speed']:.1f} km/h")
                print(f"      Efektywność: {sim_results.get('bus_efficiency', 0):.1f}%")
                
            except Exception as e:
                print(f"      Błąd: {e}")
                results[config_name] = {'error': str(e)}
        
        self.results['all_bus_scenarios'] = results
        return results
    
    def test_equivalence(self) -> Dict[str, Any]:
        """
        Test równoważności: 1 pas zwykły vs 1 buspas przy 100% autobusów
        """
        print(f"\nTEST RÓWNOWAŻNOŚCI: 1 pas zwykły vs 1 buspas (100% autobusów)")
        print("-"*60)
        
        equivalence_params = SimulationParameters(
            road_length=5.0,
            simulation_duration=400.0,
            lane_capacity=75,
            privileged_percentage=1.0,
            traffic_intensity_range=(1800, 1800),
            turning_percentage_range=(0.0, 0.0),
            green_light_range=(70.0, 70.0),
            side_road_positions=[2.5]
        )
        
        results = {}
        
        print(f"\n   1 pas zwykły + 100% autobusów")
        random.seed(self.base_seed)
        np.random.seed(self.base_seed)
        
        regular_lane_config = {
            'num_lanes': 1,
            'has_bus_lane': False,
            'bus_lane_capacity': 0,
            'traffic_light_positions': [2.5],
            'green_ratio': 0.8
        }
        
        try:
            sim = create_simulation_with_parameters(equivalence_params, regular_lane_config)
            raw_results = sim.run_simulation(save_data=True, data_filename=f"equivalence_regular_lane_{self.test_timestamp}")
            sim_results_regular = self._calculate_statistics_from_simulation(sim)
            sim_results_regular['config_name'] = 'regular_lane'
            sim_results_regular['raw_data'] = raw_results
            
            results['regular_lane'] = sim_results_regular
            
            print(f"      Pojazdy: {sim_results_regular['total_vehicles']}")
            print(f"      Czas przejazdu: {sim_results_regular['avg_travel_time']:.1f}s")
            print(f"      Prędkość: {sim_results_regular['avg_speed']:.1f} km/h")
            
        except Exception as e:
            print(f"      Błąd: {e}")
            results['regular_lane'] = {'error': str(e)}
        
        print(f"\n   1 buspas + 100% autobusów")
        random.seed(self.base_seed)
        np.random.seed(self.base_seed)
        
        bus_lane_config = {
            'num_lanes': 0,
            'has_bus_lane': True,
            'bus_lane_capacity': 75,
            'traffic_light_positions': [2.5],
            'green_ratio': 0.8
        }
        
        try:
            sim = create_simulation_with_parameters(equivalence_params, bus_lane_config)
            raw_results = sim.run_simulation(save_data=True, data_filename=f"equivalence_bus_lane_{self.test_timestamp}")
            sim_results_bus = self._calculate_statistics_from_simulation(sim)
            sim_results_bus['config_name'] = 'bus_lane'
            sim_results_bus['raw_data'] = raw_results
            
            results['bus_lane'] = sim_results_bus
            
            print(f"      Pojazdy: {sim_results_bus['total_vehicles']}")
            print(f"      Czas przejazdu: {sim_results_bus['avg_travel_time']:.1f}s")
            print(f"      Prędkość: {sim_results_bus['avg_speed']:.1f} km/h")
            
        except Exception as e:
            print(f"      Błąd: {e}")
            results['bus_lane'] = {'error': str(e)}
        
        if ('regular_lane' in results and 'bus_lane' in results and
            'error' not in results['regular_lane'] and 'error' not in results['bus_lane']):
            
            time_regular = results['regular_lane']['avg_travel_time']
            time_bus = results['bus_lane']['avg_travel_time']
            speed_regular = results['regular_lane']['avg_speed']
            speed_bus = results['bus_lane']['avg_speed']
            
            print(f"\n   PORÓWNANIE:")
            print(f"      1 pas zwykły:  {time_regular:.1f}s, {speed_regular:.1f} km/h")
            print(f"      1 buspas:      {time_bus:.1f}s, {speed_bus:.1f} km/h")
            
            time_regular_f = float(time_regular)
            time_bus_f = float(time_bus)
            
            time_diff = abs(time_regular_f - time_bus_f)
            time_percent = (time_diff / min(time_regular_f, time_bus_f)) * 100 if min(time_regular_f, time_bus_f) > 0 else 0
            
            if time_percent < 5.0:
                print(f"      RÓWNOWAŻNOŚĆ POTWIERDZONA! (różnica {time_percent:.1f}%)")
            else:
                print(f"      BRAK RÓWNOWAŻNOŚCI! (różnica: {time_percent:.1f}%)")
                if time_regular_f < time_bus_f:
                    print(f"      Pas zwykły szybszy o {((time_bus_f - time_regular_f) / time_regular_f) * 100:.1f}%")
                else:
                    print(f"      Buspas szybszy o {((time_regular_f - time_bus_f) / time_bus_f) * 100:.1f}%")
        
        self.results['equivalence'] = results
        return results
    
    def test_high_traffic_cases(self) -> Dict[str, Any]:
        """Testuje przypadki trywialne z dużą intensywnością ruchu dla większej reprezentatywności"""
        print("\nTESTOWANIE PRZYPADKÓW TRYWIALNYCH - WYSOKA INTENSYWNOŚĆ RUCHU")
        print("-"*80)
        
        high_traffic_params = self.get_high_traffic_simulation_params()
        results = {}
        
        print(f"\nPARAMETRY WYSOKIEJ INTENSYWNOŚCI:")
        print(f"   Czas symulacji: {high_traffic_params.simulation_duration}s ({high_traffic_params.simulation_duration/60:.1f} min)")
        print(f"   Intensywność: {high_traffic_params.traffic_intensity_range} pojazdów/h")
        avg_intensity = sum(high_traffic_params.traffic_intensity_range) / 2
        expected_vehicles = (avg_intensity / 3600) * high_traffic_params.simulation_duration
        print(f"   Oczekiwana liczba pojazdów: ~{expected_vehicles:.0f} pojazdów")
        
        print(f"\nPRZYPADEK WYSOKIEGO RUCHU: Test równoważności (100% autobusów)")
        print("Sprawdzenie z dużą liczbą pojazdów: 1 pas zwykły vs 1 buspas")
        print("-"*40)
        
        all_bus_high_traffic = high_traffic_params
        all_bus_high_traffic.privileged_percentage = 1.0
        
        print(f"\n   1 pas zwykły + wysokii ruch + 100% autobusów")
        random.seed(self.base_seed)
        np.random.seed(self.base_seed)
        
        regular_lane_high_config = {
            'num_lanes': 1,
            'has_bus_lane': False,
            'bus_lane_capacity': 0,
            'traffic_light_positions': [2.5],
            'green_ratio': 0.6
        }
        
        try:
            sim = create_simulation_with_parameters(all_bus_high_traffic, regular_lane_high_config)
            raw_results = sim.run_simulation(save_data=True, data_filename=f"test_high_traffic_regular_lane_{self.test_timestamp}")
            sim_results_regular_high = self._calculate_statistics_from_simulation(sim)
            sim_results_regular_high['config_name'] = 'high_traffic_regular_lane'
            sim_results_regular_high['config_description'] = '1 pas zwykły + wysoki ruch + 100% autobusów'
            sim_results_regular_high['test_case'] = 'test wysokiego ruchu'
            sim_results_regular_high['raw_data'] = raw_results
            
            results['high_traffic_regular_lane'] = sim_results_regular_high
            
            print(f"      Pojazdy: {sim_results_regular_high['total_vehicles']}")
            print(f"      Czas przejazdu: {sim_results_regular_high['avg_travel_time']:.1f}s")
            print(f"      Prędkość: {sim_results_regular_high['avg_speed']:.1f} km/h")
            
        except Exception as e:
            print(f"      Błąd: {e}")
            results['high_traffic_regular_lane'] = {'error': str(e)}
        
        print(f"\n   1 buspas + wysoki ruch + 100% autobusów")
        random.seed(self.base_seed)
        np.random.seed(self.base_seed)
        
        bus_lane_high_config = {
            'num_lanes': 0,
            'has_bus_lane': True,
            'bus_lane_capacity': 150,
            'traffic_light_positions': [2.5],
            'green_ratio': 0.6
        }
        
        try:
            sim = create_simulation_with_parameters(all_bus_high_traffic, bus_lane_high_config)
            raw_results = sim.run_simulation(save_data=True, data_filename=f"test_high_traffic_bus_lane_{self.test_timestamp}")
            sim_results_bus_high = self._calculate_statistics_from_simulation(sim)
            sim_results_bus_high['config_name'] = 'high_traffic_bus_lane'
            sim_results_bus_high['config_description'] = '1 buspas + wysoki ruch + 100% autobusów'
            sim_results_bus_high['test_case'] = 'test wysokiego ruchu'
            sim_results_bus_high['raw_data'] = raw_results
            
            results['high_traffic_bus_lane'] = sim_results_bus_high
            
            print(f"      Pojazdy: {sim_results_bus_high['total_vehicles']}")
            print(f"      Czas przejazdu: {sim_results_bus_high['avg_travel_time']:.1f}s")
            print(f"      Prędkość: {sim_results_bus_high['avg_speed']:.1f} km/h")
            
        except Exception as e:
            print(f"      Błąd: {e}")
            results['high_traffic_bus_lane'] = {'error': str(e)}
        
        if ('high_traffic_regular_lane' in results and 'high_traffic_bus_lane' in results and
            'error' not in results['high_traffic_regular_lane'] and 'error' not in results['high_traffic_bus_lane']):
            
            reg_vehicles = results['high_traffic_regular_lane']['total_vehicles']
            bus_vehicles = results['high_traffic_bus_lane']['total_vehicles']
            reg_time = results['high_traffic_regular_lane']['avg_travel_time']
            bus_time = results['high_traffic_bus_lane']['avg_travel_time']
            reg_speed = results['high_traffic_regular_lane']['avg_speed']
            bus_speed = results['high_traffic_bus_lane']['avg_speed']
            
            print(f"\n   PORÓWNANIE WYSOKIEGO RUCHU:")
            print(f"      1 pas zwykły:  {reg_vehicles} pojazdów, {reg_time:.1f}s, {reg_speed:.1f} km/h")
            print(f"      1 buspas:      {bus_vehicles} pojazdów, {bus_time:.1f}s, {bus_speed:.1f} km/h")
            
            if reg_vehicles > 0 and bus_vehicles > 0:
                vehicles_diff_pct = abs(reg_vehicles - bus_vehicles) / max(reg_vehicles, bus_vehicles) * 100
                time_diff_pct = abs(reg_time - bus_time) / max(reg_time, bus_time) * 100
                
                print(f"      Różnica pojazdów: {vehicles_diff_pct:.1f}%")
                print(f"      Różnica czasu: {time_diff_pct:.1f}%")
                
                if vehicles_diff_pct < 10 and time_diff_pct < 15:
                    print(f"      RÓWNOWAŻNOŚĆ przy wysokim ruchu POTWIERDZONA!")
                else:
                    print(f"      BRAK RÓWNOWAŻNOŚCI przy wysokim ruchu!")
                    if reg_time < bus_time:
                        print(f"      Pas zwykły efektywniejszy o {((bus_time - reg_time) / bus_time * 100):.1f}%")
                    else:
                        print(f"      Buspas efektywniejszy o {((reg_time - bus_time) / reg_time * 100):.1f}%")
            else:
                print(f"      Brak pojazdów w jednej z konfiguracji - nie można porównać")
        
        print(f"\nPRZYPADEK MIESZANEGO RUCHU: 15% autobusów + wysoka intensywność")
        print("-"*40)
        
        mixed_traffic_params = self.get_high_traffic_simulation_params()  # 15% autobusów domyślnie
        
        mixed_configs = [
            ('mixed_no_bus', 'Wysoki ruch bez buspasa', {
                'num_lanes': 3, 'has_bus_lane': False, 'bus_lane_capacity': 0,
                'traffic_light_positions': [1.5, 3.0], 'green_ratio': 0.7
            }),
            ('mixed_with_bus', 'Wysoki ruch z buspassem', {
                'num_lanes': 2, 'has_bus_lane': True, 'bus_lane_capacity': 150,
                'traffic_light_positions': [1.5, 3.0], 'green_ratio': 0.7
            })
        ]
        
        for config_name, config_desc, config_params in mixed_configs:
            print(f"\n   {config_desc}")
            random.seed(self.base_seed)
            np.random.seed(self.base_seed)
            
            try:
                sim = create_simulation_with_parameters(mixed_traffic_params, config_params)
                raw_results = sim.run_simulation(save_data=True, data_filename=f"test_high_traffic_{config_name}_{self.test_timestamp}")
                sim_results = self._calculate_statistics_from_simulation(sim)
                sim_results['config_name'] = config_name
                sim_results['config_description'] = config_desc
                sim_results['test_case'] = 'wysokii ruch mieszany'
                sim_results['raw_data'] = raw_results
                
                results[f'high_traffic_{config_name}'] = sim_results
                
                print(f"      Pojazdy: {sim_results['total_vehicles']}")
                print(f"      Czas przejazdu: {sim_results['avg_travel_time']:.1f}s")
                print(f"      Prędkość: {sim_results['avg_speed']:.1f} km/h")
                print(f"      Efektywność buspasa: {sim_results.get('bus_efficiency', 0):.1f}%")
                
            except Exception as e:
                print(f"      Błąd: {e}")
                results[f'high_traffic_{config_name}'] = {'error': str(e)}
        
        self.results['high_traffic_cases'] = results
        return results
    
    def _calculate_statistics_from_simulation(self, sim: TrafficSimulation) -> Dict[str, Any]:
        """
        Oblicza statystyki z obiektu symulacji (zastępuje brakującą funkcjonalność)
        
        Args:
            sim: obiekt TrafficSimulation po wykonaniu run_simulation()
            
        Returns:
            Słownik ze statystykami symulacji
        """
        total_generated_vehicles = len(sim.completed_vehicles) + len(sim.vehicles) + len(sim.vehicle_queue)
        
        if not sim.completed_vehicles:
            return {
                'total_vehicles': total_generated_vehicles,
                'completed_vehicles': 0,
                'vehicles_in_motion': len(sim.vehicles),
                'vehicles_in_queue': len(sim.vehicle_queue),
                'avg_travel_time': 0.0,
                'avg_speed': 0.0,
                'avg_waiting_time': 0.0,
                'traffic_jam_length': 0.0,
                'bus_efficiency': 0.0
            }
        
        travel_times = [v.travel_time for v in sim.completed_vehicles if v.travel_time > 0]
        waiting_times = [v.waiting_time for v in sim.completed_vehicles]
        speeds = []
        
        for vehicle in sim.completed_vehicles:
            if vehicle.travel_time > 0:
                # Prędkość średnia = dystans / czas
                distance = vehicle.turn_position if vehicle.will_turn and vehicle.turn_position else sim.params.road_length
                avg_speed = (distance / vehicle.travel_time) * 3600  # km/h
                speeds.append(avg_speed)
        
        bus_vehicles = [v for v in sim.completed_vehicles 
                       if v.vehicle_type == VehicleType.PRIVILEGED]
        regular_vehicles = [v for v in sim.completed_vehicles 
                          if v.vehicle_type == VehicleType.REGULAR]
        
        bus_efficiency = 0.0
        if bus_vehicles and regular_vehicles and hasattr(sim, 'has_bus_lane') and sim.has_bus_lane:
            avg_bus_time = np.mean([v.travel_time for v in bus_vehicles])
            avg_regular_time = np.mean([v.travel_time for v in regular_vehicles])
            bus_efficiency = max(0.0, (avg_regular_time - avg_bus_time) / avg_regular_time * 100)
        
        traffic_jam_length = 0.0
        if hasattr(sim, 'vehicles') and sim.vehicles:
            jammed_vehicles = []
            for vehicle in sim.vehicles:
                if hasattr(vehicle, 'speed') and vehicle.speed < 5.0:
                    jammed_vehicles.append(vehicle)
            traffic_jam_length = len(jammed_vehicles) * 0.005  # m
        
        # Informacja o pojazdach które nie ukończyły przejazdu
        if len(sim.vehicles) > 0 or len(sim.vehicle_queue) > 0:
            print(f"      UWAGA: {len(sim.vehicles)} pojazdów nadal w ruchu, {len(sim.vehicle_queue)} w kolejce")
        
        return {
            'total_vehicles': total_generated_vehicles,
            'completed_vehicles': len(sim.completed_vehicles),
            'vehicles_in_motion': len(sim.vehicles),
            'vehicles_in_queue': len(sim.vehicle_queue),
            'avg_travel_time': np.mean(travel_times) if travel_times else 0.0,
            'avg_speed': np.mean(speeds) if speeds else 0.0,
            'avg_waiting_time': np.mean(waiting_times) if waiting_times else 0.0,
            'traffic_jam_length': traffic_jam_length,
            'bus_efficiency': bus_efficiency
        }
    
    def analyze_results(self) -> Dict[str, Any]:
        """Analizuje wyniki testów z samymi autobusami"""
        print("\nANALIZA WYNIKÓW")
        print("="*60)
        
        analysis = {}
        
        if 'all_bus_scenarios' in self.results:
            print("\nAnaliza scenariuszy z 100% autobusów:")
            scenarios = self.results['all_bus_scenarios']
            
            valid_scenarios = {k: v for k, v in scenarios.items() if 'error' not in v}
            
            if valid_scenarios:
                best = min(valid_scenarios.items(), key=lambda x: x[1]['avg_travel_time'])
                worst = max(valid_scenarios.items(), key=lambda x: x[1]['avg_travel_time'])
                
                print(f"   Najlepszy: {best[0]} ({best[1]['avg_travel_time']:.1f}s)")
                print(f"   Najgorszy: {worst[0]} ({worst[1]['avg_travel_time']:.1f}s)")
                
                improvement = (worst[1]['avg_travel_time'] - best[1]['avg_travel_time']) / worst[1]['avg_travel_time'] * 100
                print(f"   Poprawa: {improvement:.1f}%")
        
        if 'equivalence' in self.results:
            equiv = self.results['equivalence']
            regular = equiv.get('regular_lane')
            bus = equiv.get('bus_lane')
            
            if regular and bus and 'error' not in regular and 'error' not in bus:
                time_diff = abs(regular['avg_travel_time'] - bus['avg_travel_time'])
                time_percent = (time_diff / min(regular['avg_travel_time'], bus['avg_travel_time'])) * 100
                
                print(f"\n   Test równoważności:")
                print(f"      Różnica czasu: {time_diff:.1f}s ({time_percent:.1f}%)")
                
                if time_percent < 5.0:
                    print(f"      RÓWNOWAŻNOŚĆ POTWIERDZONA!")
                else:
                    print(f"      BRAK RÓWNOWAŻNOŚCI!")
        
        print(f"\nWNIOSKI:")
        print(f"   1. Test weryfikuje zachowanie systemu przy 100% autobusów")
        print(f"   2. Sprawdza równoważność 1 pasa zwykłego vs 1 buspasa")
        print(f"   3. Różne konfiguracje infrastruktury wpływają na wydajność")
        
        self.results['analysis'] = analysis
        return analysis
    
    def save_summary_to_csv(self, filename: Optional[str] = None) -> str:
        """Zapisuje podsumowanie wyników testów do CSV"""
        if filename is None:
            filename = f"all_bus_summary_{self.test_timestamp}.csv"
        
        filepath = os.path.join("simulation_data", filename)
        os.makedirs("simulation_data", exist_ok=True)
        
        summary_rows = []
        
        summary_rows.append({
            'test_type': 'METADATA',
            'config': 'all_bus_tester',
            'timestamp': self.test_timestamp,
            'seed': self.base_seed,
            'vehicles': '',
            'time': '',
            'speed': '',
            'description': 'Test scenariuszy z 100% autobusów'
        })
        
        if 'all_bus_scenarios' in self.results:
            for test_name, data in self.results['all_bus_scenarios'].items():
                if 'error' not in data:
                    vehicles_info = f"{data['total_vehicles']} ({data.get('completed_vehicles', '?')} ukończone)"
                    description = data.get('config_description', '')
                    if data.get('vehicles_in_queue', 0) > 0:
                        description += f" | {data['vehicles_in_queue']} w kolejce"
                    
                    summary_rows.append({
                        'test_type': 'ALL_BUS_SCENARIO',
                        'config': test_name,
                        'timestamp': self.test_timestamp,
                        'seed': self.base_seed,
                        'vehicles': vehicles_info,
                        'time': round(data['avg_travel_time'], 1),
                        'speed': round(data['avg_speed'], 1),
                        'description': description
                        })
        
        if 'equivalence' in self.results:
            for test_name, data in self.results['equivalence'].items():
                if 'error' not in data:
                    vehicles_info = f"{data['total_vehicles']} ({data.get('completed_vehicles', '?')} ukończone)"
                    description = f"{test_name} - test równoważności"
                    if data.get('vehicles_in_queue', 0) > 0:
                        description += f" | {data['vehicles_in_queue']} w kolejce"
                    
                    summary_rows.append({
                        'test_type': 'EQUIVALENCE_TEST',
                        'config': test_name,
                        'timestamp': self.test_timestamp,
                        'seed': self.base_seed,
                        'vehicles': vehicles_info,
                        'time': round(data['avg_travel_time'], 1),
                        'speed': round(data['avg_speed'], 1),
                        'description': description
                    })
        
        if 'high_traffic_cases' in self.results:
            for test_name, data in self.results['high_traffic_cases'].items():
                if 'error' not in data:
                    vehicles_info = f"{data['total_vehicles']} ({data.get('completed_vehicles', '?')} ukończone)"
                    description = data.get('config_description', f"{test_name} - test wysokiego ruchu")
                    if data.get('vehicles_in_queue', 0) > 0:
                        description += f" | {data['vehicles_in_queue']} w kolejce"
                    
                    summary_rows.append({
                        'test_type': 'HIGH_TRAFFIC_TEST',
                        'config': test_name,
                        'timestamp': self.test_timestamp,
                        'seed': self.base_seed,
                        'vehicles': vehicles_info,
                        'time': round(data['avg_travel_time'], 1),
                        'speed': round(data['avg_speed'], 1),
                        'description': description
                    })
        
        import pandas as pd
        df = pd.DataFrame(summary_rows)
        df.to_csv(filepath, index=False)
        
        print(f"\nPodsumowanie zapisane do: {filepath}")
        return filepath
    
    def run_full_test_suite(self) -> Dict[str, Any]:
        """Uruchamia testy z samymi autobusami"""
        print("ROZPOCZĘCIE TESTÓW Z SAMYMI AUTOBUSAMI")
        print("="*60)
        
        start_time = time.time()
        
        self.test_all_bus_scenarios()
        
        self.test_equivalence()
        
        # self.test_high_traffic_cases()  # wyłączone
        
        self.analyze_results()
        
        filepath = self.save_summary_to_csv()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"\nCałkowity czas testów: {total_time:.1f}s")
        print(f"Wyniki w: {filepath}")
        print("\nTESY ZAKOŃCZONE POMYŚLNIE!")
        
        return self.results


def main():
    """Główna funkcja uruchamiająca testy z samymi autobusami"""
    print("ALL BUS TESTER")
    print("=================")
    print("Program testuje scenariusze z 100% autobusów")
    print("Sprawdza równoważność 1 pasa zwykłego vs 1 buspasa")
    print()
    
    try:
        seed_input = input("Podaj seed (Enter = 42): ").strip()
        seed = int(seed_input) if seed_input else 42
        
        tester = AllBusTester(base_seed=seed)
        results = tester.run_full_test_suite()
        
        print(f"\nUruchomić z innym seedem? (t/n)")
        if input().lower() in ['t', 'y', 'tak', 'yes']:
            new_seed_input = input("Nowy seed: ").strip()
            new_seed = int(new_seed_input) if new_seed_input else seed + 1
            
            print(f"\n" + "="*60)
            print(f"POWTÓRKA Z SEEDEM: {new_seed}")
            print("="*60)
            
            tester2 = AllBusTester(base_seed=new_seed)
            results2 = tester2.run_full_test_suite()
            
            print(f"\nPORÓWNANIE SEEDÓW {seed} vs {new_seed}:")
            if ('equivalence' in results and 'equivalence' in results2 and 
                'regular_lane' in results['equivalence'] and 'regular_lane' in results2['equivalence']):
                
                time1 = results['equivalence']['regular_lane']['avg_travel_time']
                time2 = results2['equivalence']['regular_lane']['avg_travel_time']
                
                print(f"Test równoważności - czas pasa zwykłego:")
                print(f"  Seed {seed}: {time1:.1f}s")
                print(f"  Seed {new_seed}: {time2:.1f}s")
                print(f"  Różnica: {abs(time1-time2):.1f}s")
        
    except KeyboardInterrupt:
        print(f"\n\nTest przerwany")
    except Exception as e:
        print(f"\n\nBłąd: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()