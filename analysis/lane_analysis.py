"""
Lane capacity analysis functions
"""

import os
import pandas as pd
import glob
from typing import Dict, Any


def analyze_lane_capacity(data_dir: str, pattern: str) -> Dict[str, Any]:
    """Analizuje pojemność i wykorzystanie pasów z pliku lane_capacity.csv
    
    Args:
        data_dir: katalog z danymi
        pattern: wzorzec nazwy pliku (np. 'scenario_a', 'variant_b')
    
    Returns:
        Dict z analizą pojemności pasów
    """
    capacity_files = glob.glob(os.path.join(data_dir, f"*{pattern}*_lane_capacity.csv"))
    
    if not capacity_files:
        return {'error': 'Brak pliku z danymi o pojemności pasów'}
    
    capacity_file = sorted(capacity_files, key=os.path.getmtime, reverse=True)[0]
    
    try:
        df = pd.read_csv(capacity_file)
        
        regular_lanes = df[df['lane_type'] == 'regular']
        bus_lane = df[df['lane_type'] == 'bus']
        summary = df[df['lane_type'] == 'summary']
        
        analysis = {
            'simulation_id': df['simulation_id'].iloc[0] if len(df) > 0 else '',
            'source_file': os.path.basename(capacity_file)
        }
        
        if len(regular_lanes) > 0:
            analysis['regular_lanes'] = {
                'count': len(regular_lanes),
                'total_vehicles': int(regular_lanes['vehicle_count'].sum()),
                'avg_vehicles_per_lane': round(regular_lanes['vehicle_count'].mean(), 1),
                'avg_capacity_per_km': round(regular_lanes['actual_capacity_per_km'].mean(), 1),
                'avg_utilization_percent': round(regular_lanes['utilization_percent'].mean(), 1),
                'min_utilization': round(regular_lanes['utilization_percent'].min(), 1),
                'max_utilization': round(regular_lanes['utilization_percent'].max(), 1),
                'theoretical_capacity': int(regular_lanes['theoretical_capacity_per_km'].iloc[0]) if len(regular_lanes) > 0 else 0,
                'lane_details': []
            }
            
            for _, row in regular_lanes.iterrows():
                lane_num = row['lane_id'].split('_')[1] if '_' in str(row['lane_id']) else str(row['lane_id'])
                analysis['regular_lanes']['lane_details'].append({
                    'lane_number': lane_num,
                    'vehicles': int(row['vehicle_count']),
                    'capacity_per_km': round(row['actual_capacity_per_km'], 1),
                    'utilization_percent': round(row['utilization_percent'], 1)
                })
        
        if len(bus_lane) > 0:
            bus_row = bus_lane.iloc[0]
            analysis['bus_lane'] = {
                'vehicles': int(bus_row['vehicle_count']),
                'capacity_per_km': round(bus_row['actual_capacity_per_km'], 1),
                'theoretical_capacity': int(bus_row['theoretical_capacity_per_km']),
                'utilization_percent': round(bus_row['utilization_percent'], 1)
            }
        
        if len(summary) > 0:
            summary_row = summary.iloc[0]
            analysis['summary'] = {
                'total_vehicles': int(summary_row['vehicle_count']),
                'avg_capacity_regular_lanes': round(summary_row['actual_capacity_per_km'], 1),
                'avg_utilization_regular_lanes': round(summary_row['utilization_percent'], 1),
                'theoretical_capacity': int(summary_row['theoretical_capacity_per_km'])
            }
            
        return analysis
        
    except Exception as e:
        return {'error': f'Błąd podczas analizy pojemności pasów: {str(e)}'}


