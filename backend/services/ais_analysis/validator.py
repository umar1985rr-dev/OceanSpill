import pandas as pd


class AISValidator:

    REQUIRED_COLUMNS = [
        "MMSI",
        "LAT",
        "LON",
        "BaseDateTime",
        "SOG",
        "COG",
        "IMO",
        "VesselType",
    ]

    @classmethod
    def validate(cls, dataframe):

        missing = []

        for column in cls.REQUIRED_COLUMNS:

            if column not in dataframe.columns:
                missing.append(column)

        if missing:

            raise ValueError(
                f"Missing AIS columns: {missing}"
            )

        return True