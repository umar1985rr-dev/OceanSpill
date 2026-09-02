from backend.services.impact_analysis.recommendations import (
    RecommendationEngine,
)
from backend.services.impact_analysis import (
    RiskScoringEngine,
)


class ImpactDashboard:

    def __init__(self):

        self.engine = RiskScoringEngine()
        self.recommendation = RecommendationEngine()

    def generate(
        self,
        impact_input,
    ):

        result = self.engine.calculate(
            impact_input
        )

        env = result["Environmental Report"]

        eco = result["Economic Report"]

        score = result["Risk Score"]

        level = result["Risk Level"]

        if score >= 85:

            priority = "Immediate Response"

        elif score >= 65:

            priority = "Urgent Monitoring"

        elif score >= 40:

            priority = "Routine Monitoring"

        else:

            priority = "Low Priority"
        recommendations = self.recommendation.generate(
            score
        )

        dashboard = {

            "Risk Score": score,

            "Risk Level": level,
            "Recommendations": recommendations,

            "Response Priority": priority,

            "Nearest Coastline": env[
                "Nearest Coastline"
            ]["distance"],

            "Nearest Protected Area": env[
                "Nearest Protected Area"
            ]["distance"],

            "Nearest Port": eco[
                "Nearest Port (km)"
            ],

            "Cleanup Cost": eco[
                "Cleanup Cost ($)"
            ],

            "Economic Loss": eco[
                "Total Economic Loss ($)"
            ],

        }

        return dashboard