import math


def generate_risk_zones(
    predictions,
    spill_area,
):

    risk_zones = []

    # Initial radius (meters)
    base_radius = spill_area * 500

    for point in predictions:

        hour = point["hour"]

        # Increase radius by 5% every hour
        growth_factor = 1 + (hour * 0.05)

        radius = base_radius * growth_factor

        risk_zones.append({

            "hour": hour,

            "latitude": point["latitude"],

            "longitude": point["longitude"],

            "radius": radius,

        })

    return risk_zones