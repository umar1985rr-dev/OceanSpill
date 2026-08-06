# OceanSpill — AI-Powered Oil Spill Detection & Response

A platform that watches satellite imagery for oil spills, identifies which ships might be responsible, predicts where the slick is heading, and puts together an incident report — all from your browser.

Built for coast guards, port authorities, and marine departments. You don't need to code anything. Set it up once through the in-app Configuration page and let it run.

---

## Table of Contents

- [What it does](#what-it-does)
- [System requirements](#system-requirements)
- [Installation](#installation)
- [Quick start (one-click)](#quick-start-one-click)
- [Manual run](#manual-run)
- [What data do I need?](#what-data-do-i-need)
- [Connecting live satellite imagery (Copernicus)](#connecting-live-satellite-imagery-copernicus)
- [Connecting live AIS vessel data](#connecting-live-ais-vessel-data)
- [Configuration page walkthrough](#configuration-page-walkthrough)
- [Tamil Nadu presets](#tamil-nadu-presets)
- [Dashboard pages](#dashboard-pages)
- [Alerts (email / SMS)](#alerts-email--sms)
- [Reports](#reports)
- [Configuration reference](#configuration-reference)
- [API reference](#api-reference)
- [AIS CSV file format](#ais-csv-file-format)
- [Project structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [Security notes](#security-notes)
- [Known limitations](#known-limitations)

---

## What it does

- **Live satellite monitoring** — Polls a satellite feed on a loop and runs spill detection on every new frame.
- **Oil spill detection** — A U-Net (ResNet34) model identifies the spill region and estimates what percentage of the frame it covers.
- **AIS vessel tracking** — Ranks nearby ships by proximity, speed, and heading relative to the spill.
- **Drift prediction** — 24-hour forecast of where the slick will move, using live weather and ocean current data.
- **Impact analysis** — Estimates environmental and economic damage, plus a national risk score.
- **Cleanup recommendation** — Suggests equipment, booms, actions, and resource priorities.
- **Alerts** — Shows on the dashboard, and optionally sends email (SMTP) or SMS (Twilio). Works fine if those aren't configured — it just won't send.
- **PDF reports** — One-click incident report generation for every detection.
- **Command UI** — Dashboard, live monitoring, marine map, image detection, reports, system health, and a 3D ocean globe.

---

## System requirements

- **OS** — Windows 10/11 (Linux/macOS work, but `start.bat` is Windows-only)
- **Python** — 3.10 to 3.12
- **Node.js** — 18+ (only if you're developing the frontend — the pre-built UI doesn't need it)
- **RAM** — 4 GB minimum, 8 GB recommended
- **Disk** — ~2 GB free
- **Internet** — Required for live satellite, AIS, and weather APIs

---

## Installation

### Clone the repo

The trained model (`models/fine_tuned/best_model.pth`, ~93 MB) is already in the repo — no separate download. Clone and you're set.

```bash
git clone https://github.com/umar1985rr-dev/OceanSpill.git
cd OceanSpill
```

That's it. Double-click `start.bat` and it handles everything else (creates the virtual environment, installs dependencies, builds the frontend, and starts the server).

### Manual setup (Linux/macOS or if you prefer)

```bash
python -m venv venv
source venv/bin/activate          # Linux/macOS
pip install -r backend\requirements.txt
```

### Frontend (only if you're developing)

The pre-built frontend in `frontend/dist/` is already served by the backend. Officials don't need to build it. To rebuild after making UI changes:

```bash
cd frontend
npm ci
npm run build
cd ..
```

---

## Quick start (one-click)

Just double-click **`start.bat`**. On the first run it will:

1. Create the virtual environment (if it doesn't exist yet).
2. Install all Python dependencies automatically.
3. Build the frontend (if `frontend/dist/index.html` is missing).
4. Start the backend on **http://localhost:8000** — everything (API + UI) runs on one port.
5. Open your browser to the dashboard.

On subsequent runs it skips the setup steps and just starts the server. The API docs are at **http://localhost:8000/docs** and the health check is at **http://localhost:8000/api/system/health**.

---

## Manual run

If you don't want to use `start.bat`, or you're on Linux/macOS:

```bash
./venv/Scripts/python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

The monitoring loop starts on its own. To run just the API without detection:

```bash
MONITOR_ENABLED=false ./venv/Scripts/python.exe -m uvicorn backend.main:app --reload
```

### Frontend dev mode (with hot reload)

```bash
cd frontend
npm run dev
```

Runs on `http://localhost:5173` and proxies API calls to port 8000. In production you don't need this — the backend serves the built SPA directly.

---

## What data do I need?

You need three things, all set from the **Configuration** page (no code, no file editing):

**1. Incident coordinates** — Where to watch. Set lat/lon manually or pick a Tamil Nadu preset. No credentials needed.

**2. Satellite imagery** — Either the built-in simulator (no setup) or live tiles from Copernicus (free account).

**3. AIS vessel positions** — Either upload a CSV, use the simulated-live mode (animates your CSV), or connect to AISHub (free) / MarineTraffic (paid).

> Weather and ocean current data for drift prediction come from Open-Meteo automatically — free, no API key.

### Which satellite feed should I use?

- **Want real satellite tiles?** Use [Copernicus Data Space](#connecting-live-satellite-imagery-copernicus). Free account, takes about 2 minutes.
- **Just evaluating or don't have an account yet?** Use the **Simulator** — it streams sample frames so everything works immediately.

### Which AIS source should I use?

- **Uploaded CSV** — Static file, free. Use this if you have existing historical AIS data.
- **Simulated Live** — Free, no setup. Animates your CSV so vessels move on the map. Good for demos.
- **AISHub** — Free with registration. Good for a first live deployment on a budget.
- **MarineTraffic** — Paid subscription. Best coverage for Indian waters.

---

## Connecting live satellite imagery (Copernicus)

The system pulls real Sentinel-2 / Sentinel-1 tiles from [Copernicus Data Space](https://dataspace.copernicus.eu) (ESA's free platform). Covers Tamil Nadu coastal waters and basically everywhere else.

### Step 1 — Create a free account

Go to **https://dataspace.copernicus.eu** → Sign up (free). Verify your email and log in once.

### Step 2 — Enter credentials

Either way works (UI settings override environment variables):

- **Config UI** → **Satellite Feed** card → enter your username and password, or your OAuth client ID and secret if you created one in the CDSE dashboard.
- **Or** set env vars: `COPERNICUS_USERNAME` / `COPERNICUS_PASSWORD` (or `COPERNICUS_CLIENT_ID` / `COPERNICUS_CLIENT_SECRET`).

### Step 3 — Switch to live

Config UI → **Satellite Feed** → **Source** → **Sentinel Hub / Copernicus (live)**.

### Step 4 — Pick a layer

Config UI → **Satellite Layer**:
- **TRUE_COLOR** — Sentinel-2 optical imagery (default).
- **SAR** — Sentinel-1 radar. Use this if your detection model was trained on SAR-style frames.

### Step 5 — Test it

Click **Test connection** in the Satellite Feed card. Green badge = good to go.

### What happens at runtime

- A tile around the incident coordinates gets saved to `outputs/live_frames/frame_<timestamp>.jpg`.
- Since satellites only revisit every few days, the tile is **cached** (default 600 s) instead of re-downloading every loop. The system recognises the cached frame and skips duplicate incidents.
- If credentials are wrong, the loop logs an error, shows it in System Health, and keeps running. It won't crash.

---

## Connecting live AIS vessel data

### Option A — Upload a CSV (static file)

Config UI → **AIS Feed** → upload your CSV. It gets validated against the required columns (see [AIS CSV file format](#ais-csv-file-format)). Bad files are rejected with a 400 error listing exactly what's missing.

### Option B — Simulated Live (no credentials)

Pick **Simulated Live**. The system reads your CSV once, grabs the latest position of every vessel, and advances each one along its course/speed so ships move between polls. Zero setup.

### Option C — AISHub (free, with registration)

1. Register at **https://data.aishub.net/** and grab your API key.
2. Config UI → **AIS Feed** → Source **AISHub** → enter your username and API key.
3. Set the refresh interval (default 300 s).
4. Click **Test**.

The feed is filtered to a bounding box around the incident coordinates (see `ais_bbox_span`).

### Option D — MarineTraffic (paid, best for Indian waters)

1. Subscribe at **https://www.marinetraffic.com** or Kpler and get an API key.
2. Config UI → **AIS Feed** → Source **MarineTraffic** → enter the key.
3. Set the refresh interval and click **Test**.

> MarineTraffic is migrating to Kpler. If the default endpoint stops working, check your account docs — the endpoint is a single constant in `backend/services/ais_analysis/provider.py`.

---

## Configuration page walkthrough

Open the app → **Configuration** in the sidebar.

**Model Settings** — Incident lat/lon, detection threshold (minimum spill % to trigger a full response), monitoring interval, feed source, simulator image directory.

**Tamil Nadu presets** — One-click coordinate fills for Chennai, Gulf of Mannar, Nagapattinam, and Rameswaram.

**Satellite Feed** — Live vs simulator, credentials (masked), satellite layer, frame cache TTL, bbox span. Has a Test connection button and a live status badge.

**AIS Feed** — Source selector, API keys, refresh interval, bbox span. Also has Test and status.

**Dataset uploads** — AIS CSV, satellite images, coastlines, ports, fishing zones, protected areas, mangroves, coral reefs, ocean currents.

Every **Save** writes to `runtime_config.json` and takes effect immediately — no restart needed.

---

## Tamil Nadu presets

One-click coordinates under Model Settings:

- **Chennai** — 13.08, 80.27
- **Gulf of Mannar / Tuticorin** — 8.76, 78.13
- **Nagapattinam** — 10.77, 79.84
- **Rameswaram** — 9.29, 79.31

Or just type any lat/lon — works anywhere in the world.

---

## Dashboard pages

- **Dashboard** — Live detection stats, recent incidents, alerts, system health summary.
- **Live Monitoring** — Current satellite frame with spill overlay, live from the feed.
- **Marine Map** — Leaflet map with spill location, drift path, risk zones, and nearby vessels.
- **Image Detection** — Upload a single image and run detection on demand.
- **Reports** — Generated PDF incident reports, newest first.
- **System Health** — Per-module health checks for every service.
- **Configuration** — All live data connections, coordinates, thresholds, and uploads.

> A lightweight 3D ocean globe is embedded in the **Dashboard** and **Marine Map** pages. Falls back gracefully if WebGL isn't available.

---

## Alerts (email / SMS)

Alerts always show on the dashboard. Email and SMS are optional.

### Email (SMTP)

Set these environment variables, then restart:

```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
EMAIL_ADDRESS=you@example.com
EMAIL_PASSWORD=<app password>
EMAIL_RECIPIENTS=officer@example.com,chief@example.com
```

> Gmail requires an **App Password** (Google Account → Security → 2-Step Verification → App passwords). Don't use your regular password.

### SMS (Twilio)

```
SMS_PROVIDER=twilio
TWILIO_ACCOUNT_SID=ACxxxx
TWILIO_AUTH_TOKEN=xxxx
TWILIO_FROM=+1234567890
SMS_RECIPIENTS=+9198...,+9190...
```

With `SMS_PROVIDER=SIMULATED` (default), SMS alerts are just logged — not sent. Handy for demos.

---

## Reports

- **`GET /api/report/generate`** — Builds a PDF incident report for the latest detection.
- **`GET /api/report/latest`** — Returns the most recent report.
- Reports show up on the **Reports** page in the UI.

---

## Configuration reference

### Environment variables

Set these in a `.env` file or your shell before starting the server:

**Application**

- `APP_NAME` — Default: `OceanSpill`. Name used in reports.
- `DEBUG` — Default: `true`.
- `HOST` — Default: `0.0.0.0`.
- `PORT` — Default: `8000`.

**Satellite feed**

- `FEED_SOURCE` — Default: `simulator`. Options: `simulator`, `sentinel_hub`.
- `SIMULATOR_IMAGES_DIR` — Default: `dataset/samples/satellite_images`.
- `COPERNICUS_USERNAME` / `COPERNICUS_PASSWORD` — For live satellite (free account).
- `COPERNICUS_CLIENT_ID` / `COPERNICUS_CLIENT_SECRET` — For live satellite (OAuth).

**Monitoring**

- `INCIDENT_LATITUDE` / `INCIDENT_LONGITUDE` — Default: `29.78` / `-90.10`.
- `MONITOR_ENABLED` — Default: `true`.
- `MONITOR_INTERVAL_SECONDS` — Default: `30`.
- `DETECTION_THRESHOLD` — Default: `1.0` (min spill % to trigger a response).

**AIS**

- `AISHUB_USERNAME` / `AISHUB_API_KEY` — For free live AIS.
- `MARINE_TRAFFIC_API_KEY` — For paid live AIS.

**Alerts**

- `SMTP_HOST` / `SMTP_PORT` — Default: `smtp.gmail.com` / `587`.
- `EMAIL_ADDRESS` / `EMAIL_PASSWORD` — Sender credentials.
- `EMAIL_RECIPIENTS` — Comma-separated.
- `SMS_PROVIDER` — Default: `SIMULATED`. Set to `twilio` to enable.
- `TWILIO_ACCOUNT_SID` / `TWILIO_AUTH_TOKEN` / `TWILIO_FROM` — Twilio creds.
- `SMS_RECIPIENTS` — Comma-separated.
- `CURRENCY` — Default: `₹`. Currency symbol in impact estimates.

### Runtime config (UI → `runtime_config.json`)

These are editable from the Configuration page and take effect without restarting:

- `incident_latitude` / `incident_longitude` — Where to monitor.
- `detection_threshold` — Default: `1.0`.
- `monitor_interval_seconds` — Default: `30`.
- `feed_source` — Default: `simulator`.
- `simulator_images_dir` — Default: `dataset/samples/satellite_images`.
- `ais_csv_path` — Default: `dataset/raw/ais_data/ais_data.csv`.
- `copernicus_username` / `copernicus_password` — Live satellite creds.
- `copernicus_client_id` / `copernicus_client_secret` — Live satellite OAuth.
- `satellite_layer` — Default: `TRUE_COLOR`. Options: `TRUE_COLOR`, `SAR`.
- `frame_cache_ttl_seconds` — Default: `600`.
- `satellite_bbox_span` — Default: `0.1`.
- `ais_source` — Default: `csv`. Options: `csv`, `simulated_live`, `aishub`, `marinetraffic`.
- `ais_refresh_interval_seconds` — Default: `300`.
- `marine_traffic_api_key` — MarineTraffic key.
- `aishub_username` / `aishub_api_key` — AISHub creds.
- `ais_bbox_span` — Default: `2.0`.

---

## API reference

All routes are under `/api/`. Interactive docs at **http://localhost:8000/docs**.

**Monitoring** — `GET /api/monitoring/status`, `GET /api/monitoring/start`, `GET /api/monitoring/stop`, `GET /api/monitoring/history`, `GET /api/monitoring/incidents`

**Configuration** — `GET /api/config`, `PUT /api/config`, `POST /api/config/upload/{dataset}`, `GET /api/config/datasets`, `POST /api/config/test`

**AIS** — `GET /api/ais/suspect-vessels`, `GET /api/ais/nearby-vessels`, `GET /api/ais/movement-analysis`, `GET /api/ais/map`, `GET /api/ais/health`

**Detection** — `POST /api/detection/predict`, `GET /api/detection/model-info`, `GET /api/detection/health`

**Drift** — `GET /api/drift/predict`, `GET /api/drift/path`, `GET /api/drift/risk-zones`, `GET /api/drift/map`

**Impact** — `GET /api/impact/environment`, `GET /api/impact/economic`, `GET /api/impact/risk`, `GET /api/impact/dashboard`, `GET /api/impact/summary`

**Cleanup** — `GET /api/cleanup/recommend`

**Reports** — `GET /api/report/generate`, `GET /api/report/latest`

**Weather & alerts** — `GET /api/weather/current`, `GET /api/alerts/history`, `GET /api/alerts/current`

**System** — `GET /api/system/health`

---

## AIS CSV file format

Your uploaded CSV needs all of these columns (extras are fine):

```
MMSI, LAT, LON, BaseDateTime, SOG, COG, IMO, VesselType
```

- **MMSI** — Maritime Mobile Service Identity (e.g. `565984000`)
- **LAT / LON** — Position in decimal degrees (e.g. `13.0827`, `80.2707`)
- **BaseDateTime** — Format: `YYYY-MM-DD HH:MM:SS` (e.g. `2025-01-15 08:32:00`)
- **SOG** — Speed over ground in knots (e.g. `12.4`)
- **COG** — Course over ground in degrees (e.g. `215.0`)
- **IMO** — IMO number (can be empty)
- **VesselType** — Numeric vessel type code (e.g. `70`)

Upload a file with missing columns and you'll get a `400` error listing exactly what's wrong. The bad file gets deleted and the old AIS data stays active.

---

## Project structure

```
OceanSpill/
├─ start.bat                      # Double-click to run (Windows)
├─ runtime_config.json            # Live settings written by the Config UI
├─ backend/
│  ├─ main.py                     # FastAPI app — SPA + API on one port
│  ├─ config.py                   # Environment variable settings
│  ├─ api/                        # Routers (all under /api/)
│  └─ services/
│     ├─ monitoring/              # Detection loop + state
│     ├─ satellite_feed/          # Simulator + Copernicus live
│     ├─ oil_detector/            # U-Net inference + overlay
│     ├─ ais_analysis/            # Providers, loader, validator, ranking
│     ├─ drift_prediction/        # Weather + current drift forecast
│     ├─ impact_analysis/         # Environmental/economic impact
│     ├─ cleanup_recommender/     # Response planning
│     ├─ alerts/                  # Dashboard / email / SMS
│     └─ report_generator/        # PDF reports
├─ frontend/
│  ├─ dist/                       # Pre-built UI (served by backend)
│  └─ src/pages/                  # Dashboard, Config, LiveMonitoring, etc.
├─ models/
│  └─ fine_tuned/best_model.pth   # Trained model (~93 MB, included)
├─ dataset/                       # Sample/uploaded datasets
└─ outputs/                       # Live frames, reports (runtime)
```

---

## Troubleshooting

- **`start.bat` says "backend offline"** — Port 8000 is already in use. Close the other program, or try a different port: `PORT=8001 ./venv/Scripts/python.exe -m uvicorn backend.main:app`.

- **Satellite feed says "credentials not configured"** — You chose Sentinel Hub live but haven't entered credentials yet. Add them in the Config UI or set the env vars.

- **Satellite feed shows an error but the app doesn't crash** — That's intentional. The loop keeps running. Fix the credentials and it recovers on the next tick.

- **AIS shows `Missing AIS columns: [...]`** — Your CSV is missing required columns. Check the [format spec](#ais-csv-file-format).

- **System Health shows a module OFFLINE** — That module's data source isn't configured. Check its section in the Configuration page.

- **`/config` shows JSON instead of the UI** — You hit the API endpoint directly. The UI page is at `/config` in the sidebar; API routes are all under `/api/`.

- **Model not found** — The model should be at `models/fine_tuned/best_model.pth`. It's included in the repo. Detection gets skipped gracefully if it's missing.

- **No incidents ever detected** — Spills below `detection_threshold` won't trigger. Or the simulator has no frames after the dataset was removed. Lower the threshold or switch to a live feed.

---

## Security notes

- Credentials saved through the Config UI are stored as **plain text** in `runtime_config.json`. Keep the machine and that file secured.
- API keys are masked in the UI (shown as `••••`), but the actual values travel to the backend over your network. For production use, put this behind HTTPS or a VPN.
- The server binds to `0.0.0.0` by default, so it's reachable on your local network. Use a trusted machine.

---

## Known limitations

- **Detection on live optical tiles** — The bundled model was trained on SAR-style frames. Live Sentinel-2 optical tiles might not detect as accurately. Set the layer to SAR (Sentinel-1) or retrain on optical data.
- **MarineTraffic endpoint** — MarineTraffic is migrating to Kpler. If the endpoint breaks, update `BASE_URL` in `backend/services/ais_analysis/provider.py`.
- **Copernicus cloud cover** — Optical tiles can be obscured by clouds (the feed requests ≤ 50%). SAR layers work regardless of weather.
- **Simulator needs frames** — After the training dataset was removed, the simulator might have no sample frames. Live feeds are the intended path for real deployments.

---

## Version 1

This is version 1. It works, it's functional, and it's built to be expanded. You can customize pretty much whatever you want — the detection model, the UI, the data sources, the alert logic, the report format, the drift parameters. The code is modular (each service is its own thing) so you can swap out or extend any piece without breaking the rest. Fork it, tweak it, make it yours.
