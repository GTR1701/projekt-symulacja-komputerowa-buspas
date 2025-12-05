"""
Visualization functions for simulation results
"""

import os
from typing import Dict, Any


def create_visualization(results: Dict, filename_suffix: str = "wyniki", simulation_module=None):
    """Tworzy wizualizację wyników symulacji"""
    try:
        import matplotlib.pyplot as plt
        import numpy as np
        
        available_variants = list(results.keys())
        n_variants = len(available_variants)
        
        if n_variants == 0:
            print("Brak wyników do wizualizacji")
            return
        
        if simulation_module:
            params = simulation_module.SimulationParameters()
            
            variant_labels = {}
            for var in available_variants:
                base_name = {
                    'A': 'A: 3P',
                    'B': 'B: 2P+Bus', 
                    'C': 'C: 3P+Bus',
                    'D': 'D: 4P',
                    'CUSTOM': f'CUSTOM_{available_variants.index(var)+1}',
                    'minimal': 'MIN',
                    'maximal': 'MAX'
                }.get(var, var)
                
                if var.startswith('CUSTOM_'):
                    variant_labels[var] = var
                else:
                    variant_labels[var] = base_name
        else:
            variant_labels = {var: f'Wariant {var}' for var in available_variants}
        
        labels = [variant_labels[var] for var in available_variants]
        
        base_colors = ['lightblue', 'lightgreen', 'lightcoral', 'lightyellow', 'lightpink', 'lightgray']
        bar_colors = (base_colors * ((n_variants // len(base_colors)) + 1))[:n_variants]
        
        fig, ((ax1, ax2), (ax3, ax4), (ax5, ax6)) = plt.subplots(3, 2, figsize=(14, 15))
        fig.suptitle('Porównanie wariantów rozwiązania Problemu Jagodzińskiego', fontsize=16)
        
        travel_times = [results[var]['avg_travel_time'] for var in available_variants]
        bars1 = ax1.bar(labels, travel_times, color=bar_colors[:n_variants])
        ax1.set_ylabel('Czas [s]')
        ax1.set_title('Średni czas przejazdu')
        ax1.tick_params(axis='x', rotation=45)
        
        for bar, value in zip(bars1, travel_times):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'{value:.0f}s', ha='center', va='bottom', fontsize=2)
        
        speeds = [results[var]['avg_speed'] for var in available_variants]
        bars2 = ax2.bar(labels, speeds, color=bar_colors[:n_variants])
        ax2.set_ylabel('Prędkość [km/h]')
        ax2.set_title('Średnia prędkość pojazdu')
        ax2.tick_params(axis='x', rotation=45)
        
        for bar, value in zip(bars2, speeds):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'{value:.2f}', ha='center', va='bottom', fontsize=7)
        
        jam_lengths = [results[var]['traffic_jam_length'] for var in available_variants]
        bars3 = ax3.bar(labels, jam_lengths, color=bar_colors[:n_variants])
        ax3.set_ylabel('Długość [km]')
        ax3.set_title('Długość korka')
        ax3.tick_params(axis='x', rotation=45)
        
        for bar, value in zip(bars3, jam_lengths):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'{value:.3f}', ha='center', va='bottom', fontsize=7)
        
        waiting_times = [results[var]['avg_waiting_time'] for var in available_variants]
        bars4 = ax4.bar(labels, waiting_times, color=bar_colors[:n_variants])
        ax4.set_ylabel('Czas [s]')
        ax4.set_title('Średni czas postoju')
        ax4.tick_params(axis='x', rotation=45)
        
        for bar, value in zip(bars4, waiting_times):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'{value:.0f}s', ha='center', va='bottom', fontsize=7)
        
        total_vehicles = [results[var]['total_vehicles'] for var in available_variants]
        bars5 = ax5.bar(labels, total_vehicles, color=bar_colors[:n_variants])
        ax5.set_ylabel('Liczba pojazdów')
        ax5.set_title('Łączna liczba obsłużonych pojazdów')
        ax5.tick_params(axis='x', rotation=45)
        
        for bar, value in zip(bars5, total_vehicles):
            height = bar.get_height()
            ax5.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'{value}', ha='center', va='bottom', fontsize=7)
        
        bus_variants = [var for var in available_variants if results[var]['bus_efficiency'] > 0]
        if bus_variants:
            bus_labels = [variant_labels.get(var, f'Wariant {var}') for var in bus_variants]
            bus_efficiency = [results[var]['bus_efficiency'] for var in bus_variants]
            bus_colors = [bar_colors[available_variants.index(var)] for var in bus_variants]
            
            bars6 = ax6.bar(bus_labels, bus_efficiency, color=bus_colors)
            ax6.set_ylabel('Efektywność [%]')
            ax6.set_title('Efektywność buspasa')
            ax6.tick_params(axis='x', rotation=45)
            
            for bar, value in zip(bars6, bus_efficiency):
                height = bar.get_height()
                ax6.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                        f'{value:.1f}%', ha='center', va='bottom', fontsize=7)
        else:
            ax6.text(0.5, 0.5, 'Brak wariantów\nz buspasem', 
                    ha='center', va='center', transform=ax6.transAxes, 
                    fontsize=12, style='italic')
            ax6.set_xticks([])
            ax6.set_yticks([])
        
        plt.tight_layout()
        
        filename = f'{os.getcwd()}/problem_jagodzinski_{filename_suffix}.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        
        print(f"\nWykres dla {n_variants} wariantów zapisano jako: problem_jagodzinski_{filename_suffix}.png")
        
    except ImportError:
        print("Matplotlib nie jest dostępny - pomijam tworzenie wykresów")