from dataclasses import dataclass
from datetime import datetime


@dataclass
class SpillData:

    latitude: float

    longitude: float

    area: float

    timestamp: datetime