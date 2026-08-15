class RecommendationEngine:

    def generate(
        self,
        risk_score,
    ):

        if risk_score >= 85:

            return [

                "Deploy emergency oil containment booms immediately.",

                "Notify Coast Guard and Marine Pollution Control authorities.",

                "Suspend nearby fishing operations.",

                "Issue navigation warnings to all vessels.",

                "Protect nearby marine reserves and mangroves.",

                "Begin continuous satellite monitoring every hour.",

            ]

        elif risk_score >= 65:

            return [

                "Deploy containment booms near spill boundary.",

                "Increase satellite monitoring frequency.",

                "Inspect nearby vessels for possible leakage.",

                "Warn nearby ports and fishing communities.",

                "Prepare cleanup teams for rapid deployment.",

            ]

        elif risk_score >= 40:

            return [

                "Continue monitoring spill movement.",

                "Track weather and ocean currents.",

                "Notify local environmental agencies.",

                "Prepare response equipment if spill expands.",

            ]

        else:

            return [

                "Routine monitoring required.",

                "Continue satellite observations.",

                "No immediate response required.",

            ]