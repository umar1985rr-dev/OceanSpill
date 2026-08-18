# OceanSpill — AI-Powered Oil Spill Detection & Response

A platform that watches satellite imagery for oil spills, identifies which ships might be responsible, predicts where the slick is heading, and puts together an incident report — all from your browser.

Built for coast guards, port authorities, and marine departments. You don't need to code anything. Set it up once through the in-app Configuration page and let it run.

---

## Table of Contents

- [What it does](#what-it-does)
- [System requirements](#system-requirements)
- [Quick start](#quick-start)
- [Setup files reference](#setup-files-reference)
- [Installation details](#installation-details)
- [Connecting data sources](#connecting-data-sources)
- [Dashboard and features](#dashboard-and-features)
- [Authentication & users](#authentication--users)
- [Database](#database)
- [Docker deployment](#docker-deployment)
- [Configuration reference](#configuration-reference)
- [API reference](#api-reference)
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
- **Alerts** — Shows on the dashboard, and optionally sends email (SMTP) or SMS (Twilio).
- **PDF reports** — One-click incident report generation for every detection.
- **Command UI** — Dashboard, live monitoring, marine map, image detection, reports, system health, and a 3D ocean globe.

---

## System requirements

| Requirement | Details |
|-------------|---------|
| **OS** | Windows 10/11 (Linux/macOS work, but setup scripts are Windows-only) |
| **Python** | 3.10 to 3.12 |
| **Node.js** | 18+ (only needed for frontend development) |
| **RAM** | 4 GB minimum, 8 GB recommended |
| **Disk** | ~2 GB free |
| **Internet** | Required for live satellite, AIS, weather APIs, **and model download on first run** |

> The pre-built frontend in `frontend/dist/` is served by the backend. Officials don't need Node.js unless developing the UI.

---

## Quick start

### Option 1: One-Click (Recommended)

```
1. Clone the repo
2. Double-click start.bat
3. Open http://localhost:8000
```

That's it. `start.bat` automatically:
- Creates Python virtual environment
- Installs all dependencies
- **Downloads the AI model (~98 MB) from GitHub Releases on first run**
- Builds the frontend (if needed)
- Starts the server

> **Model download:** The U-Net model (~98 MB) is **not** bundled in the repo. On first run, `start.bat` downloads it from [GitHub Releases](https://github.com/umar1985rr-dev/OceanSpill/releases/tag/v1.0.0-model). Subsequent runs skip the download — it only happens once.

### Option 2: Check requirements only

```bash
python check_requirements.py        # Shows what's missing
python check_requirements.py --auto # Auto-fixes missing packages
```

### Option 4: Manual setup

```bash
# Clone
git clone https://github.com/umar1985rr-dev/OceanSpill.git
cd OceanSpill

# Python
python -m venv venv
venv\Scripts\activate
pip install -r backend\requirements.txt

# Download model (first time only)
# Download from: https://github.com/umar1985rr-dev/OceanSpill/releases/download/v1.0.0-model/best_model.pth
# Place at: models/fine_tuned/best_model.pth

# Frontend (development only)
cd frontend && npm install && npm run build && cd ..

# Run
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## Setup files reference

| File | Purpose |
|------|---------|
| **`start.bat`** | One-click launcher — creates venv, installs packages, builds frontend, starts server |
| **`check_requirements.py`** | Standalone requirements checker — shows what's missing without installing |

---

## Installation details

### First-time setup (what happens)

1. `start.bat` checks if Python is installed
2. Creates `venv/` virtual environment
3. Runs `pip install -r backend/requirements.txt`
4. **Downloads the AI model (~98 MB) from GitHub Releases** (first run only)
5. Checks if Node.js is installed
6. Runs `npm install` and `npm run build` in `frontend/`
7. Starts the server at **http://localhost:8000**

### Subsequent runs

On second run, it skips setup and just starts the server.

### Server endpoints

| URL | Description |
|-----|-------------|
| http://localhost:8000 | Main application |
| http://localhost:8000/docs | API documentation |
| http://localhost:8000/api/system/health | Health check |

### Frontend development

```bash
cd frontend
npm run dev
# Opens at http://localhost:5173 with hot reload
```

---

## Connecting data sources

You need three things, all set from the **Configuration** page (no code, no file editing):

### 1. Incident coordinates

Where to watch. Set lat/lon manually or pick a Tamil Nadu preset.

**Tamil Nadu presets:**
| Location | Latitude | Longitude |
|----------|----------|-----------|
| Chennai | 13.08 | 80.27 |
| Gulf of Mannar / Tuticorin | 8.76 | 78.13 |
| Nagapattinam | 10.77 | 79.84 |
| Rameswaram | 9.29 | 79.31 |

### 2. Satellite imagery

| Source | Setup | Cost |
|--------|-------|------|
| **Simulator** | None — works immediately | Free |
| **Copernicus** | Free account at dataspace.copernicus.eu | Free |

For live satellite:
1. Create account at https://dataspace.copernicus.eu
2. Enter credentials in Config UI → Satellite Feed
3. Switch Source to "Sentinel Hub / Copernicus (live)"
4. Click "Test connection"

> Weather data comes from Open-Meteo automatically — no setup needed.

### 3. AIS vessel positions

| Source | Setup | Cost |
|--------|-------|------|
| **Uploaded CSV** | Upload file | Free |
| **Simulated Live** | None — animates your CSV | Free |
| **AISHub** | Register at data.aishub.net | Free |
| **MarineTraffic** | Paid subscription | Paid |

Upload a CSV with these columns:
```
MMSI, LAT, LON, BaseDateTime, SOG, COG, IMO, VesselType
```

### Which should I use?

**Satellite:** Use Simulator for demos, Copernicus for real deployments.

**AIS:** Use Simulated Live for demos, AISHub for free live tracking, MarineTraffic for best coverage.

---

## Dashboard and features

### Pages

| Page | Description |
|------|-------------|
| **Dashboard** | Live stats, recent incidents, alerts, system health |
| **Live Monitoring** | Current satellite frame with spill overlay |
| **Marine Map** | Leaflet map with spill location, drift path, vessels |
| **Image Detection** | Upload image and run detection on demand |
| **Reports** | Generated PDF incident reports |
| **System Health** | Per-module health checks |
| **Configuration** | All data connections and settings |

### Alerts

Alerts always show on the dashboard. Optional email/SMS:

**Email (SMTP):**
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
EMAIL_ADDRESS=you@example.com
EMAIL_PASSWORD=<app password>
EMAIL_RECIPIENTS=officer@example.com
```

> Gmail requires an **App Password**, not your regular password.

**SMS (Twilio):**
```
SMS_PROVIDER=twilio
TWILIO_ACCOUNT_SID=ACxxxx
TWILIO_AUTH_TOKEN=xxxx
TWILIO_FROM=+1234567890
SMS_RECIPIENTS=+9198...
```

Set `SMS_PROVIDER=SIMULATED` (default) for demo mode — SMS logged but not sent.

---

## Authentication & users

OceanSpill includes role-based access control (RBAC) built on JWT tokens.

### Roles

| Role | Permissions |
|------|-------------|
| **admin** | Full access: users, incidents, config, all APIs |
| **operator** | Manage incidents & monitoring, view users |
| **viewer** | Read-only access |

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Create account (first user = admin) |
| POST | `/api/auth/login` | Get tokens (24h access, 7d refresh) |
| POST | `/api/auth/refresh` | Refresh tokens |
| POST | `/api/auth/logout` | Discard tokens |
| GET | `/api/auth/me` | Current user profile |
| GET | `/api/users` | List users (admin/operator) |
| POST | `/api/users` | Create user (admin) |
| PATCH | `/api/users/{id}` | Update user |
| DELETE | `/api/users/{id}` | Delete user (admin) |

### API versioning

- `/api/v1/...` — Current version
- `/api/...` — Legacy aliases for backward compatibility

---

## Database

All data stored in **SQLite** at `data/oceanspill.db` — zero-config, free, backed up by copying one file.

| Table | Content |
|-------|---------|
| **users** | Accounts, roles, activity |
| **incidents** | Every detected spill with impact/drift data |
| **vessels** | Cached AIS positions |
| **config** | Runtime settings |
| **alert_history** | Alert audit trail |

---

## Docker deployment

```bash
# Build and run
docker-compose up -d --build

# Or manually
docker build -t oceanspill .
docker run -p 8000:8000 -v oceanspill-data:/app/data oceanspill
```

Features:
- No external services (SQLite persists via named volumes)
- Non-root user
- Health check at `/api/v1/system/health`
- GitHub Actions CI/CD included

---

## Configuration reference

### Environment variables

**Application:**
| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | OceanSpill | Name in reports |
| `DEBUG` | true | Debug mode |
| `HOST` | 0.0.0.0 | Bind address |
| `PORT` | 8000 | Server port |

**Monitoring:**
| Variable | Default | Description |
|----------|---------|-------------|
| `INCIDENT_LATITUDE` | 29.78 | Monitor latitude |
| `INCIDENT_LONGITUDE` | -90.10 | Monitor longitude |
| `MONITOR_ENABLED` | true | Enable monitoring loop |
| `MONITOR_INTERVAL_SECONDS` | 30 | Loop interval |
| `DETECTION_THRESHOLD` | 1.0 | Min spill % to trigger |

**Satellite:**
| Variable | Default | Description |
|----------|---------|-------------|
| `FEED_SOURCE` | simulator | simulator or sentinel_hub |
| `COPERNICUS_USERNAME` | - | Copernicus account |
| `COPERNICUS_PASSWORD` | - | Copernicus password |

**AIS:**
| Variable | Default | Description |
|----------|---------|-------------|
| `AISHUB_USERNAME` | - | AISHub username |
| `AISHUB_API_KEY` | - | AISHub API key |
| `MARINE_TRAFFIC_API_KEY` | - | MarineTraffic key |

**Alerts:**
| Variable | Default | Description |
|----------|---------|-------------|
| `SMTP_HOST` | smtp.gmail.com | SMTP server |
| `SMTP_PORT` | 587 | SMTP port |
| `EMAIL_ADDRESS` | - | Sender email |
| `EMAIL_PASSWORD` | - | Sender password |
| `SMS_PROVIDER` | SIMULATED | twilio or SIMULATED |
| `TWILIO_ACCOUNT_SID` | - | Twilio SID |
| `TWILIO_AUTH_TOKEN` | - | Twilio token |
| `CURRENCY` | ₹ | Currency symbol |

### Runtime config (from Config UI)

Editable without restarting:

- `incident_latitude` / `incident_longitude` — Where to monitor
- `detection_threshold` — Default: 1.0
- `monitor_interval_seconds` — Default: 30
- `feed_source` — Default: simulator
- `satellite_layer` — TRUE_COLOR or SAR
- `ais_source` — csv, simulated_live, aishub, or marinetraffic
- `ais_refresh_interval_seconds` — Default: 300

---

## API reference

All routes under `/api/`. Docs at **http://localhost:8000/docs**.

### Endpoints

| Category | Endpoints |
|----------|-----------|
| **Monitoring** | `/api/monitoring/status`, `/start`, `/stop`, `/history`, `/incidents` |
| **Configuration** | `/api/config` (GET, PUT), `/upload/{dataset}`, `/datasets`, `/test` |
| **AIS** | `/api/ais/suspect-vessels`, `/nearby-vessels`, `/movement-analysis`, `/map`, `/health` |
| **Detection** | `/api/detection/predict`, `/model-info`, `/health` |
| **Drift** | `/api/drift/predict`, `/path`, `/risk-zones`, `/map` |
| **Impact** | `/api/impact/environment`, `/economic`, `/risk`, `/dashboard`, `/summary` |
| **Cleanup** | `/api/cleanup/recommend` |
| **Reports** | `/api/report/generate`, `/latest` |
| **Weather** | `/api/weather/current` |
| **Alerts** | `/api/alerts/history`, `/current` |
| **System** | `/api/system/health` |
| **Auth** | `/api/auth/register`, `/login`, `/refresh`, `/logout`, `/me`, `/change-password` |
| **Users** | `/api/users` (GET, POST), `/users/{id}` (PATCH, DELETE) |

---

## Project structure

```
OceanSpill/
|
|-- Scripts & Config --
|  ├─ start.bat                      # One-click launcher (Windows)
|  ├─ check_requirements.py          # Requirements checker
|  ├─ runtime_config.json            # Live settings (created by Config UI)
|  ├─ Dockerfile                     # Multi-stage production build
|  ├─ docker-compose.yml             # Single-container deployment
|  ├─ .dockerignore                  # Build context optimization
|  └─ .github/workflows/ci.yml       # GitHub Actions CI/CD
|
|-- Backend --
|  └─ backend/
|     ├─ main.py                     # FastAPI app (SPA + API on port 8000)
|     ├─ config.py                   # Environment variables
|     ├─ database.py                 # SQLite + SQLAlchemy
|     ├─ api/
|     │  ├─ auth.py                  # JWT register/login/refresh
|     │  ├─ users.py                 # User management (RBAC)
|     │  ├─ incidents.py             # Incident CRUD + stats
|     │  └─ [monitoring, weather, ais, detection, drift, etc.]
|     ├─ core/
|     │  ├─ security.py              # JWT, bcrypt
|     │  ├─ middleware.py            # Rate limiting
|     │  └─ exceptions.py            # Error handling
|     ├─ models/
|     │  ├─ user.py                  # User accounts
|     │  ├─ incident.py              # Oil spill incidents
|     │  ├─ vessel.py                # AIS vessel cache
|     │  └─ config.py                # Runtime config + alerts
|     └─ services/
|        ├─ monitoring/              # Detection loop + state
|        ├─ satellite_feed/          # Simulator + Copernicus
|        ├─ oil_detector/            # U-Net inference
|        ├─ ais_analysis/            # Vessel ranking
|        ├─ drift_prediction/        # Weather + current drift
|        ├─ impact_analysis/         # Environmental/economic
|        ├─ cleanup_recommender/     # Response planning
|        ├─ alerts/                  # Dashboard/email/SMS
|        └─ report_generator/        # PDF reports
|
|-- Frontend --
|  └─ frontend/
|     ├─ dist/                       # Pre-built UI (served by backend)
|     └─ src/pages/                  # React pages (development)
|
|-- Data & Models --
|  ├─ models/fine_tuned/best_model.pth  # Trained model (~98 MB, downloaded on first run from GitHub Releases)
|  ├─ dataset/                       # Sample/uploaded datasets
|  ├─ data/                          # SQLite database (gitignored)
|  ├─ outputs/                       # Live frames (runtime)
|  └─ reports/                       # Generated PDFs (runtime)
```

---

## Troubleshooting

### Installation Issues

| Problem | Solution |
|---------|----------|
| **"Python not found"** | Download from https://python.org/downloads/ and CHECK "Add Python to PATH" |
| **"npm install" fails** | Install Node.js from https://nodejs.org/, delete `frontend/node_modules` and `frontend/package-lock.json`, then run `start.bat` again |
| **Frontend not opening** | Run: `cd frontend && npm install && npm run build` |
| **"Module not found" errors** | Run: `python check_requirements.py --auto` or `venv\Scripts\activate && pip install -r backend\requirements.txt` |
| **Port 8000 in use** | Stop other program, or run: `set PORT=8001 && python -m uvicorn backend.main:app --reload` |

### Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| **"backend offline"** | Port 8000 in use | Close other program or use different port |
| **"credentials not configured"** | Sentinel Hub selected but no credentials | Add credentials in Config UI |
| **"Missing AIS columns: [...]"** | CSV missing required columns | Check format in [AIS CSV format](#ais-csv-file-format) |
| **Module OFFLINE in System Health** | Data source not configured | Check that section in Configuration page |
| **Model not found** | Model file missing | Should be at `models/fine_tuned/best_model.pth` — `start.bat` auto-downloads it from GitHub Releases on first run |
| **Model download fails** | Network/permission issue | Manually download from [GitHub Releases](https://github.com/umar1985rr-dev/OceanSpill/releases/tag/v1.0.0-model) and place at `models/fine_tuned/best_model.pth` |
| **No incidents detected** | Spills below threshold | Lower `detection_threshold` or switch to live feed |
| **`/config` shows JSON** | You're at API endpoint | Navigate to Config page in sidebar |

### Manual recovery steps

```bash
# Clean reinstall
rmdir /s /q venv
rmdir /s /q frontend\node_modules
del /f frontend\package-lock.json

# Fresh setup
start.bat
```

---

## Security notes

- Credentials saved through the Config UI are stored as **plain text** in `runtime_config.json`. Keep the machine and that file secured.
- API keys are masked in the UI (shown as `••••`), but values travel to the backend over your network.
- The server binds to `0.0.0.0` by default, so it's reachable on your local network. Use a trusted machine.
- For production use, put this behind HTTPS or a VPN.

---

## Known limitations

| Limitation | Details |
|------------|---------|
| **Optical tile detection** | Model trained on SAR-style frames. Live Sentinel-2 optical tiles may be less accurate. Use SAR layer or retrain. |
| **MarineTraffic migration** | MarineTraffic is migrating to Kpler. Update `BASE_URL` in `backend/services/ais_analysis/provider.py` if needed. |
| **Copernicus cloud cover** | Optical tiles can be obscured by clouds (≤50% requested). SAR layers work in any weather. |
| **Simulator frames** | After training dataset removal, simulator may have no sample frames. Live feeds are the intended path. |

---

## Version 1

This is version 1. It works, it's functional, and it's built to be expanded. You can customize the detection model, UI, data sources, alert logic, report format, and drift parameters. The code is modular — each service is independent so you can swap or extend any piece without breaking the rest. Fork it, tweak it, make it yours.