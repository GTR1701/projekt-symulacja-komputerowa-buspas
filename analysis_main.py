#!/usr/bin/env python3
"""
Analysis entry point for Traffic Simulation analysis
Punkt wejścia do analizy danych symulacji
"""

import os
import glob
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import analysis
import simulation


def main():
    """Główna funkcja analizy"""
    print("="*60)
    print("ANALIZA DANYCH SYMULACJI PROBLEMU JAGODZIŃSKIEGO")
    print("="*60)
    
    data_dir = "simulation_data"
    if not os.path.exists(data_dir):
        print("Brak katalogu simulation_data!")
        print("Najpierw uruchom: python3 main.py")
        return 1
    
    csv_files = glob.glob(os.path.join(data_dir, "*.csv"))
    if not csv_files:
        print("Brak plików CSV z danymi!")
        print("Najpierw uruchom: python3 main.py")
        return 1
    
    print(f"Znaleziono {len(csv_files)} plików z danymi")
    print("\nMenu analizy:")
    print("1. Porównanie wszystkich wariantów")
    print("2. Analiza efektywności buspasa") 
    print("3. Test niestandardowej konfiguracji")
    print("4. Analiza pojemności pasów")
    print("5. Wszystkie powyższe")
    
    try:
        choice = input("\nWybór (1-5, Enter = 1): ").strip()
        if not choice:
            choice = "1"
    except:
        choice = "1"
    
    if choice == "1":
        print("\nPORÓWNANIE WSZYSTKICH WARIANTÓW")
        print("-" * 40)
        results = analysis.run_comparison_study(simulation)
        analysis.create_visualization(results, "wszystkie_warianty", simulation)
        
    elif choice == "2":
        print("\nANALIZA EFEKTYWNOŚCI BUSPASA")
        print("-" * 40)
        results = analysis.compare_bus_lane_efficiency()
        
    elif choice == "3":
        print("\nTEST NIESTANDARDOWEJ KONFIGURACJI")
        print("-" * 40)
        results = analysis.test_custom_configuration(
            simulation,
            lane_count=3,
            bus_lane=True,
            traffic_intensity=0.9,
            privileged_percentage=20,
            verbose=True
        )
        
    elif choice == "4":
        print("\nANALIZA POJEMNOŚCI PASÓW")
        print("-" * 50)
        analysis.print_all_lane_capacities_summary()
        
    elif choice == "5":
        print("\nCZĘŚĆ 1: PORÓWNANIE WSZYSTKICH WARIANTÓW")
        print("-" * 50)
        results1 = analysis.run_comparison_study(simulation)
        analysis.create_visualization(results1, "wszystkie_warianty", simulation)
        
        print("\nCZĘŚĆ 2: ANALIZA EFEKTYWNOŚCI BUSPASA")
        print("-" * 50)
        results2 = analysis.compare_bus_lane_efficiency()
        
        print("\nCZĘŚĆ 3: TEST NIESTANDARDOWEJ KONFIGURACJI")
        print("-" * 50)
        results3 = analysis.test_custom_configuration(
            simulation,
            lane_count=3,
            bus_lane=True,
            traffic_intensity=0.9,
            privileged_percentage=20,
            verbose=True
        )
        
        print("\nCZĘŚĆ 4: ANALIZA POJEMNOŚCI PASÓW")
        print("-" * 50)
        analysis.print_all_lane_capacities_summary()
    
    else:
        print("Nieprawidłowy wybór, uruchamiam porównanie wariantów...")
        results = analysis.run_comparison_study(simulation)
        analysis.create_visualization(results, "wszystkie_warianty", simulation)
    
    print("\n" + "="*60)
    print("ANALIZA ZAKOŃCZONA")
    print("="*60)
    return 0


if __name__ == "__main__":
    sys.exit(main())