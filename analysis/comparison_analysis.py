"""
Comparison analysis functions for different traffic scenarios
"""

import os
import pandas as pd
import time
import glob
from typing import Dict, Any
from datetime import datetime

from .data_loader import load_raw_simulation_data


def compare_bus_lane_efficiency(save_csv: bool = True) -> Dict[str, Any]:
    """Porównuje efektywność buspasa - analizuje surowe dane z CSV"""
    print("="*60)
    print("ANALIZA PORÓWNAWCZA EFEKTYWNOŚCI BUSPASA")
    print("Analiza surowych danych z plików CSV...")
    print("="*60)
    
    data_dir = "simulation_data"
    if not os.path.exists(data_dir):
        print(f"Brak katalogu {data_dir}. Najpierw uruchom symulacje.")
        return {'results': {}, 'efficiency_metrics': {}, 'comparison_table': None}
    
    scenario_patterns = {
        'A': ['scenario_a_3lanes_no_bus', 'variant_a', '3lanes_no_bus'],
        'B': ['scenario_b_2lanes_plus_bus', 'variant_b', '2lanes_plus_bus'], 
        'C': ['scenario_c_2lanes_no_bus', 'variant_c', '2lanes_no_bus']
    }
    
    results_data = {}
    
    for scenario, patterns in scenario_patterns.items():
        print(f"\nAnalizowanie scenariusza {scenario}...")
        
        found = False
        for pattern in patterns:
            stats = load_raw_simulation_data(data_dir, pattern)
            if stats:
                results_data[scenario] = stats
                print(f"   Załadowano z: {stats['source_file']}")
                found = True
                break
        
        if not found:
            print(f"   UWAGA: Nie znaleziono danych dla scenariusza {scenario}")
    
    if len(results_data) < 3:
        print("Brak wystarczających danych do analizy. Potrzebne są dane dla scenariuszy A, B, C.")
        return {'results': {}, 'efficiency_metrics': {}, 'comparison_table': None}
    
    results_a = results_data.get('A', {})
    results_b = results_data.get('B', {})  
    results_c = results_data.get('C', {})
    
    efficiency_metrics = _analyze_efficiency_metrics(results_a, results_b, results_c)
    
    _display_efficiency_results(results_a, results_b, results_c, efficiency_metrics)
    
    comparison_table = None
    if save_csv:
        comparison_table = _save_efficiency_results(results_a, results_b, results_c, efficiency_metrics)
    
    return {
        'results': {'A': results_a, 'B': results_b, 'C': results_c},
        'efficiency_metrics': efficiency_metrics,
        'comparison_table': comparison_table
    }


