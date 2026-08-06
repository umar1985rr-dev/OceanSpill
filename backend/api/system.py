from fastapi import APIRouter

from backend.services.system.workflow import (
    MarineDecisionSupportSystem,
)

from backend.services.monitoring import monitoring_service

router = APIRouter(
    prefix="/system",
    tags=["System"],
)


@router.get("/health")
def health():

    state = monitoring_service.state.to_dict()

    system = MarineDecisionSupportSystem()

    result = system.health()

    result["monitoring"] = {

        "is_running": state["is_running"],

        "is_processing": state["is_processing"],

        "feed": state.get("feed_status", {}).get("source"),

        "frames_served": (
            state.get("feed_status", {}).get("frames_served")
        ),

        "last_checked_at": state.get("last_checked_at"),

        "incidents": len(state.get("incidents", [])),

        "report_path": state.get("report_path"),

    }

    return result
