"""
Configuration & Data Upload API.

Officials use this to:
  • View / update model inputs (coordinates, thresholds, etc.)
  • Upload their own datasets (AIS CSV, satellite images, env data)
    without touching the server filesystem by hand.
"""

import shutil

from pathlib import Path

from fastapi import APIRouter, File, HTTPException, Query, UploadFile

from backend.api.config_store import get_config, update_config

router = APIRouter(
    prefix="/config",
    tags=["Configuration"],
)

# ── Dataset upload destinations ──────────────────────────────
# Each key is a logical dataset name the frontend sends; the value
# is the directory the file lands in (relative to repo root).

UPLOAD_DIR = {
    "ais": Path("dataset/raw/ais_data"),
    "satellite": Path("dataset/samples/satellite_images"),
    "coastlines": Path("dataset/raw/geographic"),
    "protected_areas": Path("dataset/raw/geographic"),
    "mangroves": Path("dataset/raw/geographic"),
    "coral_reefs": Path("dataset/raw/geographic"),
    "fishing_zones": Path("dataset/raw/geographic"),
    "ports": Path("dataset/raw/geographic"),
    "ocean_currents": Path("dataset/raw/geographic"),
}

# ── Read / Write settings ────────────────────────────────────


@router.get("")
def read_config():
    """Return the current runtime configuration."""
    return get_config()


@router.put("")
def write_config(body: dict):
    """
    Merge provided keys into the runtime config.

    Accepted keys:
      incident_latitude, incident_longitude,
      detection_threshold, monitor_interval_seconds,
      feed_source, simulator_images_dir, ais_csv_path

    Unknown keys are silently ignored.
    """
    cfg = update_config(body)
    return {"status": "updated", "config": cfg}


# ── File uploads ─────────────────────────────────────────────


@router.post("/upload/{dataset}")
async def upload_dataset(
    dataset: str,
    file: UploadFile = File(...),
):
    """
    Upload a file for *dataset* (one of: ais, satellite, coastlines, ...).

    Files land in the expected directory so existing loaders pick
    them up without code changes.
    """
    dest_dir = UPLOAD_DIR.get(dataset)

    if dest_dir is None:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unknown dataset '{dataset}'. "
                f"Supported: {', '.join(sorted(UPLOAD_DIR))}"
            ),
        )

    dest_dir.mkdir(parents=True, exist_ok=True)

    filename = file.filename or f"{dataset}_upload"
    dest_path = dest_dir / filename

    if dataset == "ais":

        contents = await file.read()

        import pandas as _pd
        from io import StringIO

        from backend.services.ais_analysis.validator import AISValidator

        try:

            df = _pd.read_csv(StringIO(contents.decode("utf-8")))

            AISValidator.validate(df)

        except ValueError as exc:

            raise HTTPException(
                status_code=400,
                detail=f"AIS CSV validation failed: {exc}",
            )

        except Exception as exc:

            raise HTTPException(
                status_code=400,
                detail=f"Could not parse AIS file: {exc}",
            )

        # Validation passed — write the file and clear any cached AIS
        # data so the next fetch uses the new upload.
        with open(dest_path, "wb") as buf:

            buf.write(contents)

        from backend.services.ais_analysis import provider

        provider._cache["fetched_at"] = None

    else:

        with open(dest_path, "wb") as buf:

            shutil.copyfileobj(file.file, buf)

    size_mb = dest_path.stat().st_size / (1024 * 1024)

    return {
        "status": "uploaded",
        "dataset": dataset,
        "filename": filename,
        "path": str(dest_path),
        "size_mb": round(size_mb, 1),
    }


@router.get("/datasets")
def list_datasets():
    """
    Return the known datasets with their upload status so the
    frontend can show green/red indicators.
    """
    result = {}
    for name, dir_path in UPLOAD_DIR.items():
        files = sorted(dir_path.glob("*")) if dir_path.exists() else []
        data_files = [f for f in files if f.is_file()]
        total_size = sum(f.stat().st_size for f in data_files)
        result[name] = {
            "path": str(dir_path),
            "files": len(data_files),
            "size_mb": round(total_size / (1024 * 1024), 1),
            "available": len(data_files) > 0,
            "filenames": [f.name for f in data_files[:5]],
        }
    return result


@router.post("/test")
def test_config(test_params: dict):
    """
    Test the current configuration for satellite and AIS feeds.
    Attempts to fetch credentials and connect to the respective services.
    Returns a dictionary indicating the status of each service test.
    """
    from backend.api.config_store import get_config

    results = {}

    # Test Satellite Feed
    try:
        cfg = get_config()
        feed_source = test_params.get("feed_source", cfg.get("feed_source"))
        if feed_source == "sentinel_hub":
            from backend.services.satellite_feed.sentinel_hub import SentinelHubFeed
            feed = SentinelHubFeed()
            feed.connect()
            results["satellite"] = {"status": "success", "message": "Sentinel Hub feed connected successfully."}
        else:
            results["satellite"] = {"status": "skipped", "message": f"Using feed source: {feed_source}"}
    except RuntimeError as e:
        results["satellite"] = {"status": "error", "message": str(e)}
    except Exception as e:
        results["satellite"] = {"status": "error", "message": f"An unexpected error occurred: {e}"}

    # Test AIS Feed
    try:
        ais_source_type = test_params.get("ais_source", cfg.get("ais_source", "csv"))
        if ais_source_type in ("csv", "simulated_live"):
            results["ais"] = {"status": "skipped", "message": "Local source - no connection test needed."}
        else:
            from backend.services.ais_analysis.provider import get_ais_data
            get_ais_data(force=True, source_type=ais_source_type)
            results["ais"] = {"status": "success", "message": f"AIS source '{ais_source_type}' connected successfully."}
    except RuntimeError as e:
        results["ais"] = {"status": "error", "message": str(e)}
    except ValueError as e:
         results["ais"] = {"status": "error", "message": f"AIS data validation error: {e}"}
    except Exception as e:
        results["ais"] = {"status": "error", "message": f"An unexpected error occurred: {e}"}

    return results