def run_comparison_study(simulation_module) -> Dict[str, Any]:
    """Uruchamia porównawczą analizę wszystkich wariantów - analizuje surowe dane z CSV"""
    print("="*60)
    print("SYMULACJA PROBLEMU JAGODZIŃSKIEGO")
    print("Analiza porównawcza wariantów infrastruktury")
    print("Analiza surowych danych z plików CSV...")
    print("="*60)
    
    data_dir = "simulation_data"
    if not os.path.exists(data_dir):
        print(f"Brak katalogu {data_dir}. Najpierw uruchom symulacje.")
        return {}
    
    all_vehicle_files = glob.glob(os.path.join(data_dir, "*_vehicles.csv"))
    if not all_vehicle_files:
        print("Brak plików z danymi pojazdów.")
        return {}
    
    standard_patterns = {
        'A': ['variant_a'],
        'B': ['variant_b'], 
        'C': ['variant_c'],
        'D': ['variant_d']
    }
    
    custom_patterns = []
    for file_path in all_vehicle_files:
        filename = os.path.basename(file_path)
        if 'custom_' in filename:
            pattern = filename.replace('_vehicles.csv', '')
            custom_patterns.append(pattern)
    
    results = {}
    params = simulation_module.SimulationParameters()
    
    if any(any(glob.glob(os.path.join(data_dir, f"*{pattern}*_vehicles.csv")) for pattern in patterns) 
           for patterns in standard_patterns.values()):
        print("\nSTANDARDOWE WARIANTY:")
        print("-" * 60)
        for variant in ['A', 'B', 'C', 'D']:
            config_desc = simulation_module.get_variant_config_description(variant, params)
            print(f"Wariant {variant}: {config_desc}")
        print("-" * 60)
    
    for variant, patterns in standard_patterns.items():
        found = False
        for pattern in patterns:
            stats = load_raw_simulation_data(data_dir, pattern)
            if stats:
                results[variant] = stats
                print(f"\nWariant {variant}: {stats['source_file']}")
                found = True
                break
        
        if not found:
            print(f"\nWariant {variant}: BRAK DANYCH")
    
    if custom_patterns:
        print(f"\nNIESTANDARDOWE SCENARIUSZE:")
        print("-" * 60)
        
        for i, pattern in enumerate(custom_patterns):
            stats = load_raw_simulation_data(data_dir, pattern)
            if stats:
                config_file = os.path.join(data_dir, f"{pattern}_config.csv")
                if os.path.exists(config_file):
                    config_df = pd.read_csv(config_file)
                    config = config_df.iloc[0]
                    
                    num_lanes = config.get('num_lanes') or config.get('lane_count', 'N/A')
                    has_bus = config.get('has_bus_lane', False)
                    traffic_int = config.get('traffic_intensity') or (config.get('traffic_intensity_max', 0) / 1000.0)
                    priv_pct = config.get('privileged_percentage', 'N/A')
                    
                    custom_desc = f"{num_lanes} pasów"
                    if has_bus:
                        custom_desc += " + buspas"
                    
                    if traffic_int and traffic_int != 'N/A':
                        custom_desc += f", int={float(traffic_int):.1f}"
                    
                    if priv_pct != 'N/A':
                        custom_desc += f", bus={int(priv_pct)}%"
                else:
                    custom_desc = "Niestandardowy scenariusz"
                
                variant_key = f"CUSTOM_{i+1}"
                results[variant_key] = stats
                results[variant_key]['description'] = custom_desc
                print(f"Scenariusz {i+1}: {custom_desc} - {stats['source_file']}")
    
    if not results:
        print("Brak danych do analizy.")
        return {}
    
    total_scenarios = len(results)
    standard_count = sum(1 for k in results.keys() if k in ['A', 'B', 'C', 'D'])
    custom_count = total_scenarios - standard_count
    
    print(f"\nPrzeanalizowano {total_scenarios} scenariuszy:")
    print(f"   - Standardowe: {standard_count}")
    print(f"   - Niestandardowe: {custom_count}")
    
    _display_comparison_results(results, params, simulation_module)
    
    return results


