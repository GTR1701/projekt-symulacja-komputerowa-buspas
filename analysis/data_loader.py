"""
Data loading and processing functions for simulation analysis
"""

import os
import pandas as pd
import numpy as np
import glob
from typing import Dict, Any
from simulation.constants import (
    VEHICLE_TOTAL_SPACE,
    SLOW_TRAFFIC_THRESHOLD,
    JAM_THRESHOLD_DISTANCE,
    BUS_EFFICIENCY_TIME_WEIGHT,
    BUS_EFFICIENCY_SPEED_WEIGHT
)


def load_raw_simulation_data(data_dir: str, pattern: str) -> Dict[str, Any]:
    """Ładuje surowe dane symulacji z plików CSV i oblicza statystyki
    
    Args:
        data_dir: katalog z danymi
        pattern: wzorzec nazwy pliku (np. 'scenario_a', 'variant_b')
    
    Returns:
        Dict ze statystykami obliczonymi z surowych danych
    """
    vehicle_files = glob.glob(os.path.join(data_dir, f"*{pattern}*_vehicles.csv"))
    config_files = glob.glob(os.path.join(data_dir, f"*{pattern}*_config.csv"))
    timeseries_files = glob.glob(os.path.join(data_dir, f"*{pattern}*_timeseries.csv"))
    
    if not vehicle_files or not config_files:
        return {}
    
    vehicle_file = sorted(vehicle_files, key=os.path.getmtime, reverse=True)[0]
    config_file = sorted(config_files, key=os.path.getmtime, reverse=True)[0]
    
    try:
        vehicles_df = pd.read_csv(vehicle_file)
        config_df = pd.read_csv(config_file)
        
        stats = calculate_statistics_from_raw_data(vehicles_df, config_df.iloc[0])
        
        stats = dict(stats)
        stats['source_file'] = os.path.basename(vehicle_file)
        stats['config_file'] = os.path.basename(config_file)
        
        return stats
        
    except Exception as e:
        print(f"Błąd przy ładowaniu danych z {pattern}: {e}")
        return {}


def calculate_statistics_from_raw_data(vehicles_df: pd.DataFrame, config: pd.Series) -> Dict[str, Any]:
    """Oblicza statystyki z surowych danych o pojazdach
    
    Args:
        vehicles_df: DataFrame z danymi o pojazdach
        config: Series z konfiguracją symulacji
    
    Returns:
        Dict ze statystykami
    """
    completed = vehicles_df[vehicles_df['action'].isin(['exited', 'turned'])].copy()
    
    all_entered = vehicles_df[vehicles_df['action'].isin(['entered', 'entered_from_queue', 'exited', 'turned'])].copy()
    total_entered = len(all_entered['vehicle_id'].unique()) if not all_entered.empty else 0
    
    completed_ids = set(completed['vehicle_id'].unique()) if not completed.empty else set()
    entered_ids = set(all_entered['vehicle_id'].unique()) if not all_entered.empty else set()
    incomplete_count = len(entered_ids - completed_ids)
    
    latest_positions = vehicles_df.loc[vehicles_df.groupby('vehicle_id')['timestamp'].idxmax()]
    vehicles_in_queue = len(latest_positions[latest_positions['action'] == 'queued'])
    vehicles_in_traffic = len(latest_positions[latest_positions['action'].isin(['entered', 'entered_from_queue'])])
    
    if completed.empty:
        return {
            'total_vehicles': 0,
            'total_entered': total_entered,
            'incomplete_vehicles': incomplete_count,
            'vehicles_in_queue': vehicles_in_queue,
            'vehicles_in_traffic': vehicles_in_traffic,
            'completion_rate': 0.0,
            'avg_travel_time': 0.0,
            'avg_speed': 0.0,
            'avg_waiting_time': 0.0,
            'traffic_jam_length': 0.0,
            'bus_efficiency': 0.0
        }
    
    total_vehicles = len(completed)
    completion_rate = (total_vehicles / total_entered * 100) if total_entered > 0 else 0.0
    avg_travel_time = completed['travel_time'].mean()
    avg_waiting_time = completed['waiting_time'].mean()
    
    speeds = []
    road_length = float(config['road_length'])
    
    for _, vehicle in completed.iterrows():
        if vehicle['travel_time'] > 0:
            if vehicle['will_turn'] and pd.notna(vehicle['turn_position']):
                distance = float(vehicle['turn_position'])
            else:
                distance = road_length
            avg_speed = (distance / vehicle['travel_time']) * 3600
            speeds.append(avg_speed)
    
    avg_speed = np.mean(speeds) if speeds else 0.0
    
    traffic_jam_length = calculate_jam_length_from_data(vehicles_df)
    
    bus_efficiency = calculate_bus_efficiency_from_data(completed, config)
    
    return {
        'total_vehicles': total_vehicles,
        'total_entered': total_entered,
        'incomplete_vehicles': incomplete_count,
        'vehicles_in_queue': vehicles_in_queue,
        'vehicles_in_traffic': vehicles_in_traffic,
        'completion_rate': completion_rate,
        'avg_travel_time': avg_travel_time,
        'avg_speed': avg_speed,
        'avg_waiting_time': avg_waiting_time,
        'traffic_jam_length': traffic_jam_length,
        'bus_efficiency': bus_efficiency
    }


