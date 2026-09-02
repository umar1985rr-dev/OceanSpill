from fastapi import APIRouter

from backend.services.monitoring import monitoring_service

router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"],
)


@router.get("/history")
def history():

    alerts = monitoring_service.state.to_dict()["alerts"]

    return {
        "count": len(alerts),
        "alerts": alerts,
    }


@router.get("/current")
def current():

    alerts = monitoring_service.state.to_dict()["alerts"]

    if alerts:

        return alerts[-1]

    return None
