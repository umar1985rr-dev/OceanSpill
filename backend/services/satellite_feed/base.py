from abc import ABC, abstractmethod

from dataclasses import dataclass
from datetime import datetime


@dataclass
class FeedFrame:
    """
    One satellite frame delivered by a feed.

    Carries everything the monitoring service needs to run
    detection and locate the spill.
    """

    frame_id: int

    image_path: str

    latitude: float

    longitude: float

    timestamp: datetime

    source: str


class SatelliteFeed(ABC):
    """
    Pluggable satellite imagery source.

    Implementations stream satellite frames so the monitoring
    service can run detection on each one. A simulator streams
    dataset images; a real connector (Sentinel Hub) downloads
    live tiles behind the same interface.
    """

    def __init__(self):

        self.frames_served = 0

        self._connected = False

    @abstractmethod
    def connect(self):
        """
        Open the feed connection.
        """

        raise NotImplementedError

    @abstractmethod
    def disconnect(self):
        """
        Close the feed connection.
        """

        raise NotImplementedError

    @abstractmethod
    def get_frame(self):
        """
        Return the next FeedFrame, or None when no frame is
        available yet.
        """

        raise NotImplementedError

    @abstractmethod
    def status(self):
        """
        Return feed diagnostics as a dict.
        """

        raise NotImplementedError
