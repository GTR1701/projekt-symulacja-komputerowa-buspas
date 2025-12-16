"""
Constants used in traffic simulation
"""

# Długości pojazdów - różne dla aut osobowych i autobusów
CAR_LENGTH = 0.0045      # ~4.5m dla samochodu osobowego
BUS_LENGTH = 0.0120      # ~12m dla autobusu
VEHICLE_SPACING = 0.0005  # Odstęp między pojazdami

# Przestrzeń zajmowana przez pojazdy (długość + odstęp)
CAR_TOTAL_SPACE = CAR_LENGTH + VEHICLE_SPACING
BUS_TOTAL_SPACE = BUS_LENGTH + VEHICLE_SPACING

# Do kompatybilności pliku z analizą. Docelowo usunąć
VEHICLE_TOTAL_SPACE = CAR_TOTAL_SPACE

JAM_THRESHOLD_DISTANCE = 0.050
DETECTION_DISTANCE = 0.500

BASE_VEHICLE_SPEED = 50.0
SLOW_TRAFFIC_THRESHOLD = 10.0
TRAFFIC_LIGHT_STOPPING_DISTANCE = 0.1

MIN_DENSITY_FACTOR = 0.1
DENSITY_REDUCTION_RATE = 0.15
SECONDS_PER_HOUR = 3600

DEFAULT_SIDE_ROAD_POSITIONS = [0.5]

BUS_EFFICIENCY_TIME_WEIGHT = 0.7
BUS_EFFICIENCY_SPEED_WEIGHT = 0.3