def calculate_jam_length_from_data(vehicles_df: pd.DataFrame) -> float:
    """Oblicza długość korka na podstawie danych o pojazdach"""
    latest_positions = vehicles_df.loc[vehicles_df.groupby('vehicle_id')['timestamp'].idxmax()]
    moving_vehicles = latest_positions[latest_positions['action'].isin(['entered', 'entered_from_queue'])]
    
    if moving_vehicles.empty:
        return 0.0
    
    slow_vehicles = moving_vehicles[moving_vehicles['speed'] < SLOW_TRAFFIC_THRESHOLD]
    
    if slow_vehicles.empty:
        return 0.0
    
    positions = sorted(slow_vehicles['position'].values)
    
    if len(positions) < 2:
        return VEHICLE_TOTAL_SPACE
    
    max_jam_length = 0.0
    current_jam_length = VEHICLE_TOTAL_SPACE
    
    for i in range(1, len(positions)):
        gap = positions[i] - positions[i-1]
        if gap < JAM_THRESHOLD_DISTANCE:
            current_jam_length += VEHICLE_TOTAL_SPACE
        else:
            max_jam_length = max(max_jam_length, current_jam_length)
            current_jam_length = VEHICLE_TOTAL_SPACE
    
    return max(max_jam_length, current_jam_length)


def calculate_bus_efficiency_from_data(completed_df: pd.DataFrame, config: pd.Series) -> float:
    """Oblicza efektywność buspasa z danych o pojazdach"""
    has_bus_lane = config.get('has_bus_lane', False)
    
    if not has_bus_lane:
        return 0.0
    
    bus_vehicles = completed_df[completed_df['vehicle_type'] == 'privileged']
    regular_vehicles = completed_df[completed_df['vehicle_type'] == 'regular']
    
    if bus_vehicles.empty or regular_vehicles.empty:
        return 0.0
    
    avg_bus_time = bus_vehicles['travel_time'].mean()
    avg_regular_time = regular_vehicles['travel_time'].mean()
    
    time_efficiency = max(0.0, (avg_regular_time - avg_bus_time) / avg_regular_time * 100)
    
    bus_speeds = []
    regular_speeds = []
    road_length = float(config['road_length'])
    
    for _, vehicle in bus_vehicles.iterrows():
        if vehicle['travel_time'] > 0:
            distance = float(vehicle['turn_position']) if vehicle['will_turn'] and pd.notna(vehicle['turn_position']) else road_length
            speed = (distance / vehicle['travel_time']) * 3600
            bus_speeds.append(speed)
    
    for _, vehicle in regular_vehicles.iterrows():
        if vehicle['travel_time'] > 0:
            distance = float(vehicle['turn_position']) if vehicle['will_turn'] and pd.notna(vehicle['turn_position']) else road_length
            speed = (distance / vehicle['travel_time']) * 3600
            regular_speeds.append(speed)
    
    if bus_speeds and regular_speeds:
        avg_bus_speed = np.mean(bus_speeds)
        avg_regular_speed = np.mean(regular_speeds)
        speed_efficiency = max(0.0, (avg_bus_speed - avg_regular_speed) / avg_regular_speed * 100)
        return float(time_efficiency * BUS_EFFICIENCY_TIME_WEIGHT + speed_efficiency * BUS_EFFICIENCY_SPEED_WEIGHT)
    
    return float(time_efficiency)