from pathlib import Path

import pandas as pd


class ImpactDataLoader:

    def __init__(self):

        self.base_path = (
            Path("dataset")
            / "raw"
            / "geographic"
        )

    def _load_csv(
        self,
        filename,
    ):

        path = self.base_path / filename

        if not path.exists():
            raise FileNotFoundError(
                f"{filename} not found."
            )

        data = pd.read_csv(path)

        required_columns = [
            "Name",
            "Latitude",
            "Longitude",
        ]

        for column in required_columns:

            if column not in data.columns:

                raise ValueError(
                    f"{filename} missing column: {column}"
                )

        data = data.dropna()

        return data

    def load_coastlines(self):

        return self._load_csv(
            "coastlines.csv"
        )

    def load_ports(self):

        return self._load_csv(
            "ports.csv"
        )

    def load_protected_areas(self):

        return self._load_csv(
            "marine_protected_areas.csv"
        )

    def load_fishing_zones(self):

        return self._load_csv(
            "fishing_zones.csv"
        )

    def load_mangroves(self):

        return self._load_csv(
            "mangroves.csv"
        )

    def load_coral_reefs(self):

        return self._load_csv(
            "coral_reefs.csv"
        )