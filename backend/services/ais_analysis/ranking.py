import numpy as np


class SuspectRanker:

    def rank(
        self,
        analyzed_df,
    ):
        """
        Rank suspect vessels and keep only the highest scoring
        record for each MMSI.

        Fully vectorized on a DataFrame; returns the ranked
        DataFrame sorted by SuspectScore (descending).
        """

        ranked = analyzed_df.copy()

        # ----------------------------------
        # Distance Score
        # ----------------------------------

        distance = ranked["Distance_km"].to_numpy(dtype=float)

        ranked["DistanceScore"] = np.select(
            [
                distance <= 2,
                distance <= 5,
                distance <= 10,
            ],
            [
                40,
                30,
                20,
            ],
            default=10,
        )

        # ----------------------------------
        # Vessel Type Score
        # ----------------------------------

        vessel_type = ranked["VesselType"].to_numpy(dtype=float)

        ranked["TypeScore"] = np.select(
            [
                np.isin(vessel_type, [80, 81, 82]),
                vessel_type == 70,
            ],
            [
                30,
                20,
            ],
            default=10,
        )

        # ----------------------------------
        # Suspect Score = distance + movement + type
        # ----------------------------------

        ranked["SuspectScore"] = (
            ranked["DistanceScore"]
            + ranked["MovementScore"]
            + ranked["TypeScore"]
        )

        ranked = ranked.drop(
            columns=["DistanceScore", "TypeScore"]
        )

        # ----------------------------------
        # Keep the highest scoring record per MMSI
        # ----------------------------------

        ranked = ranked.sort_values(
            by="SuspectScore",
            ascending=False,
        )

        ranked = ranked.drop_duplicates(
            subset="MMSI",
            keep="first",
        )

        ranked = ranked.sort_values(
            by="SuspectScore",
            ascending=False,
        ).reset_index(drop=True)

        return ranked
