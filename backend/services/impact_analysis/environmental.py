import math

from backend.services.impact_analysis import (
    ImpactDataLoader,
)


class EnvironmentalImpactAnalyzer:

    def __init__(self):

        self.loader = ImpactDataLoader()

    def distance(
        self,
        lat1,
        lon1,
        lat2,
        lon2,
    ):

        R = 6371

        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)

        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(math.radians(lat1))
            * math.cos(math.radians(lat2))
            * math.sin(dlon / 2) ** 2
        )

        c = 2 * math.atan2(
            math.sqrt(a),
            math.sqrt(1 - a),
        )

        return R * c

    def nearest_distance(
        self,
        dataframe,
        latitude,
        longitude,
    ):

        distances = []

        for _, row in dataframe.iterrows():

            distances.append(

                self.distance(

                    latitude,
                    longitude,

                    row["Latitude"],
                    row["Longitude"],

                )

            )

        return min(distances)

    def get_risk(
        self,
        distance,
    ):

        if distance <= 5:
            return "Critical"

        elif distance <= 10:
            return "High"

        elif distance <= 20:
            return "Medium"

        else:
            return "Low"

    def analyze(
        self,
        impact_input,
    ):

        coast = self.loader.load_coastlines()

        protected = self.loader.load_protected_areas()

        mangroves = self.loader.load_mangroves()

        reefs = self.loader.load_coral_reefs()

        fishing = self.loader.load_fishing_zones()

        coast_distance = self.nearest_distance(
            coast,
            impact_input.latitude,
            impact_input.longitude,
        )

        protected_distance = self.nearest_distance(
            protected,
            impact_input.latitude,
            impact_input.longitude,
        )

        mangrove_distance = self.nearest_distance(
            mangroves,
            impact_input.latitude,
            impact_input.longitude,
        )

        reef_distance = self.nearest_distance(
            reefs,
            impact_input.latitude,
            impact_input.longitude,
        )

        fishing_distance = self.nearest_distance(
            fishing,
            impact_input.latitude,
            impact_input.longitude,
        )

        return {

            "Nearest Coastline": {

                "distance": round(
                    coast_distance,
                    2,
                ),

                "risk": self.get_risk(
                    coast_distance,
                ),

            },

            "Nearest Protected Area": {

                "distance": round(
                    protected_distance,
                    2,
                ),

                "risk": self.get_risk(
                    protected_distance,
                ),

            },

            "Nearest Mangrove": {

                "distance": round(
                    mangrove_distance,
                    2,
                ),

                "risk": self.get_risk(
                    mangrove_distance,
                ),

            },

            "Nearest Coral Reef": {

                "distance": round(
                    reef_distance,
                    2,
                ),

                "risk": self.get_risk(
                    reef_distance,
                ),

            },

            "Nearest Fishing Zone": {

                "distance": round(
                    fishing_distance,
                    2,
                ),

                "risk": self.get_risk(
                    fishing_distance,
                ),

            },

        }