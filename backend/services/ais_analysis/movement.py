import numpy as np


class MovementAnalyzer:

    def analyze(
        self,
        vessels_df,
    ):
        """
        Analyze vessel movement based on speed and heading.

        Operates vectorized on a DataFrame and returns the same
        DataFrame with a MovementScore column added.
        """

        analyzed = vessels_df.copy()

        # -----------------------------
        # Speed Analysis
        # -----------------------------

        speed = analyzed["SOG"].to_numpy(dtype=float)

        analyzed["MovementScore"] = np.select(
            [
                (speed >= 2) & (speed <= 15),
                speed < 2,
            ],
            [
                30,
                15,
            ],
            default=10,
        )

        # -----------------------------
        # Heading Analysis
        # -----------------------------

        heading = analyzed["COG"].to_numpy(dtype=float)

        valid_heading = (heading >= 0) & (heading <= 360)

        analyzed["MovementScore"] += np.where(
            valid_heading,
            20,
            0,
        )

        return analyzed
