"""
TrafficLight class - reprezentuje sygnalizację świetlną
"""

from dataclasses import dataclass


@dataclass
class TrafficLight:
    """Klasa reprezentująca sygnalizację świetlną"""
    position: float
    cycle_duration: float
    green_duration: float
    current_phase: str  # "green" lub "red"
    phase_start_time: float
    
    @staticmethod
    def calculate_optimal_cycle(green_duration: float) -> float:
        """Oblicza optymalny cykl światła na podstawie czasu zielonego
        
        Założenia:
        - Zielone światło: podany czas (45-90s)
        - Żółte światło: 3 sekundy
        - Czerwone światło: minimum 30s dla bezpieczeństwa ruchu pieszego
        - Dodatkowy margines: 10% cyklu dla płynności
        """
        yellow_duration = 3.0
        min_red_duration = 30.0
        
        base_cycle = green_duration + yellow_duration + min_red_duration
        optimal_cycle = base_cycle * 1.1
        
        return round(optimal_cycle, 1)