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
        'C': ['scenario_c_3lanes_plus_bus', 'variant_c', '3lanes_plus_bus']
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
    
    print("\nPORÓWNANIE 2: Wpływ dodania buspasa")
    print("   3 pasy + buspas vs 2 pasy + buspas")
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
        'Scenariusz': ['A: 3 pasy', 'B: 2 pasy+bus', 'C: 3 pasy+bus'],
        'Ukończone': [
            results_a['total_vehicles'],
            results_b['total_vehicles'],
            results_c['total_vehicles']
        ],
        'Wjechało': [
            results_a['total_entered'],
            results_b['total_entered'],
            results_c['total_entered']
        ],
        'W kolejce': [
            results_a['vehicles_in_queue'],
            results_b['vehicles_in_queue'],
            results_c['vehicles_in_queue']
        ],
        'W ruchu': [
            results_a['vehicles_in_traffic'],
            results_b['vehicles_in_traffic'],
            results_c['vehicles_in_traffic']
        ],
        'Sukces%': [
            f"{results_a['completion_rate']:.1f}",
            f"{results_b['completion_rate']:.1f}",
            f"{results_c['completion_rate']:.1f}"
        ],
        'Czas[s]': [
            f"{results_a['avg_travel_time']:.1f}",
            f"{results_b['avg_travel_time']:.1f}",
            f"{results_c['avg_travel_time']:.1f}"
        ],
        'Prędkość[km/h]': [
            f"{results_a['avg_speed']:.1f}",
            f"{results_b['avg_speed']:.1f}",
            f"{results_c['avg_speed']:.1f}"
        ],
        'Korek[km]': [
            f"{results_a['traffic_jam_length']:.2f}",
            f"{results_b['traffic_jam_length']:.2f}",
            f"{results_c['traffic_jam_length']:.2f}"
        ],
        'Bus%': [
            'N/A',
            f"{results_b['bus_efficiency']:.1f}" if results_b['bus_efficiency'] > 0 else 'N/A',
            f"{results_c['bus_efficiency']:.1f}" if results_c['bus_efficiency'] > 0 else 'N/A'
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
        print("2 pasy + buspas jest bardziej efektywne niż 3 pasy + buspas")
    else:
        print("3 pasy + buspas jest bardziej efektywne niż 2 pasy + buspas")
    
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
        'Scenariusz': ['A: 3 pasy', 'B: 2 pasy+bus', 'C: 3 pasy+bus'],
        'Ukończone': [
            results_a['total_vehicles'],
            results_b['total_vehicles'],
            results_c['total_vehicles']
        ],
        'Wjechało': [
            results_a['total_entered'],
            results_b['total_entered'],
            results_c['total_entered']
        ],
        'W kolejce': [
            results_a['vehicles_in_queue'],
            results_b['vehicles_in_queue'],
            results_c['vehicles_in_queue']
        ],
        'W ruchu': [
            results_a['vehicles_in_traffic'],
            results_b['vehicles_in_traffic'],
            results_c['vehicles_in_traffic']
        ],
        'Sukces%': [
            f"{results_a['completion_rate']:.1f}",
            f"{results_b['completion_rate']:.1f}",
            f"{results_c['completion_rate']:.1f}"
        ],
        'Czas[s]': [
            f"{results_a['avg_travel_time']:.1f}",
            f"{results_b['avg_travel_time']:.1f}",
            f"{results_c['avg_travel_time']:.1f}"
        ],
        'Prędkość[km/h]': [
            f"{results_a['avg_speed']:.1f}",
            f"{results_b['avg_speed']:.1f}",
            f"{results_c['avg_speed']:.1f}"
        ],
        'Korek[km]': [
            f"{results_a['traffic_jam_length']:.2f}",
            f"{results_b['traffic_jam_length']:.2f}",
            f"{results_c['traffic_jam_length']:.2f}"
        ],
        'Bus%': [
            'N/A',
            f"{results_b['bus_efficiency']:.1f}" if results_b['bus_efficiency'] > 0 else 'N/A',
            f"{results_c['bus_efficiency']:.1f}" if results_c['bus_efficiency'] > 0 else 'N/A'
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
    
    print(f"\n{'Wariant':<12} {'Ukończ.':<7} {'Wjechały':<8} {'W kolejce':<9} {'W ruchu':<8} {'Sukces%':<8} {'Czas[s]':<8} {'Korek[km]':<9} {'Bus%':<6}")
    print("-" * 102)
    
    for variant in available_variants:
        variant_display = variant[:11] if len(variant) > 11 else variant
        
        bus_eff = f"{results[variant]['bus_efficiency']:.1f}" if results[variant]['bus_efficiency'] > 0 else "N/A"
        
        in_queue = results[variant].get('vehicles_in_queue', 0)
        in_traffic = results[variant].get('vehicles_in_traffic', 0)
        
        print(f"{variant_display:<12} "
              f"{results[variant]['total_vehicles']:<7} "
              f"{results[variant].get('total_entered', results[variant]['total_vehicles']):<8} "
              f"{in_queue:<9} "
              f"{in_traffic:<8} "
              f"{results[variant].get('completion_rate', 100.0):<8.1f} "
              f"{results[variant]['avg_travel_time']:<8.1f} "
              f"{results[variant]['traffic_jam_length']:<9.2f} "
              f"{bus_eff:<6}")
    
    print(f"\n{'='*60}")
    print("WYJAŚNIENIE STANÓW POJAZDÓW")
    print(f"{'='*60}")
    print("• Ukończ. = Pojazdy które dotarły do celu lub skręciły na skrzyżowaniu (exited/turned)")
    print("• Wjechały = Pojazdy które wjechały na drogę główną") 
    print("• W kolejce = Pojazdy czekające na wjazd (nie zmieściły się)")
    print("• W ruchu = Pojazdy na drodze na końcu symulacji")
    print("• Korek[km] = Długość obszaru z pojazdami jadącymi <10 km/h")
    print("• Brak korka + pojazdy w kolejce = przepustowość ograniczona czasem symulacji")
    
    print(f"\n{'='*60}")
    print("SZCZEGÓŁY WARIANTÓW")
    print(f"{'='*60}")
    
    for variant in available_variants:
        if variant.startswith('CUSTOM_'):
            if 'description' in results[variant]:
                desc = results[variant]["description"]
            else:
                desc = "Niestandardowy scenariusz"
        else:
            try:
                desc = simulation_module.get_variant_short_description(variant, params)
            except:
                desc = f"Wariant standardowy {variant}"
        
        print(f"{variant}: {desc}")
    
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
    
    completion_ranking = sorted(results.items(), key=lambda x: x[1].get('completion_rate', 100.0), reverse=True)
    print("\nRanking po wskaźniku ukończenia podróży (najlepszy → najgorszy):")
    for i, (variant, data) in enumerate(completion_ranking, 1):
        completion_rate = data.get('completion_rate', 100.0)
        in_queue = data.get('vehicles_in_queue', 0)
        in_traffic = data.get('vehicles_in_traffic', 0)
        
        status_info = ""
        if in_queue > 0 and in_traffic == 0:
            status_info = f" (kolejka: {in_queue})"
        elif in_traffic > 0 and in_queue == 0:
            status_info = f" (w ruchu: {in_traffic})" 
        elif in_queue > 0 and in_traffic > 0:
            status_info = f" (kolejka: {in_queue}, w ruchu: {in_traffic})"
            
        print(f"   {i}. Wariant {variant}: {completion_rate:.1f}%{status_info}")
    
    throughput_ranking = sorted(results.items(), key=lambda x: x[1].get('total_entered', x[1]['total_vehicles']), reverse=True)
    print("\nRanking po przepustowości (najlepszy → najgorszy):")
    for i, (variant, data) in enumerate(throughput_ranking, 1):
        total_entered = data.get('total_entered', data['total_vehicles'])
        completed = data['total_vehicles']
        print(f"   {i}. Wariant {variant}: {total_entered} wjechało, {completed} ukończyło")


def _display_hypotheses_verification(results: Dict[str, Any]):
    """Wyświetla weryfikację hipotez badawczych"""
    print("\n" + "="*60)
    print("WERYFIKACJA HIPOTEZ BADAWCZYCH")
    print("="*60)
    
    print("\n1. Hipoteza: Buspas usprawnia ruch komunikacji miejskiej - porównanie wariantów z tą samą liczbą pasów.")
    
    print("\n   PORÓWNANIE A vs B (3 pasy vs 2 pasy + buspas):")
    if 'A' in results and 'B' in results:
        a_data = results['A']
        b_data = results['B'] 
        
        print(f"   • Przepustowość: A={a_data.get('total_entered', 0)} vs B={b_data.get('total_entered', 0)} pojazdów")
        print(f"   • Ukończenie podróży: A={a_data.get('completion_rate', 0):.1f}% vs B={b_data.get('completion_rate', 0):.1f}%")
        print(f"   • Długość korków: A={a_data.get('traffic_jam_length', 0):.2f} vs B={b_data.get('traffic_jam_length', 0):.2f} km")
        print(f"   • Efektywność buspasa B: {b_data.get('bus_efficiency', 0):.1f}%")
        
        if a_data.get('total_entered', 0) > 0 and b_data.get('total_entered', 0) > 0:
            throughput_change = ((b_data.get('total_entered', 0) - a_data.get('total_entered', 0)) / a_data.get('total_entered', 0) * 100)
            completion_change = b_data.get('completion_rate', 0) - a_data.get('completion_rate', 0)
            print(f"   Buspas wpływ: {throughput_change:+.1f}% przepustowości, {completion_change:+.1f}% ukończenia")
    
    print("\n   PORÓWNANIE A vs C (3 pasy vs 3 pasy + buspas):")
    if 'A' in results and 'C' in results:
        a_data = results['A']
        c_data = results['C']
        
        print(f"   • Przepustowość: A={a_data.get('total_entered', 0)} vs C={c_data.get('total_entered', 0)} pojazdów")
        print(f"   • Ukończenie podróży: A={a_data.get('completion_rate', 0):.1f}% vs C={c_data.get('completion_rate', 0):.1f}%")
        print(f"   • Długość korków: A={a_data.get('traffic_jam_length', 0):.2f} vs C={c_data.get('traffic_jam_length', 0):.2f} km")
        print(f"   • Efektywność buspasa C: {c_data.get('bus_efficiency', 0):.1f}%")
        
        if a_data.get('total_entered', 0) > 0 and c_data.get('total_entered', 0) > 0:
            throughput_change = ((c_data.get('total_entered', 0) - a_data.get('total_entered', 0)) / a_data.get('total_entered', 0) * 100)
            completion_change = c_data.get('completion_rate', 0) - a_data.get('completion_rate', 0)
            print(f"   Buspas wpływ: {throughput_change:+.1f}% przepustowości, {completion_change:+.1f}% ukończenia")
    
    variants_with_bus = [(k, v) for k, v in results.items() if v['bus_efficiency'] > 0 and k in ['A', 'B', 'C', 'D']]
    if variants_with_bus:
        avg_bus_efficiency = sum(v['bus_efficiency'] for _, v in variants_with_bus) / len(variants_with_bus)
        print(f"\n   Średnia efektywność buspasa (standardowe warianty): {avg_bus_efficiency:.1f}%")
    
    print("\n2. Hipoteza: Większa liczba pasów zwiększa przepustowość - porównanie wariantów bez buspasa.")
    
    no_bus_variants = []
    lanes = 0
    
    for variant, data in results.items():
        if variant in ['A', 'D'] and data['bus_efficiency'] == 0:  # Tylko warianty bez buspasa
            if variant == 'A': 
                lanes = 3
            elif variant == 'D': 
                lanes = 4
            
            total_entered = data.get('total_entered', data['total_vehicles'])
            completion_rate = data.get('completion_rate', 0)
            no_bus_variants.append((variant, lanes, total_entered, completion_rate))
    
    if len(no_bus_variants) >= 2:
        no_bus_variants.sort(key=lambda x: x[1])
        print(f"   PORÓWNANIE WARIANTÓW BEZ BUSPASA:")
        for variant, lanes, throughput, completion in no_bus_variants:
            print(f"   • Wariant {variant}: {lanes} pasów → {throughput} pojazdów ({completion:.1f}% ukończenia)")
        
        if len(no_bus_variants) == 2:
            var1, lanes1, through1, comp1 = no_bus_variants[0]
            var2, lanes2, through2, comp2 = no_bus_variants[1] 
            
            throughput_change = ((through2 - through1) / through1 * 100) if through1 > 0 else 0
            completion_change = comp2 - comp1
            lanes_added = lanes2 - lanes1
            
            print(f"   {lanes_added} dodatkowy pas: {throughput_change:+.1f}% przepustowości, {completion_change:+.1f}% ukończenia")
    
    print("\n   PORÓWNANIE WPŁYWU BUSPASA PRZY RÓŻNEJ LICZBIE PASÓW:")
    bus_variants = []
    base_lanes = 0
    comparison_variant = None

    for variant, data in results.items():
        if variant in ['B', 'C'] and data['bus_efficiency'] > 0:
            if variant == 'B':
                base_lanes = 2
                comparison_variant = None
            elif variant == 'C':
                base_lanes = 3
                comparison_variant = 'A'
            
            throughput = data.get('total_entered', data['total_vehicles'])
            completion = data.get('completion_rate', 0)
            efficiency = data.get('bus_efficiency', 0)
            
            bus_variants.append((variant, base_lanes, throughput, completion, efficiency, comparison_variant))
    
    for variant, lanes, throughput, completion, efficiency, comparison in bus_variants:
        print(f"   • Wariant {variant}: {lanes} pasy + buspas → {throughput} pojazdów ({completion:.1f}% ukończenia, {efficiency:.1f}% efektywność)")
        
        if comparison and comparison in results:
            comp_data = results[comparison]
            comp_throughput = comp_data.get('total_entered', comp_data['total_vehicles'])
            comp_completion = comp_data.get('completion_rate', 0)
            
            if comp_throughput > 0:
                throughput_gain = ((throughput - comp_throughput) / comp_throughput * 100)
                completion_gain = completion - comp_completion
                print(f"     vs {comparison}: {throughput_gain:+.1f}% przepustowości, {completion_gain:+.1f}% ukończenia")
    
    print("\n3. Hipoteza: Wskaźnik ukończenia podróży jest kluczowy - analiza tylko standardowych wariantów.")
    
    # Znajdź warianty z najlepszym i najgorszym wskaźnikiem ukończenia wśród standardowych
    standard_completion_rates = [(k, v.get('completion_rate', 100.0), v.get('vehicles_in_queue', 0), v.get('vehicles_in_traffic', 0)) 
                                for k, v in results.items() if k in ['A', 'B', 'C', 'D']]
    standard_completion_rates.sort(key=lambda x: x[1], reverse=True)
    
    if standard_completion_rates:
        best = standard_completion_rates[0]
        worst = standard_completion_rates[-1]
        print(f"   • Najlepszy wskaźnik ukończenia: {best[0]} ({best[1]:.1f}%)")
        print(f"     - W kolejce: {best[2]}, w ruchu: {best[3]}")
        print(f"   • Najgorszy wskaźnik ukończenia: {worst[0]} ({worst[1]:.1f}%)")
        print(f"     - W kolejce: {worst[2]}, w ruchu: {worst[3]}")
        
        rate_difference = best[1] - worst[1]
        print(f"   Różnica w efektywności standardowych wariantów: {rate_difference:.1f} punktów procentowych")
        
        print(f"\n   ANALIZA PRZYCZYN:")
        for variant, completion, in_queue, in_traffic in standard_completion_rates:
            total_incomplete = in_queue + in_traffic
            if total_incomplete > 0:
                queue_ratio = (in_queue / total_incomplete * 100) if total_incomplete > 0 else 0
                traffic_ratio = (in_traffic / total_incomplete * 100) if total_incomplete > 0 else 0
                print(f"   • {variant}: {queue_ratio:.0f}% problem kolejki, {traffic_ratio:.0f}% problem korków")


def _display_recommendations(results: Dict[str, Any]):
    """Wyświetla rekomendacje"""
    print("\n" + "="*60)
    print("REKOMENDACJE")
    print("="*60)
    
    travel_time_ranking = sorted(results.items(), key=lambda x: x[1]['avg_travel_time'])
    speed_ranking = sorted(results.items(), key=lambda x: x[1]['avg_speed'], reverse=True)
    jam_ranking = sorted(results.items(), key=lambda x: x[1]['traffic_jam_length'])
    completion_ranking = sorted(results.items(), key=lambda x: x[1].get('completion_rate', 100.0), reverse=True)
    throughput_ranking = sorted(results.items(), key=lambda x: x[1].get('total_entered', x[1]['total_vehicles']), reverse=True)
    
    best_travel_time = travel_time_ranking[0]
    best_speed = speed_ranking[0]
    best_jam = jam_ranking[0]
    best_completion = completion_ranking[0]
    best_throughput = throughput_ranking[0]
    
    print(f"NAJKRÓTSZY CZAS PODRÓŻY: Wariant {best_travel_time[0]} ({best_travel_time[1]['avg_travel_time']:.1f}s)")
    print(f"NAJSZYBSZY: Wariant {best_speed[0]} ({best_speed[1]['avg_speed']:.1f} km/h)")
    print(f"NAJMNIEJ KORKÓW: Wariant {best_jam[0]} ({best_jam[1]['traffic_jam_length']:.2f} km)")
    print(f"NAJWYŻSZY WSKAŹNIK UKOŃCZENIA: Wariant {best_completion[0]} ({best_completion[1].get('completion_rate', 100.0):.1f}%)")
    print(f"NAJWYŻSZA PRZEPUSTOWOŚĆ: Wariant {best_throughput[0]} ({best_throughput[1].get('total_entered', best_throughput[1]['total_vehicles'])} pojazdów)")
    
    # Analiza kompromisowa - znajdź wariant w top 3 w większości kategorii
    print(f"\nANALIZA KOMPROMISOWA:")
    top3_travel = [x[0] for x in travel_time_ranking[:3]]
    top3_completion = [x[0] for x in completion_ranking[:3]]
    top3_throughput = [x[0] for x in throughput_ranking[:3]]
    
    balanced_variants = []
    for variant in results.keys():
        score = 0
        if variant in top3_travel: score += 3
        if variant in top3_completion: score += 2
        if variant in top3_throughput: score += 1
        if score > 0:
            balanced_variants.append((variant, score))
    
    balanced_variants.sort(key=lambda x: x[1], reverse=True)
    
    if balanced_variants:
        best_balanced = balanced_variants[0]
        print(f"• Najlepszy kompromis: Wariant {best_balanced[0]} (wynik: {best_balanced[1]}/6)")
        
        data = results[best_balanced[0]]
        print(f"  - Czas podróży: {data['avg_travel_time']:.1f}s")
        print(f"  - Przepustowość: {data.get('total_entered', data['total_vehicles'])} pojazdów")
        print(f"  - Wskaźnik ukończenia: {data.get('completion_rate', 100.0):.1f}%")
    
    if 'C' in [best_travel_time[0], best_speed[0], best_jam[0]]:
        print("\nKonfiguracja zoptymalizowana (Wariant C) wykazuje najlepsze wyniki!")