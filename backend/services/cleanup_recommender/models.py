from dataclasses import dataclass


@dataclass
class CleanupInput:

    spill_area: float

    distance_to_coast: float

    risk_level: str

    wind_speed: float

    current_speed: float