import numpy as np

from math import radians


class NearbyVesselFinder:

    EARTH_RADIUS_KM = 6371

    @staticmethod
    def haversine(
        lat1,
        lon1,
        lat2,
        lon2,
    ):
        """
        Calculate the distance between two GPS points.
        """

        lat1 = radians(lat1)
        lon1 = radians(lon1)

        lat2 = radians(lat2)
        lon2 = radians(lon2)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = (
            np.sin(dlat / 2) ** 2
            + np.cos(lat1)
            * np.cos(lat2)
            * np.sin(dlon / 2) ** 2
        )

        c = 2 * np.arctan2(
            np.sqrt(a),
            np.sqrt(1 - a)
        )

        return NearbyVesselFinder.EARTH_RADIUS_KM * c

    def find_nearby(
        self,
        dataframe,
        spill,
        radius_km=20,
    ):
        """
        Return all vessels within radius_km of the spill as a
        DataFrame (with a Distance_km column added).

        The haversine distance is computed vectorized over the
        whole dataframe (numpy) instead of row-by-row, so this
        stays fast even for millions of AIS records.
        """

        # Vectorized haversine over every vessel
        lat1 = np.radians(spill.latitude)
        lon1 = np.radians(spill.longitude)

        lat2 = np.radians(dataframe["LAT"].to_numpy(dtype=float))
        lon2 = np.radians(dataframe["LON"].to_numpy(dtype=float))

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = (
            np.sin(dlat / 2) ** 2
            + np.cos(lat1)
            * np.cos(lat2)
            * np.sin(dlon / 2) ** 2
        )

        c = 2 * np.arctan2(
            np.sqrt(a),
            np.sqrt(1 - a),
        )

        distances = self.EARTH_RADIUS_KM * c

        # Keep only vessels inside the radius
        mask = distances <= radius_km

        subset = dataframe.loc[mask].copy()

        subset["Distance_km"] = distances[mask].round(2)

        return subset
