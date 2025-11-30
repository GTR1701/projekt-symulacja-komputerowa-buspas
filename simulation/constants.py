"""
Constants used in traffic simulation
"""

VEHICLE_LENGTH = 0.0045  # km - średnia długość pojazdu (4.5m)
VEHICLE_SPACING = 0.0005  # km - minimalna odległość między pojazdami (0.5m) 
VEHICLE_TOTAL_SPACE = VEHICLE_LENGTH + VEHICLE_SPACING  # 5m całkowite zajęcie drogi
JAM_THRESHOLD_DISTANCE = 0.050  # km - odległość < 50m = korek (zatłoczony ruch miejski)
DETECTION_DISTANCE = 0.500  # km - odległość sprawdzania pojazdów z przodu (500m)