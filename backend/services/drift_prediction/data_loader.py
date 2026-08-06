from pathlib import Path
import math

import pandas as pd
import requests


class EnvironmentalDataLoader:
    def get_nearest_current(
        self,
        latitude,
        longitude,
    ):

        currents = self.load_ocean_currents()

        nearest = None
        minimum_distance = float("inf")

        for _, row in currents.iterrows():

            distance = math.sqrt(
                (latitude - row["latitude"]) ** 2 +
                (longitude - row["longitude"]) ** 2
            )

            if distance < minimum_distance:
                minimum_distance = distance
                nearest = row

        return nearest

    def __init__(self):

        self.current_path = (
            Path("dataset")
            / "environmental"
            / "mock_ocean_current.csv"
        )

    def load_ocean_currents(self):

        if not self.current_path.exists():
            raise FileNotFoundError(
                f"Ocean current file not found: {self.current_path}"
            )

        df = pd.read_csv(self.current_path)

        required = [
            "latitude",
            "longitude",
            "current_speed",
            "current_direction",
        ]

        for column in required:
            if column not in df.columns:
                raise ValueError(
                    f"Missing column: {column}"
                )

        return df

    def load_live_weather(
        self,
        latitude,
        longitude,
    ):

        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={latitude}"
            f"&longitude={longitude}"
            "&current=wind_speed_10m,wind_direction_10m"
        )

        response = requests.get(
            url,
            timeout=15
        )

        response.raise_for_status()

        data = response.json()["current"]

        return {
            "wind_speed": data["wind_speed_10m"],
            "wind_direction": data["wind_direction_10m"],
        }