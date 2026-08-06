from pathlib import Path

import folium
from folium import plugins


class DriftMap:

    def create(
        self,
        spill,
        predictions,
        risk_zones,
    ):

        # --------------------------------------------------
        # Create Map
        # --------------------------------------------------

        m = folium.Map(
            location=[
                spill.latitude,
                spill.longitude,
            ],
            zoom_start=10,
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
            overlay=False,
            control=True,
        ).add_to(m)

        # --------------------------------------------------
        # Spill Marker
        # --------------------------------------------------

        folium.Marker(
            [spill.latitude, spill.longitude],
            popup="<b>Detected Oil Spill</b>",
            tooltip="Current Spill",
            icon=folium.Icon(
                color="red",
                icon="tint",
                prefix="fa",
            ),
        ).add_to(m)

        path = []

        # --------------------------------------------------
        # Prediction Markers
        # --------------------------------------------------

        for point in predictions:

            location = [
                point["latitude"],
                point["longitude"],
            ]

            path.append(location)

            hour = point["hour"]

            if hour == 1:
                color = "green"
            elif hour == 6:
                color = "orange"
            elif hour == 12:
                color = "red"
            elif hour == 24:
                color = "purple"
            else:
                color = "blue"

            popup = f"""
            <b>Predicted Spill Position</b>
            <hr>

            <b>Hour:</b> {hour}<br>

            <b>Latitude:</b> {point["latitude"]:.5f}<br>

            <b>Longitude:</b> {point["longitude"]:.5f}<br><br>

            <b>Wind Speed:</b> {point["wind_speed"]} km/h<br>

            <b>Wind Direction:</b> {point["wind_direction"]}°<br>

            <b>Current Speed:</b> {point["current_speed"]} km/h<br>

            <b>Current Direction:</b> {point["current_direction"]}°<br>

            <b>Estimated Drift:</b> {point["estimated_speed"]} km/h
            """

            folium.CircleMarker(
                location=location,
                radius=6,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=1,
                popup=popup,
            ).add_to(m)

        # --------------------------------------------------
        # Drift Path
        # --------------------------------------------------

        folium.PolyLine(
            path,
            color="blue",
            weight=4,
            opacity=0.8,
        ).add_to(m)

        # --------------------------------------------------
        # Risk Zones
        # --------------------------------------------------

        for zone in risk_zones:

            folium.Circle(
                location=[
                    zone["latitude"],
                    zone["longitude"],
                ],
                radius=zone["radius"],
                color="orange",
                fill=True,
                fill_color="orange",
                fill_opacity=0.18,
                popup=f"""
                <b>Risk Zone</b><br>
                Hour: {zone['hour']}<br>
                Radius: {zone['radius']:.0f} m
                """,
            ).add_to(m)

        # --------------------------------------------------
        # Plugins
        # --------------------------------------------------

        plugins.Fullscreen().add_to(m)
        plugins.MiniMap().add_to(m)
        plugins.MousePosition().add_to(m)
        plugins.MeasureControl().add_to(m)

        folium.LayerControl().add_to(m)

        # --------------------------------------------------
        # Legend
        # --------------------------------------------------

        legend = """
        <div style="
        position: fixed;
        bottom: 40px;
        left: 40px;
        width: 240px;
        background:white;
        border:2px solid grey;
        border-radius:8px;
        z-index:9999;
        font-size:14px;
        padding:12px;
        ">

        <h4 style="margin-top:0;">
        Drift Prediction
        </h4>

        🔴 Current Spill<br>
        🟢 Hour 1<br>
        🟠 Hour 6<br>
        🔴 Hour 12<br>
        🟣 Hour 24<br>
        🔵 Intermediate Hours<br>
        🟠 Risk Zone

        </div>
        """

        m.get_root().html.add_child(
            folium.Element(legend)
        )

        # --------------------------------------------------
        # Save Map
        # --------------------------------------------------

        output = (
            Path("reports")
            / "drift_prediction_map.html"
        )

        output.parent.mkdir(
            exist_ok=True
        )

        m.save(output)

        return output