from dataclasses import dataclass
from datetime import datetime


@dataclass
class SpillLocation:
    """
    Represents one detected oil spill.
    """

    latitude: float
    longitude: float
    timestamp: datetime