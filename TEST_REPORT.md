# OceanSpill — End-to-End Test & Fix Report

**Date:** 2026-08-31
**Scope:** Full API surface (99 endpoints), frontend integration, security, mock data, RBAC.
**Runtime:** System Python 3.12, SQLite, uvicorn :8000.

---

## 1. Bugs Found & Fixed

| # | Severity | Area | Description | Status |
|---|----------|------|-------------|--------|
| 2 | 🔴 Critical | Frontend | `api.js` baseURL `undefined` → every API call hit the FastAPI SPA catch-all and returned `index.html` instead of JSON (wrong URL when no `VITE_API_URL` set). | ✅ Fixed (`\|\| "http://127.0.0.1:8000"`) |
| 3 | 🟠 High | Git | `.gitignore` bare `dist/` silently ignored `frontend/dist/`, contradicting "dist IS committed". | ✅ Fixed (`!frontend/dist/`) |
| 6 | 🔴 Critical | Backend | passlib 1.7.4 broken with bcrypt ≥4.1 → registration/login impossible. | ✅ Fixed (direct bcrypt) |
| 7 | 🟠 High | Auth | `GET /api/auth/me` with no token → **500** (called `.to_dict()` on `None`). | ✅ Fixed (401) |
| 8 | 🟠 High | Config | `PUT /api/config` accepted `"not_a_number"` for numeric keys — corrupted persisted config. | ✅ Fixed (type+range validation → 400) |
| 11 | 🟠 High | Incidents | `GET/PATCH /api/incidents/{id}` expected an **integer** id, but the API returns string ids (`INC-...`) everywhere else. | ✅ Fixed (accepts both) |
| 12 | 🟠 High | Auth/RBAC | Unauthenticated `GET /api/users`, `PATCH /api/incidents` → **500** `'NoneType' has no attribute 'role'` (role check on absent user). | ✅ Fixed (401) |
| 13 | 🔴 Critical | Frontend | Every frontend call used bare paths (`/weather/current`, `/config`, …) with baseURL `http://127.0.0.1:8000` — but the API is served under `/api/...`. **Entire dashboard returned HTML, not data.** | ✅ Fixed (`baseURL: \`${API_URL}/api\``) + rebuilt `dist/` |

### Bug #2 vs #13 (no double-count)
- **#2** was the *original* defect: no fallback URL → offline builds sent requests to the wrong host.
- **#13** is the *persisting* defect: correct host but missing `/api` prefix. Both are in `api.js`; the final file fixes both with one baseURL.

---

## 2. Bugs Found — Not Yet Fixed (documented)

| # | Severity | Area | Description |
|---|----------|------|-------------|
| 4 | 🟡 Medium | Satellite feed | `simulator.connect()` caches `image_paths` once; files added after boot are never seen until restart. Recommend re-scan each `get_frame()`. |
| 9 | 🟡 Medium | Config/UI | `GET /api/config/datasets` shows the **same 7 files** for `coastlines`, `protected_areas`, `mangroves`, `coral_reefs`, `fishing_zones`, `ports` (all map to `dataset/raw/geographic/`) — can't tell which specific dataset was uploaded. |
| 10 | 🟠 High | Detection | Uploading a corrupt/truncated image → **HTTP 500** with misleading `"Image not found: uploads\..."` — should be **400** with a real parse-error message. |
| — | 🟡 Medium | Design | `start`/`stop` monitoring are **GET** endpoints (side-effecting). A prefetch/curl GET can toggle monitoring. Should be POST. |
| — | 🟡 Medium | Report | `.gitignore` ignores `*.csv` — but runtime report/economic files rely on data dirs; verify nothing needed for startup is accidentally untracked. |

---

## 3. Verified Working (all pass)

- **Auth (14 tests):** register (first user→admin, dup username/email 409), login (correct/incorrect/disabled), token refresh, change-password, logout, `me`. JWT expiry/`type` checks enforced. Tampered/forged JWTs → **401** (signature + alg enforced).
- **Config:** GET, typed PUT (valid + rejected invalid), `/datasets`, `/upload/{dataset}`, `/test`. Valid AIS upload accepted; missing-column AIS **rejected 400** (`Missing AIS columns: ['IMO', 'VesselType']`); unknown dataset → 400.
- **Monitoring:** status (instance_id, version, feed, frames), history, incidents, start/stop. Detections flowing into DB (219 incidents, REAL model output from synthetic frames).
- **Detection:** health, model-info (U-Net/ResNet34), predict (✓ real 99.9% confidence, mask/overlay saved to `outputs/`).
- **Drift:** predict/path/risk-zones/map (wind+current integration, 6-hr path, HTML map).
- **Impact:** summary/risk/environment/economic/dashboard (coastline/port/mangrove/coral/fishing + $ economic loss).
- **AIS:** health, nearby-vessels, suspect-vessels, movement-analysis, map (real MMSI/IMO from mock CSV).
- **Alerts/Incidents/Cleanup/Report/System/Weather/Users:** all functional. PDF report generated verbatim (`%PDF-1.4`).
- **RBAC:** viewer blocked from delete-user/patch-incident (**403**); operator can patch incidents but not delete users or change roles (**403**); admin full. *Unauthenticated* now **401** (was 500).

---

## 4. Security Testing Results

| Check | Result |
|-------|--------|
| SQL injection (login, filters) | ✅ Rejected (parameterized queries) |
| JWT tampering / forged `role=admin`, bad sig | ✅ 401 (HS256 sig + `type: access` verified) |
| RBAC privilege escalation | ✅ 403 enforced |
| Unauthenticated protected routes | ✅ 401 now (was 500) |
| Stored XSS vector (`<script>` in `full_name`) | ⚠️ Stored unescaped — **no sanitization** (low risk on local admin-only UI; recommend escaping at render) |
| Rate limiting / brute-force | ❌ **None** — 20 rapid failed logins all 401, never 429. Add per-IP/login throttling. |
| Hardcoded `SECRET_KEY` in `security.py` | ⚠️ `"oceanspill-secret-key-change-..."` — move to env for production. |

---

## 5. Architecture Notes (for the "click start" experience)

- **Vite/Node are build-time only** — not needed at runtime. The committed `frontend/dist/` (post-build) is served by FastAPI. The `.gitignore` fix (#3) means the built bundle is now actually committed, so `start.bat` skips `npm install`/`build` for end users.
- **No Docker in repo** despite assumptions; this is a pure `python start.bat` + SQLite app. A Dockerfile could be added later for an alternative one-click path, but it is not currently the bottleneck.
- **Two mis-served route families:** 50 legacy `/api/*` (working) + 49 broken `/api/v1/*/*` (doubled prefix, e.g. `/api/v1/auth/auth/login`). The frontend uses only the legacy routes, so this doesn't block the UI — but the v1 router registrations in `backend/main.py` produce 46 duplicate broken paths that should be de-duplicated.

## 6. Recommended Next Steps (untested risk areas)

1. Install `slowapi`/`limits` and add a login rate-limit (security gap above).
2. Fix simulator re-scan (#4) and corrupt-image 400 (#10).
3. Restore/repair the v1 router prefix in `backend/main.py`.
4. Move `SECRET_KEY` to environment; add input sanitization for stored strings.
5. Add a `Dockerfile` + `docker-compose.yml` as an alternative to `start.bat` for the "one-click" promise.

> ⚠️ **Note on my testing:** this session uses System Python 3.12 directly (the venv has only ~15 pkgs). For a reproducible end-user install, the venv route in `start.bat` is the correct path — but it must fully install `backend/requirements.txt`.
