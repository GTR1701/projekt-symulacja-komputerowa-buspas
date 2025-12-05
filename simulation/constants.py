"""
Constants used in traffic simulation
"""

# Wymiary pojazdów
VEHICLE_LENGTH = 0.0045  # km - średnia długość pojazdu (4.5m)
VEHICLE_SPACING = 0.0005  # km - minimalna odległość między pojazdami (0.5m) 
VEHICLE_TOTAL_SPACE = VEHICLE_LENGTH + VEHICLE_SPACING  # 5m całkowite zajęcie drogi

# Progi detekcji ruchu
JAM_THRESHOLD_DISTANCE = 0.050  # km - odległość < 50m = korek (zatłoczony ruch miejski)
DETECTION_DISTANCE = 0.500  # km - odległość sprawdzania pojazdów z przodu (500m)

# Prędkości i ruch
BASE_VEHICLE_SPEED = 50.0  # km/h - podstawowa prędkość pojazdu w ruchu miejskim
SLOW_TRAFFIC_THRESHOLD = 10.0  # km/h - prędkość poniżej której ruch uznawany za zakorkowany
TRAFFIC_LIGHT_STOPPING_DISTANCE = 0.1  # km - odległość od świateł przy której pojazd zatrzymuje się na czerwonym

# Parametry ruchu
MIN_DENSITY_FACTOR = 0.1  # minimalna wartość współczynnika gęstości ruchu
DENSITY_REDUCTION_RATE = 0.15  # o ile zmniejsza się prędkość na każdy pojazd z przodu
SECONDS_PER_HOUR = 3600  # konwersja sekund na godziny

# Pozycje domyślne sygnalizacji
DEFAULT_SIDE_ROAD_POSITIONS = [1.0, 2.5, 4.0]  # km - domyślne pozycje dróg bocznych

# Analiza efektywności buspasa
BUS_EFFICIENCY_TIME_WEIGHT = 0.7  # waga czasu w kalkulacji efektywności buspasa
BUS_EFFICIENCY_SPEED_WEIGHT = 0.3  # waga prędkości w kalkulacji efektywności buspasa