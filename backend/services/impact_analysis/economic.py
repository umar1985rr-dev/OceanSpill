from backend.services.impact_analysis import (
    ImpactDataLoader,
)
from backend.services.impact_analysis.environmental import (
    EnvironmentalImpactAnalyzer,
)


class EconomicImpactAnalyzer:

    def __init__(self):

        self.loader = ImpactDataLoader()

        self.environment = (
            EnvironmentalImpactAnalyzer()
        )

    def analyze(
        self,
        impact_input,
    ):

        ports = self.loader.load_ports()

        fishing = (
            self.loader.load_fishing_zones()
        )

        port_distance = (
            self.environment.nearest_distance(
                ports,
                impact_input.latitude,
                impact_input.longitude,
            )
        )

        fishing_distance = (
            self.environment.nearest_distance(
                fishing,
                impact_input.latitude,
                impact_input.longitude,
            )
        )

        spill_area = impact_input.spill_area

        cleanup_cost = spill_area * 450000

        fisheries_loss = max(
            0,
            (30 - fishing_distance)
        ) * 18000

        shipping_loss = max(
            0,
            (30 - port_distance)
        ) * 25000

        tourism_loss = spill_area * 120000

        total_loss = (

            cleanup_cost +

            fisheries_loss +

            shipping_loss +

            tourism_loss

        )

        return {

            "Nearest Port (km)": round(
                port_distance,
                2,
            ),

            "Nearest Fishing Zone (km)": round(
                fishing_distance,
                2,
            ),

            "Cleanup Cost ($)": round(
                cleanup_cost,
                2,
            ),

            "Estimated Fisheries Loss ($)": round(
                fisheries_loss,
                2,
            ),

            "Estimated Shipping Loss ($)": round(
                shipping_loss,
                2,
            ),

            "Estimated Tourism Loss ($)": round(
                tourism_loss,
                2,
            ),

            "Total Economic Loss ($)": round(
                total_loss,
                2,
            ),

        }