#!/usr/bin/env python3
"""
Main entry point for Traffic Simulation - Problem Jagodzińskiego
Autor: Dawid Kowal

Główny punkt wejścia do aplikacji symulacji ruchu drogowego
"""

import numpy as np
import random
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simulation import (
    SimulationParameters, 
    RoadConfiguration, 
    TrafficSimulation,
    TrafficLight,
    get_variant_a_parameters,
    get_variant_b_parameters,
    get_variant_c_parameters,
    get_variant_d_parameters,
    create_simulation_with_parameters
)

import analysis


def main():
    """Główna funkcja programu"""
    np.random.seed(42)
    random.seed(42)
    
    print("="*60)
    print("SYSTEM SYMULACJI PROBLEMU JAGODZIŃSKIEGO")
    print("="*60)
    
    print("Wybierz tryb symulacji:")
    print("1. Tylko predefiniowane scenariusze (A, B, C, D)")
    print("2. Predefiniowane + scenariusz niestandardowy")
    print("3. Tylko scenariusz niestandardowy")
    
    try:
        mode = input("\nWybór (1-3, Enter = 1): ").strip()
        if not mode:
            mode = "1"
    except:
        mode = "1"
    
    params = SimulationParameters()
    
    predefined_variants = {
        'A': ('Wariant A: 3 pasy, bez buspasa', RoadConfiguration.VARIANT_A, None),
        'B': ('Wariant B: 2 pasy + buspas', RoadConfiguration.VARIANT_B, None), 
        'C': ('Wariant C: zoptymalizowany', None, get_variant_c_parameters(params)),
        'D': ('Wariant D: wysokie natężenie', None, get_variant_d_parameters(params))
    }
    
    scenarios_to_run = []
    
    if mode in ["1", "2"]:
        print("\n" + "="*40)
        print("PREDEFINIOWANE SCENARIUSZE")
        print("="*40)
        for variant_id, (description, config, infra_params) in predefined_variants.items():
            scenarios_to_run.append((variant_id, description, config, infra_params, f"variant_{variant_id.lower()}"))
            print(f"{description}")
    
    if mode in ["2", "3"]:
        print("\n" + "="*40)
        print("SCENARIUSZ NIESTANDARDOWY")
        print("="*40)
        
        try:
            print("Wprowadź parametry niestandardowego scenariusza:")
            
            lanes_input = input("Liczba pasów regularnych (min 1, domyślnie 3): ").strip()
            lane_count = int(lanes_input) if lanes_input and lanes_input.isdigit() else 3
            lane_count = max(1, lane_count)
            
            bus_input = input("Czy dodać buspas? (t/N): ").strip().lower()
            has_bus_lane = bus_input in ['t', 'tak', 'y', 'yes', '1']
            
            intensity_input = input("Intensywność ruchu (min 0.1, domyślnie 0.8): ").strip()
            try:
                traffic_intensity = float(intensity_input) if intensity_input else 0.8
                traffic_intensity = max(0.1, traffic_intensity)
            except:
                traffic_intensity = 0.8
            
            bus_percent_input = input("Procent autobusów (0-100, domyślnie 15): ").strip()
            try:
                privileged_percentage = int(bus_percent_input) if bus_percent_input else 15
                privileged_percentage = max(0, min(100, privileged_percentage))
            except:
                privileged_percentage = 15
            
            min_green, max_green = params.green_light_range
            green_input = input(f"Czas zielonego światła w sekundach ({min_green}-{max_green}s, domyślnie 60s): ").strip()
            try:
                green_duration = float(green_input) if green_input else 60.0
                green_duration = max(min_green, min(max_green, green_duration))
                
                cycle_duration = TrafficLight.calculate_optimal_cycle(green_duration)
                green_ratio = green_duration / cycle_duration
                
                print(f"Ustawiono: {green_duration}s zielone, cykl {cycle_duration}s (ratio: {green_ratio:.1%})")
                
            except:
                green_duration = 60.0
                cycle_duration = TrafficLight.calculate_optimal_cycle(green_duration)
                green_ratio = green_duration / cycle_duration
            
            lights_input = input("Liczba sygnalizacji (min 0, domyślnie 3): ").strip()
            try:
                num_lights = int(lights_input) if lights_input else 3
                num_lights = max(0, num_lights)
            except:
                num_lights = 3
            
            if num_lights > 0:
                traffic_light_positions = [i * (5.0 / num_lights) + 0.5 for i in range(num_lights)]
            else:
                traffic_light_positions = []
                
            custom_params = {
                'num_lanes': lane_count + (1 if has_bus_lane else 0),
                'has_bus_lane': has_bus_lane,
                'bus_lane_capacity': params.lane_capacity,
                'traffic_light_positions': traffic_light_positions,
                'green_ratio': green_ratio,
                'cycle_duration': cycle_duration
            }
            
            custom_sim_params = SimulationParameters()
            custom_sim_params.traffic_intensity = traffic_intensity
            custom_sim_params.privileged_percentage = privileged_percentage / 100.0
            custom_sim_params.traffic_light_cycle = cycle_duration
            
            custom_description = f"Niestandardowy: {lane_count}P{'+ buspas' if has_bus_lane else ''}, int={traffic_intensity:.1f}, bus={privileged_percentage}%"
            custom_id = f"custom_{lane_count}l_{int(has_bus_lane)}_i{traffic_intensity:.1f}_b{privileged_percentage}_g{int(green_ratio*cycle_duration)}"
            
            scenarios_to_run.append((
                "CUSTOM", 
                custom_description, 
                None, 
                custom_params,
                custom_id,
                custom_sim_params
            ))
            
            print(f"{custom_description}")
            
        except KeyboardInterrupt:
            print("\nAnulowano wprowadzanie parametrów niestandardowych")
        except Exception as e:
            print(f"Błąd przy wprowadzaniu parametrów: {e}")
    
    print(f"\n" + "="*60)
    print(f"URUCHAMIANIE {len(scenarios_to_run)} SCENARIUSZY")
    print("="*60)
    
    for i, scenario in enumerate(scenarios_to_run, 1):
        if len(scenario) == 5:
            variant_id, description, config, infra_params, filename = scenario
            sim_params = params
        else:
            variant_id, description, config, infra_params, filename, sim_params = scenario
        
        print(f"\nScenariusz {i}/{len(scenarios_to_run)}: {description}")
        
        try:
            if config is not None:
                sim = TrafficSimulation(config, sim_params)
            else:
                sim = create_simulation_with_parameters(sim_params, infra_params)
            
            result = sim.run_simulation(save_data=True, data_filename=filename)
            
            print(f"   Ukończono - zapisano surowe dane jako '{filename}'")
            
        except Exception as e:
            print(f"   Błąd: {e}")
    
    print(f"\nWszystkie symulacje zakończone")
    print(f"Dane zapisane w katalogu: simulation_data/")
    print(f"\nAby przeprowadzić analizę, uruchom:")
    print(f"   python3 analysis_main.py")
    print("="*60)
    print("SYMULACJA ZAKOŃCZONA")
    print("="*60)


if __name__ == "__main__":
    main()