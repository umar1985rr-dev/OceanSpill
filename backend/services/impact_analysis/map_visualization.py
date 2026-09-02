from pathlib import Path

import folium
from folium.plugins import MarkerCluster

from backend.services.impact_analysis import (
    ImpactDataLoader,
)


class ImpactMap:

    def __init__(self):

        self.loader = ImpactDataLoader()

    def create(
        self,
        impact_input,
        drift_predictions=None,
        risk_zones=None,
        suspect_vessels=None,
    ):

        m = folium.Map(

            location=[
                impact_input.latitude,
                impact_input.longitude,
            ],

            zoom_start=9,

            control_scale=True,

        )

        # --------------------------------------------------
        # Base Maps
        # --------------------------------------------------

        folium.TileLayer(
            "OpenStreetMap",
            name="Street Map",
        ).add_to(m)

        folium.TileLayer(
            "CartoDB positron",
            name="Light Map",
        ).add_to(m)

        folium.TileLayer(
            "CartoDB dark_matter",
            name="Dark Map",
        ).add_to(m)

        folium.TileLayer(
            tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            attr="Esri",
            name="Satellite",
        ).add_to(m)

        # --------------------------------------------------
        # Oil Spill Marker
        # --------------------------------------------------

        folium.Marker(

            [
                impact_input.latitude,
                impact_input.longitude,
            ],

            tooltip="Detected Oil Spill",

            popup="<b>Detected Oil Spill</b>",

            icon=folium.Icon(
                color="red",
                icon="tint",
                prefix="fa",
            ),

        ).add_to(m)

        # --------------------------------------------------
        # Drift Prediction Path
        # --------------------------------------------------

        if drift_predictions:

            path = []

            for point in drift_predictions:

                location = [

                    point["latitude"],

                    point["longitude"],

                ]

                path.append(location)

                folium.CircleMarker(

                    location,

                    radius=5,

                    color="blue",

                    fill=True,

                    fill_color="blue",

                    popup=f"Hour {point['hour']}",

                ).add_to(m)

            folium.PolyLine(

                path,

                color="blue",

                weight=3,

                opacity=0.8,

            ).add_to(m)

        # --------------------------------------------------
        # Risk Zones
        # --------------------------------------------------

        if risk_zones:

            for zone in risk_zones:

                folium.Circle(

                    [

                        zone["latitude"],

                        zone["longitude"],

                    ],

                    radius=zone["radius"],

                    color="orange",

                    fill=True,

                    fill_color="orange",

                    fill_opacity=0.20,

                    popup=f"Risk Zone - Hour {zone['hour']}",

                ).add_to(m)

        # --------------------------------------------------
        # AIS Suspect Vessels
        # --------------------------------------------------

        if suspect_vessels:

            for vessel in suspect_vessels:

                folium.Marker(

                    [

                        vessel["LAT"],

                        vessel["LON"],

                    ],

                    popup=f"""
                    <b>Suspect Vessel</b><br>
                    MMSI: {vessel['MMSI']}<br>
                    Score: {vessel['Suspect Score']}
                    """,

                    icon=folium.Icon(

                        color="black",

                        icon="ship",

                        prefix="fa",

                    ),

                ).add_to(m)

        # --------------------------------------------------
        # Environmental Layers
        # --------------------------------------------------

        datasets = [

            (

                self.loader.load_coastlines(),

                "blue",

                "Coastlines",

            ),

            (

                self.loader.load_ports(),

                "gray",

                "Ports",

            ),

            (

                self.loader.load_protected_areas(),

                "green",

                "Protected Areas",

            ),

            (

                self.loader.load_fishing_zones(),

                "orange",

                "Fishing Zones",

            ),

            (

                self.loader.load_mangroves(),

                "darkgreen",

                "Mangroves",

            ),

            (

                self.loader.load_coral_reefs(),

                "purple",

                "Coral Reefs",

            ),

        ]

        for dataframe, color, label in datasets:

            cluster = MarkerCluster(
                name=label
            )

            for _, row in dataframe.iterrows():

                folium.CircleMarker(

                    [

                        row["Latitude"],

                        row["Longitude"],

                    ],

                    radius=5,

                    color=color,

                    fill=True,

                    fill_color=color,

                    fill_opacity=1,

                    popup=row["Name"],

                ).add_to(cluster)

            cluster.add_to(m)

        # --------------------------------------------------
        # Layer Control
        # --------------------------------------------------

        folium.LayerControl().add_to(m)

        # --------------------------------------------------
        # Save Map
        # --------------------------------------------------

        output = (
            Path("reports")
            / "impact_map.html"
        )

        output.parent.mkdir(
            exist_ok=True
        )

        m.save(output)

        return output