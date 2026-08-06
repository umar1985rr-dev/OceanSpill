class CleanupRecommendationEngine:

    def recommend(self, data):

        recommendations = []

        equipment = []

        priority = "LOW"

        # ------------------------
        # Spill Size
        # ------------------------

        if data.spill_area >= 5:

            recommendations.append(
                "Deploy containment booms immediately."
            )

            equipment.extend(

                [

                    "Containment Booms",

                    "Skimmer Vessel",

                    "Oil Recovery Vessel",

                ]

            )

            priority = "CRITICAL"

        elif data.spill_area >= 2:

            recommendations.append(
                "Deploy skimmer vessels."
            )

            equipment.extend(

                [

                    "Skimmer Vessel",

                    "Absorbent Pads",

                ]

            )

            priority = "HIGH"

        else:

            recommendations.append(
                "Monitor spill expansion."
            )

            equipment.append(
                "Monitoring Drone"
            )

            priority = "MEDIUM"

        # ------------------------
        # Coastline
        # ------------------------

        if data.distance_to_coast < 10:

            recommendations.append(
                "Protect coastline using floating barriers."
            )

        # ------------------------
        # Wind
        # ------------------------

        if data.wind_speed > 20:

            recommendations.append(
                "Increase monitoring frequency due to strong winds."
            )

        # ------------------------
        # Ocean Current
        # ------------------------

        if data.current_speed > 2:

            recommendations.append(
                "Predict rapid spill drift."
            )

        # ------------------------
        # Risk Level
        # ------------------------

        if "HIGH" in data.risk_level or "CRITICAL" in data.risk_level:

            recommendations.append(
                "Mobilize emergency response teams."
            )

        return {

            "Priority": priority,

            "Equipment": equipment,

            "Recommendations": recommendations,

        }