from dataclasses import dataclass
from datetime import datetime


@dataclass
class ImpactInput:

    latitude: float

    longitude: float

    spill_area: float

    predicted_path: list

    risk_zones: list

    timestamp: datetime