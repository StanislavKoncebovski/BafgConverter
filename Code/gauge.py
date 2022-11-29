from dataclasses import dataclass

@dataclass
class Gauge:
    grid_number: int = 0
    river: str = ''
    station: str = ''