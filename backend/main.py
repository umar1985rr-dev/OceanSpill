from contextlib import asynccontextmanager

from pathlib import Path

from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from fastapi.responses import FileResponse

from brotli_asgi import BrotliMiddleware

from backend.config import settings

from backend.core.exceptions import generic_exception_handler
from backend.core.middleware import RateLimitMiddleware

from backend.api import get_v1_routers
from backend.api import (
    auth_router,
    users_router,
    incidents_router,
    monitoring_router,
    weather_router,
    alerts_router,
    system_router,
    drift_router,
    report_router,
    config_router,
    cleanup_router,
    detection_router,
    impact_router,
    ais_router,
    error_router,
)

from backend.services.monitoring import monitoring_service
from backend.database import init_db


DIST = Path("frontend/dist")


def check_startup_requirements():
    """Check all requirements before starting the server."""
    import sys
    import subprocess

    print("=" * 60)
    print("  OceanSpill Startup Check")
    print("=" * 60)
    print()

    errors = []
    warnings = []

    # Check Python version
    py_version = sys.version_info
    if py_version < (3, 10):
        errors.append(f"Python 3.10+ required, found {py_version.major}.{py_version.minor}")
    else:
        print(f"[OK] Python {py_version.major}.{py_version.minor}.{py_version.micro}")

    # Check critical packages
    critical_packages = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("sqlalchemy", "SQLAlchemy"),
        ("numpy", "NumPy"),
        ("pandas", "Pandas"),
        ("jose", "python-jose"),
        ("passlib", "passlib"),
        ("email_validator", "email-validator"),
    ]

    for import_name, display_name in critical_packages:
        try:
            __import__(import_name)
            print(f"[OK] {display_name}")
        except ImportError:
            errors.append(f"{display_name} not installed. Run: pip install {import_name}")

    # Check optional packages with warnings
    optional_packages = [
        ("cv2", "OpenCV"),
        ("torch", "PyTorch"),
        ("transformers", "Transformers"),
    ]

    for import_name, display_name in optional_packages:
        try:
            __import__(import_name)
            print(f"[OK] {display_name}")
        except ImportError:
            warnings.append(f"{display_name} not installed (optional)")

    # Check frontend build
    if DIST.exists() and (DIST / "index.html").exists():
        print(f"[OK] Frontend built")
    else:
        warnings.append("Frontend not built. Run: cd frontend && npm install && npm run build")

    print()

    if errors:
        print("ERRORS:")
        for err in errors:
            print(f"  [ERROR] {err}")
        print()
        print("Please fix the errors above before starting the server.")
        print("Run 'python check_requirements.py --auto' to auto-fix some issues.")
        print()
        return False

    if warnings:
        print("WARNINGS (server will start but some features may not work):")
        for warn in warnings:
            print(f"  [WARN] {warn}")
        print()

    print("All requirements satisfied! Starting server...")
    print()
    return True


@asynccontextmanager
async def lifespan(app):
    # Initialize database tables
    init_db()

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

# Run startup check
_startup_ok = check_startup_requirements()
if not _startup_ok:
    import sys
    # Don't exit immediately - let FastAPI handle it gracefully
    # Server will start but some features may not work

app.add_exception_handler(Exception, generic_exception_handler)

app.add_middleware(BrotliMiddleware)

# Rate limiting middleware (must be added before CORS for proper IP extraction)
app.add_middleware(RateLimitMiddleware, requests_per_minute=60, requests_per_hour=1000)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        # The backend also serves the built SPA on these origins. Safety
        # net for any request that still targets the API by host (e.g. a
        # stale bundle or an absolute API_URL) — the current frontend uses
        # same-origin relative URLs, so no CORS is triggered normally.
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API routes ──────────────────────────────────────────────

# Versioned API (v1)
for router, prefix, tags in get_v1_routers():
    app.include_router(router, prefix="/api/v1" + prefix, tags=tags)

# Legacy routes (without version) for backward compatibility
app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(incidents_router, prefix="/api")
app.include_router(monitoring_router, prefix="/api")
app.include_router(weather_router, prefix="/api")
app.include_router(alerts_router, prefix="/api")
app.include_router(system_router, prefix="/api")
app.include_router(drift_router, prefix="/api")
app.include_router(report_router, prefix="/api")
app.include_router(config_router, prefix="/api")
app.include_router(cleanup_router, prefix="/api")
app.include_router(detection_router, prefix="/api")
app.include_router(impact_router, prefix="/api")
app.include_router(ais_router, prefix="/api")
app.include_router(error_router, prefix="/api")


# ── Generated artifacts (model overlays / masks / reports) ──
# The detection pipeline writes analysis images into ./outputs;
# serve them so the frontend can preview original/mask/overlay
# results instead of dead links. Mounted for static serving before
# the SPA catch-all so /outputs/* never falls through to index.html.
from fastapi.staticfiles import StaticFiles

OUTPUTS_DIR = Path("outputs")
if OUTPUTS_DIR.exists():
    app.mount("/outputs", StaticFiles(directory=OUTPUTS_DIR), name="outputs")


# ── Frontend (built React SPA) ─────────────────────────────
# Served from frontend/dist/ so the official only runs one
# server on one port. API routes registered above take
# precedence; the catch-all below handles SPA navigation.


@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):

    if DIST.exists():

        file_path = DIST / full_path

        if file_path.is_file():

            # Hashed assets are content-addressed (filename changes when
            # content changes) so they are safe to cache forever.
            return FileResponse(
                file_path,
                headers={"Cache-Control": "public, max-age=31536000, immutable"},
            )

        # index.html is the SPA entry point. Never let the browser keep a
        # stale copy: an old index.html requests asset hashes that no longer
        # exist after a rebuild, which makes the page render blank.
        return FileResponse(
            DIST / "index.html",
            headers={"Cache-Control": "no-cache"},
        )

    return {
        "message": "OceanSpill Backend Running",
        "version": "1.0",
    }
