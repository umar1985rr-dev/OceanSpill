from pathlib import Path

import folium


class AISMapVisualizer:

    def __init__(
        self,
        save_dir="reports/maps"
    ):

        self.save_dir = Path(save_dir)

        self.save_dir.mkdir(
            parents=True,
            exist_ok=True
        )

    def create_map(
        self,
        spill,
        ranked_vessels,
    ):

        m = folium.Map(
            location=[
                spill.latitude,
                spill.longitude,
            ],
            zoom_start=11
        )

        # Spill marker

        folium.Marker(
            [spill.latitude, spill.longitude],
            popup="Oil Spill",
            icon=folium.Icon(
                color="red",
                icon="warning-sign"
            ),
        ).add_to(m)

        # Top 20 vessels

        for _, vessel in ranked_vessels.head(20).iterrows():

            folium.CircleMarker(
                [
                    vessel["LAT"],
                    vessel["LON"],
                ],
                radius=5,
                popup=f"MMSI: {vessel['MMSI']}\nScore: {vessel['SuspectScore']}",
                color="blue",
                fill=True,
            ).add_to(m)

        # Highlight best suspect

        suspect = ranked_vessels.iloc[0]

        folium.Marker(
            [
                suspect["LAT"],
                suspect["LON"],
            ],
            popup="Top Suspect",
            icon=folium.Icon(
                color="green"
            ),
        ).add_to(m)

        output = self.save_dir / "suspect_map.html"

        m.save(output)

        return output