from backend.services.impact_analysis.environmental import (
    EnvironmentalImpactAnalyzer,
)

from backend.services.impact_analysis.economic import (
    EconomicImpactAnalyzer,
)


class RiskScoringEngine:

    def __init__(self):

        self.environment = (
            EnvironmentalImpactAnalyzer()
        )

        self.economic = (
            EconomicImpactAnalyzer()
        )

    def calculate(
        self,
        impact_input,
    ):

        env = self.environment.analyze(
            impact_input
        )

        eco = self.economic.analyze(
            impact_input
        )

        score = 0

        # -----------------------------
        # Spill Size
        # -----------------------------

        if impact_input.spill_area >= 5:

            score += 30

        elif impact_input.spill_area >= 2:

            score += 20

        else:

            score += 10

        # -----------------------------
        # Environmental Risk
        # -----------------------------

        for value in env.values():

            if value["risk"] == "🔴 Critical":

                score += 12

            elif value["risk"] == "🟠 High":

                score += 8

            elif value["risk"] == "🟡 Medium":

                score += 5

            else:

                score += 2

        # -----------------------------
        # Economic Loss
        # -----------------------------

        total_loss = eco[
            "Total Economic Loss ($)"
        ]

        if total_loss >= 3000000:

            score += 30

        elif total_loss >= 1500000:

            score += 20

        elif total_loss >= 700000:

            score += 10

        else:

            score += 5

        score = min(score, 100)

        if score >= 85:

            level = "🔴 CRITICAL"

        elif score >= 65:

            level = "🟠 HIGH"

        elif score >= 40:

            level = "🟡 MEDIUM"

        else:

            level = "🟢 LOW"

        return {

            "Risk Score": score,

            "Risk Level": level,

            "Environmental Report": env,

            "Economic Report": eco,

        }