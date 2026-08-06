from contextlib import asynccontextmanager

from pathlib import Path

from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from fastapi.responses import FileResponse

from brotli_asgi import BrotliMiddleware

from backend.config import settings

from backend.core.exceptions import generic_exception_handler

from backend.api.errors import router as error_router

from backend.api.monitoring import router as monitoring_router

from backend.api.weather import router as weather_router

from backend.api.alerts import router as alerts_router

from backend.api.ais import router as ais_router

from backend.api.detection import router as detection_router

from backend.api.drift import router as drift_router

from backend.api.impact import router as impact_router

from backend.api.cleanup import router as cleanup_router

from backend.api.report import router as report_router

from backend.api.system import router as system_router

from backend.api.config import router as config_router

from backend.services.monitoring import monitoring_service


DIST = Path("frontend/dist")


@asynccontextmanager
async def lifespan(app):

    if settings.monitor_enabled:

        try:

            monitoring_service.start()

        except Exception as exc:

            print(f"[startup] monitoring start failed: {exc}")

    yield

    monitoring_service.stop()


app = FastAPI(
    title="OceanSpill API",
    version="1.0",
    lifespan=lifespan,
)

app.add_exception_handler(Exception, generic_exception_handler)

app.add_middleware(BrotliMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API routes ──────────────────────────────────────────────

app.include_router(monitoring_router, prefix="/api")

app.include_router(weather_router, prefix="/api")

app.include_router(alerts_router, prefix="/api")

app.include_router(system_router, prefix="/api")

app.include_router(drift_router, prefix="/api")

app.include_router(report_router, prefix="/api")

app.include_router(config_router, prefix="/api")

app.include_router(error_router, prefix="/api")

app.include_router(cleanup_router, prefix="/api")

app.include_router(detection_router, prefix="/api")

app.include_router(impact_router, prefix="/api")

app.include_router(ais_router, prefix="/api")


# ── Frontend (built React SPA) ─────────────────────────────
# Served from frontend/dist/ so the official only runs one
# server on one port. API routes registered above take
# precedence; the catch-all below handles SPA navigation.


@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):

    if DIST.exists():

        file_path = DIST / full_path

        if file_path.is_file():

            return FileResponse(file_path)

        return FileResponse(DIST / "index.html")

    return {
        "message": "OceanSpill Backend Running",
        "version": "1.0",
    }
