import math

from backend.services.drift_prediction.models import SpillData
from backend.services.drift_prediction.data_loader import (
    EnvironmentalDataLoader,
)


class DriftPredictor:

    def __init__(self):
        self.loader = EnvironmentalDataLoader()

    def predict(
        self,
        spill: SpillData,
        hours=24,
        interval=1,
    ):

        # Load live weather
        weather = self.loader.load_live_weather(
            spill.latitude,
            spill.longitude,
        )

        # Load nearest ocean current
        current = self.loader.get_nearest_current(
            spill.latitude,
            spill.longitude,
        )

        latitude = spill.latitude
        longitude = spill.longitude

        predictions = []

        for hour in range(
            interval,
            hours + 1,
            interval,
        ):

            # -----------------------------
            # Wind Vector
            # -----------------------------

            wind_speed = weather["wind_speed"] * 0.03

            wind_direction = math.radians(
                weather["wind_direction"]
            )

            wind_x = wind_speed * math.sin(
                wind_direction
            )

            wind_y = wind_speed * math.cos(
                wind_direction
            )

            # -----------------------------
            # Ocean Current Vector
            # -----------------------------

            current_speed = current["current_speed"]

            current_direction = math.radians(
                current["current_direction"]
            )

            current_x = current_speed * math.sin(
                current_direction
            )

            current_y = current_speed * math.cos(
                current_direction
            )

            # -----------------------------
            # Combined Drift Vector
            # -----------------------------

            total_x = wind_x + current_x
            total_y = wind_y + current_y

            delta_lat = total_y / 111

            delta_lon = total_x / (
                111
                * math.cos(
                    math.radians(latitude)
                )
            )

            latitude += delta_lat
            longitude += delta_lon

            predictions.append(
                {
                    "hour": hour,

                    "latitude": latitude,

                    "longitude": longitude,

                    "wind_speed": round(
                        weather["wind_speed"], 2
                    ),

                    "wind_direction": round(
                        weather["wind_direction"], 2
                    ),

                    "current_speed": round(
                        current["current_speed"], 2
                    ),

                    "current_direction": round(
                        current["current_direction"], 2
                    ),

                    "estimated_speed": round(
                        math.sqrt(
                            total_x ** 2 +
                            total_y ** 2
                        ),
                        2,
                    ),
                }
            )

        return predictions