def print_lane_capacity_analysis(analysis: Dict[str, Any]) -> None:
    """Wyświetla analizę pojemności pasów w czytelnej formie"""
    if 'error' in analysis:
        print(f"{analysis['error']}")
        return
    
    print(f"\nANALIZA POJEMNOŚCI PASÓW")
    print(f"{'='*50}")
    print(f"Symulacja: {analysis.get('simulation_id', 'N/A')}")
    
    if 'regular_lanes' in analysis:
        reg = analysis['regular_lanes']
        print(f"\nPASY REGULARNE:")
        print(f"   Liczba pasów: {reg['count']}")
        print(f"   Łącznie pojazdów: {reg['total_vehicles']}")
        print(f"   Średnio pojazdów/pas: {reg['avg_vehicles_per_lane']}")
        print(f"   Średnia pojemność: {reg['avg_capacity_per_km']} poj./km")
        print(f"   Teoretyczna pojemność: {reg['theoretical_capacity']} poj./km")
        print(f"   Średnie wykorzystanie: {reg['avg_utilization_percent']}%")
        print(f"   Zakres wykorzystania: {reg['min_utilization']}% - {reg['max_utilization']}%")
        
        for lane in reg['lane_details']:
            print(f"     • Pas {lane['lane_number']}: {lane['vehicles']} poj., {lane['capacity_per_km']} poj./km ({lane['utilization_percent']}%)")
    
    if 'bus_lane' in analysis:
        bus = analysis['bus_lane']
        print(f"\nBUSPAS:")
        print(f"   Pojazdy: {bus['vehicles']}")
        print(f"   Rzeczywista pojemność: {bus['capacity_per_km']} poj./km")
        print(f"   Teoretyczna pojemność: {bus['theoretical_capacity']} poj./km")
        print(f"   Wykorzystanie: {bus['utilization_percent']}%")
    
    if 'summary' in analysis:
        summary = analysis['summary']
        print(f"\nPODSUMOWANIE:")
        print(f"   Łącznie pojazdów: {summary['total_vehicles']}")
        print(f"   Średnia pojemność pasów reg.: {summary['avg_capacity_regular_lanes']} poj./km")
        print(f"   Średnie wykorzystanie: {summary['avg_utilization_regular_lanes']}%")


def analyze_all_lane_capacities(data_dir: str = "simulation_data") -> Dict[str, Any]:
    """Analizuje pojemność pasów dla wszystkich dostępnych symulacji
    
    Returns:
        Dict z analizą pojemności dla wszystkich symulacji
    """
    capacity_files = glob.glob(os.path.join(data_dir, "*_lane_capacity.csv"))
    
    if not capacity_files:
        return {'error': 'Brak plików z danymi o pojemności pasów'}
    
    all_analyses = {}
    
    for file_path in capacity_files:
        filename = os.path.basename(file_path)
        pattern = filename.replace('_lane_capacity.csv', '')
        
        analysis = analyze_lane_capacity(data_dir, pattern)
        if 'error' not in analysis:
            all_analyses[pattern] = analysis
    
    return all_analyses


def print_all_lane_capacities_summary(data_dir: str = "simulation_data") -> None:
    """Wyświetla podsumowanie pojemności pasów dla wszystkich symulacji"""
    all_analyses = analyze_all_lane_capacities(data_dir)
    
    if 'error' in all_analyses:
        print(f"{all_analyses['error']}")
        return
    
    if not all_analyses:
        print("Brak danych o pojemności pasów do analizy")
        return
    
    print(f"PRZEGLĄD POJEMNOŚCI PASÓW - WSZYSTKIE SYMULACJE")
    print(f"{'='*70}")
    
    for pattern, analysis in all_analyses.items():
        print(f"\n{pattern}")
        print(f"{'─'*50}")
        
        if 'regular_lanes' in analysis:
            reg = analysis['regular_lanes']
            print(f"Pasy regularne: {reg['count']} pasów, śr. wykorzystanie {reg['avg_utilization_percent']}%")
            print(f"   Pojemność: {reg['avg_capacity_per_km']}/{reg['theoretical_capacity']} poj./km")
        
        if 'bus_lane' in analysis:
            bus = analysis['bus_lane']
            print(f"Buspas: {bus['utilization_percent']}% wykorzystania ({bus['capacity_per_km']}/{bus['theoretical_capacity']} poj./km)")
        
        if 'summary' in analysis:
            summary = analysis['summary']
            print(f"Łącznie: {summary['total_vehicles']} pojazdów")