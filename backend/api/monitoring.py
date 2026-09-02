from fastapi import APIRouter

from backend.config import settings

from backend.services.monitoring import monitoring_service

router = APIRouter(
    prefix="/monitoring",
    tags=["Live Monitoring"],
)


@router.get("/status")
def status():

    state = monitoring_service.state.to_dict()

    feed_status = state["feed_status"]

    try:

        live = monitoring_service.feed.status()

        feed_status = {**feed_status, **live}

    except Exception:

        pass

    return {
        "instance_id": monitoring_service.instance_id,
        "version": state["version"],
        "is_running": state["is_running"],
        "is_processing": state["is_processing"],
        "feed": feed_status,
        "interval_seconds": settings.monitor_interval_seconds,
        "detection_threshold": settings.detection_threshold,
        "last_checked_at": state["last_checked_at"],
        "current_frame": state["current_frame"],
        "last_detection": state["last_detection"],
        "report_path": state["report_path"],
    }


@router.get("/start")
async def start():

    monitoring_service.start()

    return {
        "status": "Monitoring started",
    }


@router.get("/stop")
async def stop():

    monitoring_service.stop()

    return {
        "status": "Monitoring stopped",
    }


@router.get("/history")
def history():

    incidents = monitoring_service.state.to_dict()["incidents"]

    return {
        "count": len(incidents),
        "incidents": incidents,
    }


@router.get("/incidents")
def incidents():

    return monitoring_service.state.to_dict()["incidents"]
