# Dokumentacja Projektu - Symulacja Komputerowa Buspas

## Spis Treści

1. [Struktura Projektu](#struktura-projektu)
2. [Główne Pliki Wejściowe](#główne-pliki-wejściowe)
3. [Pliki CSV - Dane Wyjściowe](#pliki-csv---dane-wyjściowe)
4. [Krótki Opis Metod w Klasach](#krótki-opis-metod-w-klasach)
5. [Przykłady Uruchomienia](#przykłady-uruchomienia)

---

## Struktura Projektu

```
/
├── main.py                         # Główny punkt wejścia (interfejs CLI)
├── simulation_main.py              # Uruchamianie symulacji
├── analysis_main.py                # Uruchamianie analizy
├── trivial_cases_tester.py         # Testy przypadków trywialnych
│
├── simulation/                     # Moduł symulacji
│   ├── __init__.py                 # Eksport publicznego API
│   ├── traffic_simulation.py       # Główna klasa symulacji
│   ├── vehicle.py                  # Klasa pojazdu
│   ├── traffic_light.py            # Klasa sygnalizacji świetlnej
│   ├── simulation_parameters.py    # Parametry symulacji
│   ├── infrastructure_config.py    # Konfiguracja infrastruktury
│   ├── variant_configs.py          # Predefiniowane warianty
│   └── constants.py                # Stałe fizyczne
│
├── analysis/                       # Moduł analizy
│   ├── __init__.py                 # Eksport funkcji analizy
│   ├── data_loader.py              # Ładowanie danych z CSV
│   ├── comparison_analysis.py      # Analiza porównawcza
│   ├── lane_analysis.py            # Analiza pojemności pasów
│   └── visualization.py            # Generowanie wykresów
│
└── simulation_data/                # Dane wyjściowe symulacji (CSV)
    ├── *_timeseries.csv            # Szeregi czasowe
    ├── *_vehicles.csv              # Szczegóły pojazdów
    ├── *_config.csv                # Metadane konfiguracji
    ├── *_lane_capacity.csv         # Analiza pojemności pasów
    └── *_traffic_lights.csv        # Stan sygnalizacji
```

---

## Główne Pliki Wejściowe

### main.py

Główny interfejs CLI do systemu. Zapewnia ujednolicony punkt wejścia z trzema trybami pracy:

- Tryb interaktywny z menu
- Bezpośrednie uruchamianie symulacji
- Bezpośrednie uruchamianie analizy
- Uruchamianie testów przypadków trywialnych

### simulation_main.py

Punkt wejścia do modułu symulacji. Umożliwia uruchamianie:

- Wszystkich standardowych wariantów infrastruktury (A, B, C, D)
- Pojedynczych wariantów do szczegółowego testowania
- Niestandardowych konfiguracji z interaktywnym konfiguratorem

### analysis_main.py

Punkt wejścia do modułu analizy. Zapewnia:

- Porównanie wszystkich wariantów z wizualizacją
- Analizę efektywności buspasa
- Test niestandardowej konfiguracji
- Analizę pojemności pasów ruchu

### trivial_cases_tester.py

Narzędzie do testowania przypadków trywialnych (100% autobusów) w celu walidacji poprawności modelu symulacji.

---

## Pliki CSV - Dane Wyjściowe

Każda symulacja generuje zestaw plików CSV w katalogu `simulation_data/` z prefiksem zawierającym wariant i timestamp utworzenia pliku (format: `{wariant}_{YYYYMMDD_HHMMSS}`).

### Konwencje Nazewnictwa

**Format nazw plików:**

```
{wariant}_{timestamp}_{typ}.csv
```

**Przykłady:**

- `variant_a_20251208_153327_vehicles.csv`
- `variant_b_20251208_120404_timeseries.csv`
- `custom_3l_1_i0.8_b15_g54_20251208_173906_config.csv`

**Kody wariantów:**

- `variant_a` - Wariant A (3 pasy regularne)
- `variant_b` - Wariant B (2 pasy + buspas)
- `variant_c` - Wariant C (3 pasy + buspas)
- `variant_d` - Wariant D (4 pasy regularne)
- `custom_*` - Konfiguracje niestandardowe

### 1. \*\_vehicles.csv - Szczegółowe Dane Pojazdów

Zawiera informacje o każdym pojeździe, który wziął udział w symulacji.

**Kolumny:**

- `vehicle_id` (int) - Unikalny identyfikator pojazdu
- `vehicle_type` (str) - Typ pojazdu: "regular" (samochód) lub "privileged" (autobus)
- `entry_time` (float) - Czas wjazdu na drogę główną [s]
- `travel_time` (float) - Łączny czas podróży [s]
- `waiting_time` (float) - Czas oczekiwania w korkach [s]
- `final_position` (float) - Pozycja opuszczenia drogi głównej [km]
- `lane` (int) - Numer pasa (0-N dla regularnych, -1 dla buspasa)
- `action` (str) - Sposób zakończenia: "exited", "turned", "in_motion", "queued"
- `timestamp` (float) - Czas zapisania zdarzenia [s]

**Przykład:**

```csv
vehicle_id,vehicle_type,entry_time,travel_time,waiting_time,final_position,lane,action,timestamp
1,regular,0.5,145.2,23.1,5.0,0,exited,145.7
2,privileged,1.2,98.7,8.3,2.5,-1,turned,99.9
```

### 2. \*\_timeseries.csv - Szeregi Czasowe

Dane zbierane w każdym kroku czasowym symulacji (co 1 symulowaną sekundę).

**Kolumny:**

- `timestamp` (float) - Czas symulacji [s]
- `vehicles_in_motion` (int) - Liczba pojazdów aktualnie w ruchu
- `average_speed` (float) - Średnia prędkość wszystkich pojazdów [km/h]
- `jam_length` (float) - Długość obszarów korków [km]
- `green_lights_count` (int) - Liczba zielonych sygnalizatorów
- `bus_lane_utilization` (int) - Pojazdy na buspassie (0 jeśli brak buspasa)
- `vehicles_in_queue` (int) - Pojazdy oczekujące na wjazd

**Przykład:**

```csv
timestamp,vehicles_in_motion,average_speed,jam_length,green_lights_count,bus_lane_utilization,vehicles_in_queue
0.0,0,0.0,0.0,2,0,0
10.0,15,48.5,0.12,1,3,2
20.0,28,35.2,0.25,2,5,0
```

### 3. \*\_config.csv - Metadane Konfiguracji

Podstawowe informacje o parametrach symulacji.

**Kolumny:**

- `simulation_id` (str) - Identyfikator symulacji
- `num_lanes` (int) - Liczba pasów regularnych
- `has_bus_lane` (bool) - Czy ma buspas
- `road_length` (float) - Długość drogi głównej [km]
- `privileged_percentage` (float) - Procent autobusów [0-1]
- `simulation_duration` (float) - Czas trwania symulacji [s]
- `traffic_light_positions` (str) - Pozycje sygnalizatorów [km] (lista jako string)
- `bus_lane_capacity` (int) - Pojemność buspasa [pojazdy/km]

**Przykład:**

```csv
simulation_id,num_lanes,has_bus_lane,road_length,privileged_percentage,simulation_duration,traffic_light_positions,bus_lane_capacity
variant_b_20251208_153327,2,True,5.0,0.05,3600.0,"[1.0, 2.5, 4.0]",75
```

### 4. \*\_lane_capacity.csv - Analiza Pojemności Pasów

Wykorzystanie rzeczywiste vs teoretyczne każdego pasa.

**Kolumny:**

- `simulation_id` (str) - Identyfikator symulacji
- `lane_id` (str) - Identyfikator pasa ("lane_0", "lane_1", "bus_lane", "summary")
- `lane_type` (str) - Typ pasa: "regular", "bus", "summary"
- `vehicle_count` (int) - Liczba pojazdów, które korzystały z pasa
- `actual_capacity_per_km` (float) - Rzeczywista pojemność [pojazdy/km]
- `theoretical_capacity_per_km` (int) - Teoretyczna pojemność [pojazdy/km]
- `utilization_percent` (float) - Wykorzystanie w procentach

**Przykład:**

```csv
simulation_id,lane_id,lane_type,vehicle_count,actual_capacity_per_km,theoretical_capacity_per_km,utilization_percent
variant_b_20251208_153327,lane_0,regular,142,28.4,75,37.9
variant_b_20251208_153327,lane_1,regular,138,27.6,75,36.8
variant_b_20251208_153327,bus_lane,bus,67,13.4,75,17.9
variant_b_20251208_153327,summary,summary,347,69.4,225,30.8
```

### 5. \*\_traffic_lights.csv - Stan Sygnalizacji

Historia zmian sygnalizacji podczas symulacji.

**Kolumny:**

- `timestamp` (float) - Czas zmiany stanu [s]
- `light_id` (int) - Numer sygnalizatora
- `position` (float) - Pozycja na drodze [km]
- `state` (str) - Stan sygnalizatora ("green", "red")
- `phase` (str) - Faza cyklu ("green", "red")
- `cycle_time` (float) - Długość pełnego cyklu [s]

**Przykład:**

```csv
timestamp,light_id,position,state,phase,cycle_time
0.0,0,1.0,green,green,67.5
67.5,0,1.0,red,red,67.5
135.0,0,1.0,green,green,67.5
202.5,0,1.0,red,red,67.5
```

---

## Krótki Opis Metod w Klasach

### simulation/traffic_simulation.py - TrafficSimulation

**Odpowiedzialność**: Główna klasa zarządzająca symulacją ruchu drogowego

**Docstring**: "Główna klasa symulacji ruchu drogowego"

#### Metody:

- `__init__(config: RoadConfiguration, params: SimulationParameters, infrastructure_config: Optional[InfrastructureConfig] = None)`

  - **Docstring**: Inicjalizuje symulację z konfiguracją i parametrami
  - **Argumenty**:
    - `config` - wariant konfiguracji drogi
    - `params` - parametry symulacji
    - `infrastructure_config` - opcjonalna niestandardowa konfiguracja infrastruktury

- `get_infrastructure_parameters() -> Dict[str, Any]`

  - **Docstring**: "Zwraca parametry infrastruktury na podstawie konfiguracji lub wariantu"
  - **Argumenty**: brak
  - **Zwraca**: słownik z parametrami infrastruktury

- `get_configuration_description() -> str`

  - **Docstring**: "Zwraca szczegółowy opis konfiguracji infrastruktury"
  - **Argumenty**: brak
  - **Zwraca**: tekstowy opis konfiguracji

- `get_short_configuration_description() -> str`

  - **Docstring**: "Zwraca krótki opis konfiguracji do wykresów"
  - **Argumenty**: brak
  - **Zwraca**: skrócony opis konfiguracji

- `setup_infrastructure(num_lanes: int, has_bus_lane: bool, bus_lane_capacity: int, traffic_light_positions: List[float], green_ratio: float = 0.6, cycle_duration: float = None)`

  - **Docstring**: "Konfiguracja infrastruktury na podstawie przekazanych parametrów"
  - **Argumenty**:
    - `num_lanes` - liczba pasów regularnych
    - `has_bus_lane` - czy ma buspas
    - `bus_lane_capacity` - pojemność buspasa
    - `traffic_light_positions` - pozycje sygnalizacji na drodze
    - `green_ratio` - stosunek czasu zielonego do pełnego cyklu
    - `cycle_duration` - długość cyklu sygnalizacji (opcjonalne)

- `generate_traffic_intensity() -> float`

  - **Docstring**: Generuje natężenie ruchu zgodnie z parametrami symulacji
  - **Argumenty**: brak
  - **Zwraca**: liczbę pojazdów do wygenerowania w danym kroku

- `should_vehicle_turn() -> bool`

  - **Docstring**: Określa czy pojazd skręci w boczną drogę na podstawie prawdopodobieństwa
  - **Argumenty**: brak
  - **Zwraca**: True jeśli pojazd powinien skręcić

- `assign_turn_position() -> float`

  - **Docstring**: Losowo przypisuje pozycję skrętu pojazdu
  - **Argumenty**: brak
  - **Zwraca**: pozycja skrętu na drodze głównej

- `process_vehicle_queue(max_capacity: int)`

  - **Docstring**: Przetwarza kolejkę pojazdów oczekujących na wjazd
  - **Argumenty**:
    - `max_capacity` - maksymalna pojemność drogi

- `generate_vehicle() -> Vehicle`

  - **Docstring**: "Generuje nowy pojazd"
  - **Argumenty**: brak
  - **Zwraca**: nowy obiekt Vehicle

- `update_traffic_lights()`

  - **Docstring**: Aktualizuje stan sygnalizacji świetlnej według cykli
  - **Argumenty**: brak

- `calculate_vehicle_speed(vehicle: Vehicle) -> float`

  - **Docstring**: "Oblicza prędkość pojazdu na podstawie warunków ruchu"
  - **Argumenty**:
    - `vehicle` - pojazd dla którego obliczana jest prędkość
  - **Zwraca**: prędkość w km/h

- `can_enter_road_segment(lane: int) -> bool`

  - **Docstring**: Sprawdza czy pojazd może wjechać na początkowy segment drogi
  - **Argumenty**:
    - `lane` - numer pasa
  - **Zwraca**: True jeśli może wjechać

- `collect_simulation_data()`

  - **Docstring**: "Zbiera szczegółowe dane z aktualnego stanu symulacji"
  - **Argumenty**: brak

- `record_vehicle_data(vehicle: Vehicle, action: str)`

  - **Docstring**: Zapisuje szczegółowe dane o pojedynczym pojeździe
  - **Argumenty**:
    - `vehicle` - pojazd do zapisania
    - `action` - akcja pojazdu (entered, exited, queued, etc.)

- `move_vehicles()`

  - **Docstring**: "Przesuwa pojazdy i aktualizuje ich stan"
  - **Argumenty**: brak

- `calculate_traffic_jam_length() -> float`

  - **Docstring**: "Oblicza długość korka (pojazdy o prędkości < 10 km/h)"
  - **Argumenty**: brak
  - **Zwraca**: długość korka w kilometrach

- `calculate_bus_efficiency() -> float`

  - **Docstring**: "Oblicza efektywność buspasa porównując z podobnym scenariuszem bez buspasa"
  - **Argumenty**: brak
  - **Zwraca**: wskaźnik efektywności w procentach

- `step()`

  - **Docstring**: "Wykonuje jeden krok symulacji"
  - **Argumenty**: brak

- `run_simulation(save_data: bool = False, data_filename: str = None) -> Dict`

  - **Docstring**: "Uruchamia pełną symulację - zwraca tylko surowe dane"
  - **Argumenty**:
    - `save_data` - czy zapisać dane do plików CSV
    - `data_filename` - nazwa pliku do zapisu (opcjonalne)
  - **Zwraca**: słownik z podsumowaniem symulacji

- `_calculate_final_statistics()`

  - **Docstring**: "Oblicza końcowe statystyki symulacji"
  - **Argumenty**: brak

- `save_simulation_data_to_csv(base_filename: str = None)`

  - **Docstring**: "Zapisuje surowe dane symulacji do plików CSV"
  - **Argumenty**:
    - `base_filename` - bazowa nazwa plików (opcjonalne)

- `calculate_lane_utilization() -> Dict[str, Any]`
  - **Docstring**: "Oblicza rzeczywiste wykorzystanie każdego pasa na podstawie danych o pojazdach"
  - **Argumenty**: brak
  - **Zwraca**: słownik ze statystykami wykorzystania pasów

### simulation/vehicle.py

**VehicleType (Enum)**
**Odpowiedzialność**: Definiuje typy pojazdów w symulacji
**Docstring**: "Typy pojazdów w symulacji"

**Wartości**:

- `REGULAR = "regular"` - Pojazdy regularne (samochody osobowe, ciężarowe)
- `PRIVILEGED = "privileged"` - Pojazdy uprzywilejowane (autobusy komunikacji publicznej)

**Vehicle (dataclass)**
**Odpowiedzialność**: Reprezentuje pojedynczy pojazd z jego właściwościami
**Docstring**: "Klasa reprezentująca pojedynczy pojazd"

**Atrybuty** (brak metod - tylko dataclass):

- `id: int` - Unikalny identyfikator pojazdu
- `vehicle_type: VehicleType` - Typ pojazdu (REGULAR/PRIVILEGED)
- `entry_time: float` - Czas wjazdu na drogę główną [s]
- `current_position: float` - Aktualna pozycja na drodze [km]
- `speed: float` - Aktualna prędkość [km/h]
- `lane: int` - Numer pasa (-1 dla buspasa, 0+ dla regularnych)
- `will_turn: bool` - Czy pojazd będzie skręcał w boczną drogę
- `turn_position: Optional[float] = None` - Pozycja skrętu [km] (jeśli applicable)
- `waiting_time: float = 0.0` - Łączny czas oczekiwania [s]
- `travel_time: float = 0.0` - Łączny czas podróży [s]

### simulation/traffic_light.py - TrafficLight

**Odpowiedzialność**: Reprezentuje sygnalizację świetlną
**Docstring**: Klasa reprezentująca sygnalizację świetlną

#### Metody:

- `calculate_optimal_cycle(green_time: float) -> float` (metoda statyczna)
  - **Docstring**: Oblicza optymalny cykl sygnalizacji na podstawie czasu zielonego światła
  - **Argumenty**:
    - `green_time` - czas trwania zielonego światła [s]
  - **Zwraca**: optymalną długość pełnego cyklu [s]

**Atrybuty (dataclass)**:

- `position: float` - Pozycja sygnalizacji na drodze głównej [km]
- `cycle_duration: float` - Czas pełnego cyklu sygnalizacji [s]
- `green_duration: float` - Czas trwania zielonego światła [s]
- `current_phase: str` - Aktualny stan sygnalizacji ("green" lub "red")
- `phase_start_time: float` - Czas rozpoczęcia aktualnej fazy [s]

### simulation/simulation_parameters.py

**RoadConfiguration (Enum)**
**Odpowiedzialność**: Definiuje warianty konfiguracji dróg
**Docstring**: Enumeracja wariantów konfiguracji infrastruktury drogowej

**Wartości**:

- `VARIANT_A = "variant_a"` - Wariant A (3 pasy regularne, bez buspasa)
- `VARIANT_B = "variant_b"` - Wariant B (2 pasy regularne + buspas)
- `CUSTOM = "custom"` - Konfiguracja niestandardowa

**SimulationParameters (dataclass)**
**Odpowiedzialność**: Przechowuje wszystkie parametry symulacji
**Docstring**: Klasa parametrów symulacji ruchu drogowego

#### Metody:

- `__post_init__()`
  - **Docstring**: Ustawia domyślne pozycje dróg bocznych jeśli nie podano
  - **Argumenty**: brak

**Atrybuty**:

- `traffic_intensity_range: Tuple[int, int] = (500, 1500)` - Zakres natężenia ruchu [pojazdy/godzina]
- `turning_percentage_range: Tuple[float, float] = (0.05, 0.20)` - Zakres procentu pojazdów skręcających
- `privileged_percentage: float = 0.05` - Procent pojazdów uprzywilejowanych (autobusów)
- `road_length: float = 5.0` - Długość drogi głównej [km]
- `lane_capacity: int = 75` - Pojemność pasa [pojazdy/km]
- `traffic_light_cycle: float = 75.0` - Domyślny cykl sygnalizacji [s]
- `green_light_range: Tuple[float, float] = (45.0, 90.0)` - Zakres czasu zielonego światła [s]
- `simulation_duration: float = 3600.0` - Czas trwania symulacji [s]
- `time_step: float = 1.0` - Krok czasowy symulacji [s]
- `side_road_positions: List[float]` - Pozycje dróg bocznych [km]

### simulation/infrastructure_config.py - InfrastructureConfig

**Odpowiedzialność**: Konfiguracja infrastruktury drogowej
**Docstring**: Klasa konfiguracji infrastruktury drogowej

**Atrybuty (dataclass, brak metod)**:

- `num_lanes: int = 2` - Liczba pasów regularnych
- `has_bus_lane: bool = False` - Czy ma buspas
- `bus_lane_capacity: int = 0` - Pojemność buspasa [pojazdy/km]
- `traffic_light_positions: List[float]` - Pozycje sygnalizacji [km]
- `traffic_light_green_ratio: float = 0.6` - Stosunek czasu zielonego do cyklu
- `description: str = ""` - Opis konfiguracji

### analysis/comparison_analysis.py (funkcje)

**Odpowiedzialność**: Porównawcza analiza różnych scenariuszy ruchu
**Docstring modułu**: Funkcje analizy porównawczej wyników symulacji

#### Funkcje:

- `compare_bus_lane_efficiency() -> Dict`

  - **Docstring**: Porównuje efektywność buspasa analizując surowe dane CSV
  - **Argumenty**: brak
  - **Zwraca**: słownik z wynikami analizy efektywności

- `run_comparison_study(simulation_module) -> Dict[str, Dict]`

  - **Docstring**: Uruchamia porównawczą analizę wszystkich wariantów z plików CSV
  - **Argumenty**:
    - `simulation_module` - moduł symulacji
  - **Zwraca**: słownik z wynikami dla wszystkich wariantów

- `test_custom_configuration(sim_module, lane_count: int, bus_lane: bool, traffic_intensity: float, privileged_percentage: float, verbose: bool = True) -> Dict`

  - **Docstring**: Testuje niestandardową konfigurację uruchamiając symulację
  - **Argumenty**:
    - `sim_module` - moduł symulacji
    - `lane_count` - liczba pasów regularnych
    - `bus_lane` - czy dodać buspas
    - `traffic_intensity` - intensywność ruchu
    - `privileged_percentage` - procent autobusów
    - `verbose` - czy wyświetlać szczegółowe informacje
  - **Zwraca**: słownik z wynikami testu

- `test_direct_parameter_approach(simulation_module) -> Dict[str, Any]`

  - **Docstring**: "Demonstracja bezpośredniego wywołania metody z parametrami"
  - **Argumenty**:
    - `simulation_module` - moduł symulacji
  - **Zwraca**: słownik z wynikami demonstracji

- `analyze_efficiency_metrics(results: Dict) -> Dict`

  - **Docstring**: Analizuje metryki efektywności między scenariuszami
  - **Argumenty**:
    - `results` - słownik z wynikami symulacji
  - **Zwraca**: słownik z metrykami efektywności

- `display_efficiency_results(results: Dict) -> None`

  - **Docstring**: Wyświetla wyniki analizy efektywności w tabeli
  - **Argumenty**:
    - `results` - słownik z wynikami analizy
  - **Zwraca**: None (wyświetla na konsoli)

- `display_efficiency_conclusions(results: Dict) -> None`

  - **Docstring**: Wyświetla wnioski z analizy efektywności
  - **Argumenty**:
    - `results` - słownik z wynikami analizy
  - **Zwraca**: None (wyświetla na konsoli)

- `save_efficiency_results(results: Dict, filename: str = "efficiency_analysis.csv") -> None`

  - **Docstring**: Zapisuje wyniki efektywności do plików CSV
  - **Argumenty**:
    - `results` - słownik z wynikami
    - `filename` - nazwa pliku do zapisu
  - **Zwraca**: None

- `display_comparison_results(results: Dict[str, Dict]) -> None`

  - **Docstring**: Wyświetla analizę porównawczą wyników wszystkich wariantów
  - **Argumenty**:
    - `results` - słownik z wynikami dla wszystkich wariantów
  - **Zwraca**: None (wyświetla na konsoli)

- `display_variant_rankings(results: Dict[str, Dict]) -> None`

  - **Docstring**: Wyświetla rankingi wariantów według różnych metryk
  - **Argumenty**:
    - `results` - słownik z wynikami dla wszystkich wariantów
  - **Zwraca**: None (wyświetla na konsoli)

- `display_hypothesis_verification(results: Dict[str, Dict]) -> None`

  - **Docstring**: Weryfikuje hipotezy badawcze na podstawie wyników
  - **Argumenty**:
    - `results` - słownik z wynikami dla wszystkich wariantów
  - **Zwraca**: None (wyświetla na konsoli)

- `display_recommendations(results: Dict[str, Dict]) -> None`
  - **Docstring**: Wyświetla rekomendacje najlepszych wariantów
  - **Argumenty**:
    - `results` - słownik z wynikami dla wszystkich wariantów
  - **Zwraca**: None (wyświetla na konsoli)

### analysis/data_loader.py (funkcje)

**Odpowiedzialność**: Ładowanie i przetwarzanie danych symulacji
**Docstring modułu**: "Data loading and processing functions for simulation analysis"

#### Funkcje:

- `load_raw_simulation_data(data_dir: str, pattern: str) -> Dict[str, Any]`

  - **Docstring**: "Ładuje surowe dane symulacji z plików CSV i oblicza statystyki"
  - **Argumenty**:
    - `data_dir` - katalog z plikami danych
    - `pattern` - wzorzec nazwy pliku (np. 'variant_a', 'scenario_b')
  - **Zwraca**: słownik ze statystykami obliczonymi z surowych danych

- `calculate_statistics_from_raw_data(vehicles_df: pd.DataFrame, config: pd.Series) -> Dict[str, Any]`

  - **Docstring**: "Oblicza statystyki z surowych danych o pojazdach"
  - **Argumenty**:
    - `vehicles_df` - DataFrame z danymi o pojazdach
    - `config` - Series z konfiguracją symulacji
  - **Zwraca**: słownik ze statystykami

- `calculate_jam_length_from_data(vehicles_df: pd.DataFrame) -> float`

  - **Docstring**: Oblicza długość korka na podstawie danych o pojazdach
  - **Argumenty**:
    - `vehicles_df` - DataFrame z danymi o pojazdach
  - **Zwraca**: długość korka w kilometrach

- `calculate_bus_efficiency_from_data(vehicles_df: pd.DataFrame) -> float`
  - **Docstring**: Oblicza efektywność buspasa z danych o pojazdach
  - **Argumenty**:
    - `vehicles_df` - DataFrame z danymi o pojazdach
  - **Zwraca**: wskaźnik efektywności buspasa w procentach

### analysis/lane_analysis.py (funkcje)

**Odpowiedzialność**: Analiza pojemności i wykorzystania pasów ruchu
**Docstring modułu**: "Lane capacity analysis functions"

#### Funkcje:

- `analyze_lane_capacity(data_dir: str, pattern: str) -> Dict[str, Any]`

  - **Docstring**: "Analizuje pojemność i wykorzystanie pasów z pliku lane_capacity.csv"
  - **Argumenty**:
    - `data_dir` - katalog z danymi
    - `pattern` - wzorzec nazwy pliku (np. 'scenario_a', 'variant_b')
  - **Zwraca**: słownik z analizą pojemności pasów

- `print_lane_capacity_analysis(analysis: Dict[str, Any]) -> None`

  - **Docstring**: "Wyświetla analizę pojemności pasów w czytelnej formie"
  - **Argumenty**:
    - `analysis` - słownik z wynikami analizy pojemności
  - **Zwraca**: None (wyświetla na konsoli)

- `analyze_all_lane_capacities(data_dir: str = "simulation_data") -> Dict[str, Dict[str, Any]]`

  - **Docstring**: Analizuje pojemność pasów dla wszystkich dostępnych symulacji
  - **Argumenty**:
    - `data_dir` - katalog z danymi symulacji (domyślnie "simulation_data")
  - **Zwraca**: słownik z analizami dla wszystkich symulacji

- `print_all_lane_capacities_summary(data_dir: str = "simulation_data") -> None`
  - **Docstring**: Wyświetla podsumowanie pojemności pasów wszystkich symulacji
  - **Argumenty**:
    - `data_dir` - katalog z danymi (domyślnie "simulation_data")
  - **Zwraca**: None (wyświetla na konsoli)

### analysis/visualization.py (funkcje)

**Odpowiedzialność**: Tworzenie wizualizacji wyników symulacji
**Docstring modułu**: Funkcje tworzenia wykresów i wizualizacji wyników

#### Funkcje:

- `create_visualization(results: Dict, chart_name: str, sim_module) -> None`
  - **Docstring**: Tworzy wykresy słupkowe porównujące różne warianty
  - **Argumenty**:
    - `results` - słownik z wynikami symulacji
    - `chart_name` - nazwa wykresów do zapisu
    - `sim_module` - moduł symulacji (do opisu wariantów)
  - **Zwraca**: None (zapisuje wykresy do plików PNG)
  - **Generuje wykresy**: średni czas przejazdu, średnia prędkość, długość korków, efektywność buspasa

### trivial_cases_tester.py - AllBusTester

**Odpowiedzialność**: Testowanie przypadków z samymi autobusami (100%)
**Docstring**: Klasa do testowania przypadków trywialnych z 100% autobusów

#### Metody:

- `__init__(base_seed: int = 42)`

  - **Docstring**: Inicjalizuje tester z bazowym seedem dla powtarzalności
  - **Argumenty**:
    - `base_seed` - ziarno generatora liczb losowych (domyślnie 42)

- `get_all_bus_parameters() -> SimulationParameters`

  - **Docstring**: Zwraca parametry symulacji z 100% autobusów
  - **Argumenty**: brak
  - **Zwraca**: obiekt SimulationParameters z privileged_percentage=1.0

- `get_high_intensity_parameters() -> SimulationParameters`

  - **Docstring**: Zwraca parametry z wysoką intensywnością ruchu
  - **Argumenty**: brak
  - **Zwraca**: obiekt SimulationParameters z wysoką intensywnością

- `test_all_bus_scenarios() -> Dict[str, Dict]`

  - **Docstring**: Testuje różne konfiguracje infrastruktury z 100% autobusów
  - **Argumenty**: brak
  - **Zwraca**: słownik z wynikami testów różnych konfiguracji

- `test_equivalent_configurations() -> Dict[str, Dict]`

  - **Docstring**: Test równoważności 1 pasa zwykłego vs 1 buspasa przy 100% autobusów
  - **Argumenty**: brak
  - **Zwraca**: słownik z wynikami testu równoważności

- `test_high_intensity_scenarios() -> Dict[str, Dict]`

  - **Docstring**: Testuje przypadki z dużą intensywnością ruchu dla reprezentatywności
  - **Argumenty**: brak
  - **Zwraca**: słownik z wynikami testów wysokiej intensywności

- `calculate_statistics(simulation) -> Dict[str, float]`

  - **Docstring**: Oblicza statystyki z obiektu symulacji (metoda pomocnicza)
  - **Argumenty**:
    - `simulation` - obiekt symulacji TrafficSimulation
  - **Zwraca**: słownik ze statystykami

- `analyze_results(results: Dict[str, Dict]) -> None`

  - **Docstring**: Analizuje wyniki testów z samymi autobusami
  - **Argumenty**:
    - `results` - słownik z wynikami testów
  - **Zwraca**: None (wyświetla analizę na konsoli)

- `save_results(results: Dict[str, Dict], filename: str = "trivial_tests_results.csv") -> None`

  - **Docstring**: Zapisuje podsumowanie wyników testów do pliku CSV
  - **Argumenty**:
    - `results` - słownik z wynikami
    - `filename` - nazwa pliku do zapisu
  - **Zwraca**: None

- `run_all_tests() -> Dict[str, Dict]`

  - **Docstring**: Uruchamia kompletny zestaw testów z samymi autobusami
  - **Argumenty**: brak
  - **Zwraca**: słownik z wszystkimi wynikami testów

- `main() -> int` (metoda statyczna)
  - **Docstring**: Główna funkcja uruchamiająca tester interaktywnie
  - **Argumenty**: brak
  - **Zwraca**: kod wyjścia (0 = sukces)

---

## Przykłady Uruchomienia

### Podstawowe Uruchomienie z Menu Interaktywnym

```bash
python main.py
```

Po uruchomieniu pojawi się menu z opcjami:

- Uruchom symulację ruchu
- Uruchom analizę danych
- Uruchom testy przypadków trywialnych
- Wyjdź

### Bezpośrednie Uruchomienie Modułów

```bash
# Tylko symulacja
python main.py simulate

# Tylko analiza
python main.py analyze

# Tylko testy
python main.py test
```

### Uruchomienie Symulacji z Parametrami

```bash
# Symulacja z wielokrotnymi powtórzeniami
python simulation_main.py --reruns 5 --seed 123

# Symulacja interaktywna
python simulation_main.py
```

Menu symulacji oferuje:

1. Wszystkie standardowe warianty (A, B, C, D)
2. Wariant A (3P) - 3 pasy regularne
3. Wariant B (2P+Bus) - 2 pasy + buspas
4. Wariant C (3P+Bus) - 3 pasy + buspas
5. Wariant D (4P) - 4 pasy regularne
6. Niestandardowy wariant

### Uruchomienie Analizy

```bash
python analysis_main.py
```

Menu analizy oferuje:

1. Porównanie wszystkich wariantów
2. Analiza efektywności buspasa
3. Test niestandardowej konfiguracji
4. Analiza pojemności pasów
5. Wszystkie powyższe

### Programowe Użycie API

#### Przykład 1: Podstawowa Symulacja

```python
#!/usr/bin/env python3
import simulation

# Utwórz parametry symulacji
params = simulation.SimulationParameters()
params.privileged_percentage = 0.15  # 15% autobusów
params.simulation_duration = 1800.0  # 30 minut

# Uruchom wariant A (3 pasy, bez buspasa)
sim_a = simulation.TrafficSimulation(simulation.RoadConfiguration.VARIANT_A, params)
result_a = sim_a.run_simulation()

# Uruchom wariant B (2 pasy + buspas)
sim_b = simulation.TrafficSimulation(simulation.RoadConfiguration.VARIANT_B, params)
result_b = sim_b.run_simulation()

# Porównaj wyniki
print(f"Wariant A: {result_a['completed_vehicles']} pojazdów")
print(f"Wariant B: {result_b['completed_vehicles']} pojazdów")
print(f"Średni czas A: {result_a['avg_travel_time']:.1f}s")
print(f"Średni czas B: {result_b['avg_travel_time']:.1f}s")
```

#### Przykład 2: Niestandardowa Konfiguracja

```python
#!/usr/bin/env python3
from simulation import create_simulation_with_parameters, SimulationParameters

# Zdefiniuj parametry symulacji
params = SimulationParameters()
params.traffic_intensity_range = (800, 1200)
params.privileged_percentage = 0.20

# Konfiguracja infrastruktury
infra_params = {
    'num_lanes': 2,
    'has_bus_lane': True,
    'bus_lane_capacity': 100,
    'traffic_light_positions': [1.5, 3.5],
    'green_ratio': 0.7,
    'cycle_duration': 80.0
}

# Utwórz i uruchom symulację
sim = create_simulation_with_parameters(params, infra_params)
result = sim.run_simulation(save_data=True, data_filename="custom_test")

# Wyniki
print(f"Konfiguracja: {sim.get_configuration_description()}")
print(f"Ukończone pojazdy: {result['completed_vehicles']}")
print(f"Efektywność buspasa: {result['bus_efficiency']:.1f}%")
```

#### Przykład 3: Analiza Surowych Danych

```python
#!/usr/bin/env python3
import analysis

# Załaduj dane z symulacji
stats = analysis.load_raw_simulation_data("simulation_data", "variant_b_20251208_153327")

# Wyświetl podstawowe statystyki
print(f"Średni czas przejazdu: {stats['avg_travel_time']:.1f}s")
print(f"Średnia prędkość: {stats['avg_speed']:.1f} km/h")
print(f"Współczynnik ukończenia: {stats['completion_rate']:.1%}")
print(f"Średnia długość korka: {stats['avg_jam_length']:.3f} km")
print(f"Efektywność buspasa: {stats['bus_efficiency']:.1f}%")

# Szczegółowa analiza pojemności pasów
lane_stats = analysis.analyze_lane_capacity("simulation_data", "variant_b_20251208_153327")
analysis.print_lane_capacity_analysis(lane_stats)
```

#### Przykład 4: Batch Analysis

```python
#!/usr/bin/env python3
import os
import glob
import analysis

# Znajdź wszystkie pliki symulacji
data_dir = "simulation_data"
simulation_files = glob.glob(f"{data_dir}/*_config.csv")

results = {}
for config_file in simulation_files:
    # Wyciągnij ID symulacji z nazwy pliku
    simulation_id = os.path.basename(config_file).replace("_config.csv", "")

    try:
        # Załaduj i przeanalizuj
        stats = analysis.calculate_statistics_from_raw_data(data_dir, simulation_id)
        results[simulation_id] = stats
        print(f"✓ {simulation_id}: avg_time={stats['avg_travel_time']:.1f}s")
    except Exception as e:
        print(f"✗ Błąd dla {simulation_id}: {e}")

# Stwórz ranking
sorted_results = sorted(results.items(), key=lambda x: x[1]['avg_travel_time'])
print("\nRANKING (najkrótszy czas przejazdu):")
for i, (sim_id, stats) in enumerate(sorted_results, 1):
    print(f"{i}. {sim_id}: {stats['avg_travel_time']:.1f}s")
```

### Uruchomienie Testów Trywialnych

```bash
python trivial_cases_tester.py
```

Tester uruchamia przypadki z 100% autobusów w celu walidacji modelu:

- Test równoważności konfiguracji
- Scenariusze z różną infrastrukturą
- Przypadki z wysoką intensywnością ruchu