def test_custom_configuration(
    simulation_module,
    lane_count: int = 2,
    bus_lane: bool = True,
    traffic_intensity: float = 0.8,
    privileged_percentage: int = 15,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Testuje niestandardową konfigurację symulacji - uruchamia symulację i analizuje surowe dane
    """
    start_time = time.time()
    
    params = simulation_module.SimulationParameters()
    
    params.lane_count = lane_count
    params.bus_lane = bus_lane
    params.traffic_intensity = traffic_intensity
    params.privileged_percentage = privileged_percentage / 100.0  # %
    params.verbosity = 1 if verbose else 0
    
    config_id = f"custom_{lane_count}lanes_{int(bus_lane)}bus_{traffic_intensity:.1f}int_{privileged_percentage}priv"
    
    if verbose:
        print(f"\nTestowanie niestandardowej konfiguracji:")
        print(f"   Liczba pasów: {lane_count}")
        print(f"   Pas autobusowy: {'TAK' if bus_lane else 'NIE'}")
        print(f"   Intensywność ruchu: {traffic_intensity:.1f}")
        print(f"   Pojazdy uprzywilejowane: {privileged_percentage}%")
        print(f"   ID konfiguracji: {config_id}")
    
    try:
        sim_results = simulation_module.run_simulation(params, save_csv=True, save_id=config_id)
        
        if not sim_results or not sim_results.get('success', True):
            print("Symulacja zakończona niepowodzeniem")
            return {}
        
        data_dir = "simulation_data"
        stats = load_raw_simulation_data(data_dir, config_id)
        
        if not stats:
            print("Nie można załadować danych z symulacji")
            return {}
        
        if verbose:
            elapsed = time.time() - start_time
            print(f"\nTest zakończony w {elapsed:.2f}s")
            print(f"Wyniki konfiguracji {config_id}:")
            print(f"   Łączna liczba pojazdów: {stats['total_vehicles']}")
            print(f"   Średni czas podróży: {stats['avg_travel_time']:.2f}s")
            print(f"   Średnia prędkość: {stats['avg_speed']:.2f} m/s")
            print(f"   Średni czas oczekiwania: {stats['avg_waiting_time']:.2f}s")
            print(f"   Długość korka: {stats['traffic_jam_length']:.2f}m")
            
            if stats.get('bus_efficiency') is not None:
                print(f"   Efektywność autobusów: {stats['bus_efficiency']:.1f}%")
        
        return stats
        
    except Exception as e:
        print(f"Błąd podczas testowania konfiguracji: {e}")
        return {}


def test_direct_parameter_approach(simulation_module) -> Dict[str, Any]:
    """Demonstracja bezpośredniego wywołania metody z parametrami"""
    print("="*60)
    print("TEST BEZPOŚREDNIEGO PODEJŚCIA Z PARAMETRAMI")
    print("="*60)
    
    params = simulation_module.SimulationParameters()
    
    print("Testowanie różnych konfiguracji poprzez bezpośrednie parametry...")
    
    print("\n--- Konfiguracja minimalistyczna ---")
    minimal_params = {
        'num_lanes': 1,
        'has_bus_lane': False,
        'bus_lane_capacity': 0,
        'traffic_light_positions': [2.5],
        'green_ratio': 0.5
    }
    
    sim1 = simulation_module.create_simulation_with_parameters(params, minimal_params)
    results1 = sim1.run_simulation()
    print(f"Wynik: {results1['avg_travel_time']:.1f}s średni czas, {results1['avg_speed']:.1f} km/h")
    
    print("\n--- Konfiguracja maksymalna ---")
    maximal_params = {
        'num_lanes': 6,
        'has_bus_lane': True,
        'bus_lane_capacity': params.lane_capacity * 2,
        'traffic_light_positions': [1.0, 2.0, 3.0, 4.0],
        'green_ratio': 0.9
    }
    
    sim2 = simulation_module.create_simulation_with_parameters(params, maximal_params)
    results2 = sim2.run_simulation()
    print(f"Wynik: {results2['avg_travel_time']:.1f}s średni czas, {results2['avg_speed']:.1f} km/h")
    
    print(f"\nPorównanie:")
    print(f"Konfiguracja minimalistyczna: {results1['avg_travel_time']:.1f}s")
    print(f"Konfiguracja maksymalna: {results2['avg_travel_time']:.1f}s")
    improvement = ((results1['avg_travel_time'] - results2['avg_travel_time']) / results1['avg_travel_time'] * 100)
    print(f"Poprawa: {improvement:+.1f}%")
    
    return {'minimal': results1, 'maximal': results2}


def _analyze_efficiency_metrics(results_a: Dict, results_b: Dict, results_c: Dict) -> Dict[str, float]:
    """Analizuje metryki efektywności między scenariuszami"""
    efficiency_metrics = {}
    
    time_improvement_a_b = ((results_a['avg_travel_time'] - results_b['avg_travel_time']) / results_a['avg_travel_time'] * 100)
    efficiency_metrics['time_improvement_a_b'] = time_improvement_a_b
    
    speed_improvement_a_b = ((results_b['avg_speed'] - results_a['avg_speed']) / results_a['avg_speed'] * 100)
    efficiency_metrics['speed_improvement_a_b'] = speed_improvement_a_b
    
    jam_improvement_a_b = ((results_a['traffic_jam_length'] - results_b['traffic_jam_length']) / max(results_a['traffic_jam_length'], 0.001) * 100)
    efficiency_metrics['jam_improvement_a_b'] = jam_improvement_a_b
    
    time_improvement_c_b = ((results_c['avg_travel_time'] - results_b['avg_travel_time']) / results_c['avg_travel_time'] * 100)
    efficiency_metrics['time_improvement_c_b'] = time_improvement_c_b
    
    speed_improvement_c_b = ((results_b['avg_speed'] - results_c['avg_speed']) / results_c['avg_speed'] * 100)
    efficiency_metrics['speed_improvement_c_b'] = speed_improvement_c_b
    
    jam_improvement_c_b = ((results_c['traffic_jam_length'] - results_b['traffic_jam_length']) / max(results_c['traffic_jam_length'], 0.001) * 100)
    efficiency_metrics['jam_improvement_c_b'] = jam_improvement_c_b
    
    if results_b['bus_efficiency'] > 0:
        efficiency_metrics['bus_efficiency'] = results_b['bus_efficiency']
    
    return efficiency_metrics


def _display_efficiency_results(results_a: Dict, results_b: Dict, results_c: Dict, efficiency_metrics: Dict):
    """Wyświetla wyniki analizy efektywności"""
    print("\n" + "="*60)
    print("ANALIZA EFEKTYWNOŚCI BUSPASA")
    print("="*60)
    
    print("\nPORÓWNANIE 1: Podobna przepustowość")
    print("   3 pasy bez buspasa vs 2 pasy + buspas")
    print("-" * 50)
    
    print(f"   Czas przejazdu (A→B): {efficiency_metrics['time_improvement_a_b']:+.1f}%")
    print(f"   Średnia prędkość (A→B): {efficiency_metrics['speed_improvement_a_b']:+.1f}%")
    print(f"   Redukcja korków (A→B): {efficiency_metrics['jam_improvement_a_b']:+.1f}%")
    
    print("\nPORÓWNANIE 2: Wpływ samego buspasa")
    print("   2 pasy bez buspasa vs 2 pasy + buspas")
    print("-" * 50)
    
    print(f"   Czas przejazdu (C→B): {efficiency_metrics['time_improvement_c_b']:+.1f}%")
    print(f"   Średnia prędkość (C→B): {efficiency_metrics['speed_improvement_c_b']:+.1f}%")
    print(f"   Redukcja korków (C→B): {efficiency_metrics['jam_improvement_c_b']:+.1f}%")
    
    if 'bus_efficiency' in efficiency_metrics:
        print(f"   Efektywność buspasa: {efficiency_metrics['bus_efficiency']:.1f}%")
    
    print("\n" + "="*60)
    print("TABELA PORÓWNAWCZA")
    print("="*60)
    
    comparison_data = {
        'Scenariusz': ['A: 3 pasy', 'B: 2 pasy+bus', 'C: 2 pasy'],
        'Czas przejazdu [s]': [
            f"{results_a['avg_travel_time']:.1f}",
            f"{results_b['avg_travel_time']:.1f}",
            f"{results_c['avg_travel_time']:.1f}"
        ],
        'Prędkość [km/h]': [
            f"{results_a['avg_speed']:.1f}",
            f"{results_b['avg_speed']:.1f}",
            f"{results_c['avg_speed']:.1f}"
        ],
        'Długość korka [km]': [
            f"{results_a['traffic_jam_length']:.3f}",
            f"{results_b['traffic_jam_length']:.3f}",
            f"{results_c['traffic_jam_length']:.3f}"
        ],
        'Pojazdy obsłużone': [
            results_a['total_vehicles'],
            results_b['total_vehicles'],
            results_c['total_vehicles']
        ]
    }
    
    df = pd.DataFrame(comparison_data)
    print(df.to_string(index=False))
    
    _display_conclusions(efficiency_metrics)


def _display_conclusions(efficiency_metrics: Dict):
    """Wyświetla wnioski z analizy"""
    print("\n" + "="*60)
    print("WNIOSKI Z ANALIZY")
    print("="*60)
    
    if efficiency_metrics['time_improvement_a_b'] > 0:
        print("Buspas (2P+Bus) jest bardziej efektywny niż poszerzenie drogi (3P)")
    else:
        print("Poszerzenie drogi (3P) jest bardziej efektywne niż buspas (2P+Bus)")
    
    if efficiency_metrics['time_improvement_c_b'] > 0:
        print("Buspas poprawia przepustowość w porównaniu do tej samej liczby pasów")
    else:
        print("Buspas nie poprawia przepustowości")
    
    if efficiency_metrics['jam_improvement_a_b'] > 10:
        print("Buspas znacząco redukuje korki w porównaniu do poszerzenia drogi")
    elif efficiency_metrics['jam_improvement_a_b'] > 0:
        print("Buspas nieznacznie redukuje korki")
    else:
        print("Buspas nie redukuje korków")


def _save_efficiency_results(results_a: Dict, results_b: Dict, results_c: Dict, efficiency_metrics: Dict) -> pd.DataFrame:
    """Zapisuje wyniki efektywności do plików CSV"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    efficiency_df = pd.DataFrame([efficiency_metrics])
    efficiency_df['timestamp'] = timestamp
    efficiency_file = f"simulation_data/bus_efficiency_comparison_{timestamp}.csv"
    efficiency_df.to_csv(efficiency_file, index=False)
    print(f"\nZapisano analizę efektywności do: {efficiency_file}")
    
    comparison_data = {
        'Scenariusz': ['A: 3 pasy', 'B: 2 pasy+bus', 'C: 2 pasy'],
        'Czas przejazdu [s]': [
            f"{results_a['avg_travel_time']:.1f}",
            f"{results_b['avg_travel_time']:.1f}",
            f"{results_c['avg_travel_time']:.1f}"
        ],
        'Prędkość [km/h]': [
            f"{results_a['avg_speed']:.1f}",
            f"{results_b['avg_speed']:.1f}",
            f"{results_c['avg_speed']:.1f}"
        ],
        'Długość korka [km]': [
            f"{results_a['traffic_jam_length']:.3f}",
            f"{results_b['traffic_jam_length']:.3f}",
            f"{results_c['traffic_jam_length']:.3f}"
        ],
        'Pojazdy obsłużone': [
            results_a['total_vehicles'],
            results_b['total_vehicles'],
            results_c['total_vehicles']
        ]
    }
    
    df = pd.DataFrame(comparison_data)
    comparison_file = f"simulation_data/scenario_comparison_{timestamp}.csv"
    df.to_csv(comparison_file, index=False)
    print(f"Zapisano tabelę porównawczą do: {comparison_file}")
    
    return df


def _display_comparison_results(results: Dict[str, Any], params, simulation_module):
    """Wyświetla analizę porównawczą wyników"""
    print("\n" + "="*60)
    print("PODSUMOWANIE WYNIKÓW")
    print("="*60)
    
    available_variants = list(results.keys())
    
    comparison_data = {
        'Wskaźnik': [
            'Łączna liczba pojazdów',
            'Średni czas przejazdu [s]',
            'Średnia prędkość [km/h]',
            'Średni czas postoju [s]',
            'Długość korka [km]',
            'Efektywność buspasa [%]'
        ]
    }
    
    for variant in available_variants:
        if variant.startswith('CUSTOM_'):
            if 'description' in results[variant]:
                column_name = f'{variant}\n({results[variant]["description"]})'
            else:
                column_name = f'{variant}\n(Niestandardowy)'
        else:
            try:
                short_desc = simulation_module.get_variant_short_description(variant, params)
                column_name = f'Wariant {variant}\n({short_desc})'
            except:
                column_name = f'Wariant {variant}'
            
        comparison_data[column_name] = [
            results[variant]['total_vehicles'],
            f"{results[variant]['avg_travel_time']:.1f}",
            f"{results[variant]['avg_speed']:.1f}",
            f"{results[variant]['avg_waiting_time']:.1f}",
            f"{results[variant]['traffic_jam_length']:.2f}",
            f"{results[variant]['bus_efficiency']:.1f}" if results[variant]['bus_efficiency'] > 0 else "N/A"
        ]
    
    df = pd.DataFrame(comparison_data)
    print(df.to_string(index=False))
    
    _display_rankings(results)
    _display_hypotheses_verification(results)
    _display_recommendations(results)


def _display_rankings(results: Dict[str, Any]):
    """Wyświetla rankingi wariantów"""
    print("\n" + "="*60)
    print("RANKING WARIANTÓW")
    print("="*60)
    
    travel_time_ranking = sorted(results.items(), key=lambda x: x[1]['avg_travel_time'])
    print("\nRanking po czasie przejazdu (najlepszy → najgorszy):")
    for i, (variant, data) in enumerate(travel_time_ranking, 1):
        print(f"   {i}. Wariant {variant}: {data['avg_travel_time']:.1f}s")
    
    speed_ranking = sorted(results.items(), key=lambda x: x[1]['avg_speed'], reverse=True)
    print("\nRanking po średniej prędkości (najlepszy → najgorszy):")
    for i, (variant, data) in enumerate(speed_ranking, 1):
        print(f"   {i}. Wariant {variant}: {data['avg_speed']:.1f} km/h")
    
    jam_ranking = sorted(results.items(), key=lambda x: x[1]['traffic_jam_length'])
    print("\nRanking po długości korków (najlepszy → najgorszy):")
    for i, (variant, data) in enumerate(jam_ranking, 1):
        print(f"   {i}. Wariant {variant}: {data['traffic_jam_length']:.2f} km")


def _display_hypotheses_verification(results: Dict[str, Any]):
    """Wyświetla weryfikację hipotez badawczych"""
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


def _display_recommendations(results: Dict[str, Any]):
    """Wyświetla rekomendacje"""
    print("\n" + "="*60)
    print("REKOMENDACJE")
    print("="*60)
    
    travel_time_ranking = sorted(results.items(), key=lambda x: x[1]['avg_travel_time'])
    speed_ranking = sorted(results.items(), key=lambda x: x[1]['avg_speed'], reverse=True)
    jam_ranking = sorted(results.items(), key=lambda x: x[1]['traffic_jam_length'])
    
    best_travel_time = travel_time_ranking[0]
    best_speed = speed_ranking[0]
    best_jam = jam_ranking[0]
    
    print(f"NAJLEPSZY OGÓLNIE: Wariant {best_travel_time[0]} (najkrótszy czas przejazdu)")
    print(f"NAJSZYBSZY: Wariant {best_speed[0]} (najwyższa średnia prędkość)")
    print(f"NAJMNIEJ KORKÓW: Wariant {best_jam[0]} (najkrótsze korki)")
    
    if 'C' in [best_travel_time[0], best_speed[0], best_jam[0]]:
        print("\nKonfiguracja zoptymalizowana (Wariant C) wykazuje najlepsze wyniki!")