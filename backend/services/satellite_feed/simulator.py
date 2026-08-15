from pathlib import Path
from datetime import datetime

from backend.services.satellite_feed.base import FeedFrame, SatelliteFeed
from backend.config import settings


class SimulatorFeed(SatelliteFeed):
    """
    Streams satellite frames from a directory of images.

    Used for the demo and CI: no credentials needed, one frame
    per poll, looping through the available images. Each frame
    embeds the configured incident coordinates.
    """

    IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".tif", ".tiff")

    def __init__(self, images_dir=None, latitude=None, longitude=None):

        super().__init__()

        self.images_dir = Path(images_dir or settings.simulator_images_dir)

        self.latitude = latitude or settings.incident_latitude

        self.longitude = longitude or settings.incident_longitude

        self.image_paths = []

    def connect(self):

        if not self.images_dir.exists():

            raise FileNotFoundError(
                f"Simulator image directory not found: {self.images_dir}"
            )

        self.image_paths = sorted(
            str(path)
            for path in self.images_dir.iterdir()
            if path.suffix.lower() in self.IMAGE_EXTENSIONS
        )

        if not self.image_paths:

            raise FileNotFoundError(
                f"No satellite images found in: {self.images_dir}"
            )

        self._connected = True

        return True

    def disconnect(self):

        self._connected = False

    def get_frame(self):

        if not self._connected:

            self.connect()

        path = self.image_paths[self.frames_served % len(self.image_paths)]

        self.frames_served += 1

        return FeedFrame(
            frame_id=self.frames_served,
            image_path=path,
            latitude=self.latitude,
            longitude=self.longitude,
            timestamp=datetime.now(),
            source="simulator",
        )

    def status(self):

        return {
            "source": "simulator",
            "connected": self._connected,
            "frames_served": self.frames_served,
            "images_available": len(self.image_paths),
            "directory": str(self.images_dir),
        }
