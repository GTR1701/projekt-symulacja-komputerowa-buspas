# Projekt Symulacja Komputerowa Buspas

## Spis treści

- [Cel projektu](#cel-projektu)
- [Problem Jagodziński](#problem-jagodziński)
- [Architektura systemu](#architektura-systemu)
- [Struktura projektu](#struktura-projektu)
- [Warianty symulacji](#warianty-symulacji)
- [Konfiguracja parametrów](#konfiguracja-parametrów)
- [Analiza wyników](#analiza-wyników)
- [Testowanie](#testowanie)
- [Dokumentacja API](#dokumentacja-api)
- [Przykłady użycia](#przykłady-użycia)

## Cel projektu

System symulacji komputerowej służy do **analizy efektywności różnych rozwiązań infrastruktury drogowej**, ze szczególnym uwzględnieniem buspassów. Projekt umożliwia porównanie wpływu różnych konfiguracji drogowych na:

- **Czas przejazdu** pojazdów
- **Średnią prędkość** ruchu
- **Długość korków** drogowych
- **Efektywność komunikacji publicznej**
- **Przepustowość** infrastruktury

## Problem Jagodziński

**Problem Jagodziński** to klasyczny dylemat w planowaniu transportu miejskiego:

> _"Czy lepiej jest poszerzyć drogę o dodatkowe pasy dla wszystkich pojazdów, czy też wydzielić dedykowany pas dla komunikacji publicznej (buspas)?"_

### Badane scenariusze

| Scenariusz    | Opis konfiguracji             | Cel analizy                                      |
| ------------- | ----------------------------- | ------------------------------------------------ |
| **Wariant A** | 3 pasy regularne, bez buspasa | Rozwiązanie przez poszerzenie drogi              |
| **Wariant B** | 2 pasy regularne + buspas     | Priorytet dla komunikacji publicznej             |
| **Wariant C** | Konfiguracja zoptymalizowana  | Równowaga między przepustowością a efektywnością |
| **Wariant D** | 4 pasy + buspas               | Rozwiązanie dla intensywnego ruchu               |

### Kluczowe hipotezy badawcze

1. **Hipoteza efektywności**: Buspas usprawnia ruch komunikacji publicznej
2. **Hipoteza przepustowości**: Wpływ buspasa na ogólny ruch nie jest jednoznaczny
3. **Hipoteza korków**: Buspas może redukować korki w pewnych warunkach

## Architektura systemu

System oparty jest na **modularnej architekturze** z wyraźnym podziałem odpowiedzialności:

```
┌─────────────────────────────────────────┐
│             MAIN INTERFACE              │
│  main.py │ analysis_main.py │ test.py   │
├─────────────────────────────────────────┤
│           ANALYSIS MODULE               │
│  • Porównanie wariantów                 │
│  • Analiza efektywności buspasa         │
│  • Wizualizacja wyników                 │
├─────────────────────────────────────────┤
│          SIMULATION ENGINE              │
│  • TrafficSimulation (główny silnik)    │
│  • Vehicle (model pojazdu)              │
│  • TrafficLight (sygnalizacja)          │
│  • InfrastructureConfig                 │
├─────────────────────────────────────────┤
│            DATA LAYER                   │
│  • CSV export/import                    │
│  • Surowe dane symulacji                │
│  • Metadane konfiguracji                │
└─────────────────────────────────────────┘
```

### Wzorce projektowe

- **Strategy Pattern**: Różne konfiguracje infrastruktury
- **Observer Pattern**: Zbieranie danych w trakcie symulacji
- **Factory Pattern**: Tworzenie wariantów symulacji
- **Data Transfer Object**: Struktury parametrów symulacji

## Struktura projektu

```
projekt-symulacja-komputerowa-buspas/
├── main.py                          # Główny punkt wejścia
├── analysis_main.py                 # Punkt wejścia analizy
├── trivial_cases_tester.py         # Tester przypadków trywialnych
├── simulation/                     # Silnik symulacji
│   ├── __init__.py                 # Eksport modułu
│   ├── traffic_simulation.py       # Główny silnik symulacji
│   ├── vehicle.py                  # Model pojazdu
│   ├── traffic_light.py            # Model sygnalizacji
│   ├── infrastructure_config.py    # Konfiguracja infrastruktury
│   ├── simulation_parameters.py    # Parametry symulacji
│   ├── variant_configs.py          # Predefiniowane warianty
│   └── constants.py                # Stałe fizyczne
├── analysis/                      # Moduł analizy
│   ├── __init__.py                 # Eksport modułu analizy
│   ├── data_loader.py              # Ładowanie surowych danych
│   ├── comparison_analysis.py      # Analiza porównawcza
│   ├── lane_analysis.py            # Analiza pojemności pasów
│   └── visualization.py            # Generowanie wykresów
└── simulation_data/               # Dane wyjściowe (gitignore)
    ├── *_timeseries.csv            # Szeregi czasowe symulacji
    ├── *_vehicles.csv              # Szczegółowe dane pojazdów
    ├── *_config.csv                # Metadane konfiguracji
    ├── *_lane_capacity.csv         # Analiza pojemności pasów
    └── *_traffic_lights.csv        # Stan sygnalizacji
```

### Tryby symulacji

| Tryb  | Opis                                       | Użycie                                 |
| ----- | ------------------------------------------ | -------------------------------------- |
| **1** | Tylko predefiniowane scenariusze (A,B,C,D) | Szybka analiza standardowych wariantów |
| **2** | Predefiniowane + niestandardowy            | Porównanie z własną konfiguracją       |
| **3** | Tylko niestandardowy scenariusz            | Testowanie specyficznych parametrów    |

## Warianty symulacji

### Predefiniowane warianty

#### Wariant A: Poszerzenie drogi

```python
{
    'num_lanes': 3,                    # 3 pasy regularne
    'has_bus_lane': False,             # Bez buspasa
    'traffic_light_positions': [1.0, 2.5, 4.0],
    'green_ratio': 0.6                 # 60% czasu na zielonym
}
```

#### Wariant B: Buspas

```python
{
    'num_lanes': 2,                    # 2 pasy regularne
    'has_bus_lane': True,              # + dedykowany buspas
    'bus_lane_capacity': 75,           # pojazdy/km
    'traffic_light_positions': [1.0, 2.5, 4.0],
    'green_ratio': 0.6
}
```

#### Wariant C: Zoptymalizowany

```python
{
    'num_lanes': 3,                    # 3 pasy regularne
    'has_bus_lane': True,              # + buspas
    'traffic_light_positions': [1.5, 3.0],  # Mniej sygnalizacji
    'green_ratio': 0.7                 # Dłuższe zielone światło
}
```

#### Wariant D: Intensywny ruch

```python
{
    'num_lanes': 4,                    # 4 pasy regularne
    'has_bus_lane': True,              # + buspas
    'traffic_light_positions': [0.8, 1.8, 2.8, 3.8],  # Więcej świateł
    'green_ratio': 0.65
}
```

### Parametry niestandardowe

Podczas wyboru trybu **2** lub **3** możesz skonfigurować:

- **Liczba pasów regularnych** (min 1, domyślnie 3)
- **Buspas** (tak/nie)
- **Intensywność ruchu** (min 0.1, domyślnie 0.8)
- **Procent autobusów** (0-100%, domyślnie 15%)
- **Czas zielonego światła** (45-90s, domyślnie 60s)
- **Liczba sygnalizacji** (min 0, domyślnie 3)

## Konfiguracja parametrów

### SimulationParameters

Główna klasa konfiguracji symulacji:

```python
class SimulationParameters:
    # Parametry ruchu
    traffic_intensity_range: Tuple[int, int] = (500, 1500)  # pojazdy/h
    turning_percentage_range: Tuple[float, float] = (0.05, 0.20)  # 5-20%
    privileged_percentage: float = 0.05  # Procent autobusów (5%)

    # Parametry infrastruktury
    road_length: float = 5.0  # km
    lane_capacity: int = 75   # pojazdy/km
    traffic_light_cycle: float = 67.5  # sekundy
    green_light_range: Tuple[float, float] = (45.0, 90.0)

    # Parametry czasowe
    simulation_duration: float = 3600.0  # 1 godzina
    time_step: float = 1.0  # sekunda

    # Pozycje skrzyżowań
    side_road_positions: List[float] = [1.0, 2.5, 4.0]  # km
```

### InfrastructureConfig

Szczegółowa konfiguracja infrastruktury:

```python
class InfrastructureConfig:
    num_lanes: int = 2              # Liczba pasów regularnych
    has_bus_lane: bool = False      # Czy ma buspas
    bus_lane_capacity: int = 0      # Pojemność buspasa
    traffic_light_positions: List[float] = [1.0, 2.5, 4.0]
    traffic_light_green_ratio: float = 0.6  # % czasu na zielonym
    description: str = "Standardowa konfiguracja"
```

### Typy pojazdów

```python
class VehicleType(Enum):
    REGULAR = "regular"      # Pojazdy prywatne
    PRIVILEGED = "privileged"  # Autobusy/komunikacja publiczna
```

### Stałe fizyczne

```python
VEHICLE_LENGTH = 0.0045      # km (4.5m)
VEHICLE_SPACING = 0.0005     # km (0.5m)
VEHICLE_TOTAL_SPACE = 0.005  # km (5m na pojazd)
JAM_THRESHOLD_DISTANCE = 0.050  # km (50m = korek)
DETECTION_DISTANCE = 0.500   # km (500m zasięg wykrywania)
```

## Analiza wyników

System generuje **5 rodzajów plików danych** dla każdej symulacji:

### Rodzaje danych wyjściowych

1. **`*_timeseries.csv`** - Szeregi czasowe symulacji

   ```csv
   timestamp,vehicles_in_motion,average_speed,jam_length,bus_lane_utilization,vehicles_in_queue
   0.0,0,0.0,0.0,0,0
   1.0,2,45.5,0.0,0,0
   ```

2. **`*_vehicles.csv`** - Szczegółowe dane o pojazdach

   ```csv
   vehicle_id,timestamp,action,vehicle_type,lane,position,speed,travel_time
   1,0.0,entered,regular,0,0.0,0.0,0.0
   1,150.2,exited,regular,0,5.0,47.3,150.2
   ```

3. **`*_config.csv`** - Metadane konfiguracji

   ```csv
   simulation_id,num_lanes,has_bus_lane,road_length,privileged_percentage
   variant_a,3,False,5.0,0.05
   ```

4. **`*_lane_capacity.csv`** - Analiza pojemności pasów

   ```csv
   lane_id,lane_type,vehicle_count,actual_capacity_per_km,utilization_percent
   lane_0,regular,125,25.0,33.3
   bus_lane,bus,45,9.0,12.0
   ```

5. **`*_traffic_lights.csv`** - Stan sygnalizacji
   ```csv
   timestamp,light_id,position,state
   0.0,0,1.0,green
   67.5,0,1.0,red
   ```

### Menu analizy

Po uruchomieniu `python3 analysis_main.py`:

1. **Porównanie wszystkich wariantów** - Analiza A,B,C,D + scenariusze niestandardowe
2. **Analiza efektywności buspasa** - Porównanie 3P vs 2P+Bus vs 2P
3. **Test niestandardowej konfiguracji** - Weryfikacja konkretnych parametrów
4. **Analiza pojemności pasów** - Wykorzystanie infrastruktury
5. **Wszystkie powyższe** - Kompletna analiza

### Przykładowe wyniki

```
PODSUMOWANIE WYNIKÓW
============================================================
Wskaźnik                        Wariant A    Wariant B    Wariant C
                                (3P)         (2P+Bus)     (Optym.)
Łączna liczba pojazdów          1247         1205         1289
Średni czas przejazdu [s]       156.3        142.7        138.9
Średnia prędkość [km/h]         29.2         32.5         34.1
Średni czas postoju [s]         45.2         38.7         35.1
Długość korka [km]              0.089        0.067        0.052
Efektywność buspasa [%]         N/A          23.4         28.7
```

## Testowanie

### Tester przypadków trywialnych

Plik `trivial_cases_tester.py` implementuje **test równoważności** z 100% autobusów:

```python
# Test: 1 pas zwykły vs 1 buspas przy samych autobusach
python3 trivial_cases_tester.py
```

#### Cel testu

Weryfikuje czy przy **100% pojazdów uprzywilejowanych** (autobusy):

- 1 pas regularny ≈ 1 buspas (efektywność)
- System poprawnie obsługuje graniczne przypadki
- Konfiguracja infrastruktury jest spójna

#### Przykładowe wyniki testu

```
TEST RÓWNOWAŻNOŚCI: 1 pas zwykły vs 1 buspas (100% autobusów)
────────────────────────────────────────────────────────────────
   PORÓWNANIE:
      1 pas zwykły:  145.3s, 29.1 km/h
      1 buspas:      143.7s, 29.4 km/h
      RÓWNOWAŻNOŚĆ POTWIERDZONA! (różnica 1.1%)
```

### Testowanie funkcjonalne

```bash
# Test podstawowych funkcji
python3 -c "from simulation import *; print('Import simulation OK')"
python3 -c "from analysis import *; print('Import analysis OK')"

# Test tworzenia symulacji
python3 -c "
from simulation import SimulationParameters, RoadConfiguration, TrafficSimulation
params = SimulationParameters()
sim = TrafficSimulation(RoadConfiguration.VARIANT_A, params)
print('TrafficSimulation OK')
"
```

## Dokumentacja API

### Główne klasy

#### TrafficSimulation

Główny silnik symulacji ruchu drogowego.

```python
class TrafficSimulation:
    def __init__(self,
                 config: RoadConfiguration,
                 params: SimulationParameters,
                 infrastructure_config: Optional[InfrastructureConfig] = None)

    def run_simulation(self,
                       save_data: bool = False,
                       data_filename: str = None) -> Dict

    def step(self) -> None  # Jeden krok symulacji
    def get_configuration_description(self) -> str
    def get_short_configuration_description(self) -> str
```

#### Vehicle

Model pojedynczego pojazdu w symulacji.

```python
@dataclass
class Vehicle:
    id: int
    vehicle_type: VehicleType
    entry_time: float
    current_position: float
    speed: float
    lane: int
    will_turn: bool
    turn_position: Optional[float] = None
    waiting_time: float = 0.0
    travel_time: float = 0.0
```

#### TrafficLight

Model sygnalizacji świetlnej.

```python
@dataclass
class TrafficLight:
    position: float
    cycle_duration: float
    green_duration: float
    current_phase: str  # "green" lub "red"
    phase_start_time: float

    @staticmethod
    def calculate_optimal_cycle(green_duration: float) -> float
```

### Funkcje pomocnicze

#### Tworzenie symulacji z parametrami

```python
from simulation import create_simulation_with_parameters

params = SimulationParameters()
infra_params = {
    'num_lanes': 3,
    'has_bus_lane': True,
    'bus_lane_capacity': 100,
    'traffic_light_positions': [2.0, 4.0],
    'green_ratio': 0.7
}

sim = create_simulation_with_parameters(params, infra_params)
result = sim.run_simulation(save_data=True, data_filename="custom_test")
```

#### Analiza surowych danych

```python
from analysis import load_raw_simulation_data

# Załaduj dane z plików CSV
stats = load_raw_simulation_data("simulation_data", "variant_a")
print(f"Średni czas: {stats['avg_travel_time']:.1f}s")
print(f"Efektywność buspasa: {stats['bus_efficiency']:.1f}%")
```

#### Porównanie wariantów

```python
from analysis import run_comparison_study
import simulation

results = run_comparison_study(simulation)
# Automatycznie analizuje wszystkie dostępne warianty
```

## Przykłady użycia

### Przykład 1: Podstawowa symulacja

```python
#!/usr/bin/env python3
from simulation import *

# Utwórz parametry symulacji
params = SimulationParameters()
params.privileged_percentage = 0.15  # 15% autobusów
params.simulation_duration = 1800.0  # 30 minut

# Uruchom wariant A (3 pasy, bez buspasa)
sim_a = TrafficSimulation(RoadConfiguration.VARIANT_A, params)
result_a = sim_a.run_simulation()

# Uruchom wariant B (2 pasy + buspas)
sim_b = TrafficSimulation(RoadConfiguration.VARIANT_B, params)
result_b = sim_b.run_simulation()

print(f"Wariant A: {result_a['completed_vehicles']} pojazdów")
print(f"Wariant B: {result_b['completed_vehicles']} pojazdów")
```

### Przykład 2: Niestandardowa konfiguracja

```python
#!/usr/bin/env python3
from simulation import *

# Parametry dla intensywnego ruchu
params = SimulationParameters()
params.traffic_intensity_range = (2000, 3000)  # Wysokie natężenie
params.privileged_percentage = 0.25  # 25% autobusów

# Konfiguracja: 4 pasy + buspas o dużej pojemności
custom_config = {
    'num_lanes': 4,
    'has_bus_lane': True,
    'bus_lane_capacity': 150,  # Zwiększona pojemność
    'traffic_light_positions': [1.0, 2.5, 4.0],
    'green_ratio': 0.8  # 80% czasu na zielonym
}

# Utwórz i uruchom symulację
sim = create_simulation_with_parameters(params, custom_config)
result = sim.run_simulation(save_data=True, data_filename="intensive_traffic")

print(f"Konfiguracja: {sim.get_configuration_description()}")
print(f"Obsłużono: {result['completed_vehicles']} pojazdów")
```

### Przykład 3: Analiza efektywności buspasa

```python
#!/usr/bin/env python3
import analysis

# Uruchom analizę porównawczą efektywności
results = analysis.compare_bus_lane_efficiency()

efficiency = results['efficiency_metrics']
print(f"Poprawa czasu przejazdu przez buspas: {efficiency['time_improvement_a_b']:.1f}%")
print(f"Redukcja korków przez buspas: {efficiency['jam_improvement_a_b']:.1f}%")
print(f"Efektywność buspasa: {efficiency.get('bus_efficiency', 0):.1f}%")
```

### Przykład 4: Analiza pojemności pasów

```python
#!/usr/bin/env python3
from analysis import analyze_lane_capacity, print_lane_capacity_analysis

# Analizuj wykorzystanie pasów dla konkretnej symulacji
lane_analysis = analyze_lane_capacity("simulation_data", "variant_b")
print_lane_capacity_analysis(lane_analysis)

# Wynik przykładowy:
# PASY REGULARNE:
#    Średnie wykorzystanie: 67.3%
#    Średnia pojemność: 50.5 poj./km
# BUSPAS:
#    Wykorzystanie: 45.2%
#    Pojemność: 33.9 poj./km
```

### Przykład 5: Automatyczna wizualizacja

```python
#!/usr/bin/env python3
from analysis import run_comparison_study, create_visualization
import simulation

# Uruchom porównanie wszystkich wariantów
results = run_comparison_study(simulation)

# Wygeneruj wykresy porównawcze
create_visualization(results, "analiza_wszystkich_wariantow", simulation)

# Wynik: plik problem_jagodzinski_analiza_wszystkich_wariantow.png
```
