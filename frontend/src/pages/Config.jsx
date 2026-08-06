import { useEffect, useRef, useState } from "react";
import api from "../services/api";
import PageHeader from "../components/ui/PageHeader";
import Button from "../components/ui/Button";
import Badge from "../components/ui/Badge";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from "../components/ui/Card";
import { IconUpload } from "../components/ui/icons";

const DATASETS = [
  {
    key: "ais",
    label: "AIS Vessel Data",
    desc: "CSV with columns: MMSI, BaseDateTime, LAT, LON, SOG, COG, Heading, VesselName …",
    accept: ".csv",
  },
  {
    key: "satellite",
    label: "Satellite Images",
    desc: "PNG / JPEG / TIFF files for the oil spill detection model.",
    accept: ".png,.jpg,.jpeg,.tif,.tiff",
  },
  {
    key: "coastlines",
    label: "Coastlines",
    desc: "CSV with columns: Name, Latitude, Longitude",
    accept: ".csv",
  },
  {
    key: "protected_areas",
    label: "Marine Protected Areas",
    desc: "CSV with columns: Name, Latitude, Longitude",
    accept: ".csv",
  },
  {
    key: "mangroves",
    label: "Mangroves",
    desc: "CSV with columns: Name, Latitude, Longitude",
    accept: ".csv",
  },
  {
    key: "coral_reefs",
    label: "Coral Reefs",
    desc: "CSV with columns: Name, Latitude, Longitude",
    accept: ".csv",
  },
  {
    key: "fishing_zones",
    label: "Fishing Zones",
    desc: "CSV with columns: Name, Latitude, Longitude",
    accept: ".csv",
  },
  {
    key: "ports",
    label: "Ports",
    desc: "CSV with columns: Name, Latitude, Longitude",
    accept: ".csv",
  },
];

const PRESETS = [
  { label: "Chennai", lat: 13.08, lon: 80.27 },
  { label: "Gulf of Mannar", lat: 8.76, lon: 78.13 },
  { label: "Nagapattinam", lat: 10.77, lon: 79.84 },
  { label: "Rameswaram", lat: 9.29, lon: 79.31 },
];

function UploadCard({ dataset, datasets }) {
  const info = datasets[dataset.key] ?? {};
  const fileRef = useRef(null);
  const [uploading, setUploading] = useState(false);
  const [msg, setMsg] = useState(null);

  const upload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true);
    setMsg(null);
    const fd = new FormData();
    fd.append("file", file);
    try {
      const res = await api.post(`/config/upload/${dataset.key}`, fd, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setMsg({
        ok: true,
        text: `Uploaded ${res.data.filename} (${res.data.size_mb} MB)`,
      });
    } catch (err) {
      setMsg({
        ok: false,
        text: err.response?.data?.detail ?? "Upload failed",
      });
    }
    setUploading(false);
    if (fileRef.current) fileRef.current.value = "";
  };

  return (
    <div className="rounded-lg border border-border p-4">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="text-sm font-semibold">{dataset.label}</div>
          <div className="mt-0.5 text-xs text-muted">{dataset.desc}</div>
        </div>
        <Badge variant={info.available ? "success" : "outline"}>
          {info.available
            ? `${info.files} file${info.files === 1 ? "" : "s"} · ${info.size_mb} MB`
            : "Not uploaded"}
        </Badge>
      </div>

      {info.filenames?.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1">
          {info.filenames.map((n) => (
            <span
              key={n}
              className="rounded bg-slate-100 px-2 py-0.5 text-xs text-muted"
            >
              {n}
            </span>
          ))}
          {info.files > 5 && (
            <span className="text-xs text-muted">
              +{info.files - 5} more
            </span>
          )}
        </div>
      )}

      <div className="mt-3">
        <input
          ref={fileRef}
          type="file"
          accept={dataset.accept}
          onChange={upload}
          className="hidden"
          aria-label={`Upload ${dataset.label}`}
        />
        <Button
          variant="outline"
          size="sm"
          onClick={() => fileRef.current?.click()}
          loading={uploading}
          icon={<IconUpload />}
        >
          {info.available ? "Replace" : "Upload"}
        </Button>
      </div>

      {msg && (
        <div
          className={`mt-2 text-xs ${msg.ok ? "text-emerald-600" : "text-red-600"}`}
        >
          {msg.text}
        </div>
      )}
    </div>
  );
}

function Field({ label, children, mono }) {
  return (
    <div>
      <label className="mb-1 block text-xs font-medium uppercase tracking-wide text-muted">
        {label}
      </label>
      {children}
    </div>
  );
}

export default function Config() {
  const [config, setConfig] = useState(null);
  const [datasets, setDatasets] = useState({});
  const [saving, setSaving] = useState(false);
  const [saveMsg, setSaveMsg] = useState(null);
  const [testResults, setTestResults] = useState({});
  const [testing, setTesting] = useState(false);

  useEffect(() => {
    api.get("/config").then((r) => setConfig(r.data));
    api.get("/config/datasets").then((r) => setDatasets(r.data));
  }, []);

  const update = (key, value) =>
    setConfig((prev) => ({ ...prev, [key]: value }));

  const save = async () => {
    setSaving(true);
    setSaveMsg(null);
    try {
      await api.put("/config", config);
      setSaveMsg({ ok: true, text: "Settings saved" });
    } catch {
      setSaveMsg({ ok: false, text: "Failed to save" });
    }
    setSaving(false);
  };

  const runTest = async () => {
    setTesting(true);
    setTestResults({});
    try {
      const res = await api.post("/config/test", {
        feed_source: config.feed_source,
        ais_source: config.ais_source,
        ais_bbox_span: config.ais_bbox_span,
        incident_latitude: config.incident_latitude,
        incident_longitude: config.incident_longitude,
      });
      setTestResults(res.data);
    } catch {
      setTestResults({ error: "Failed to run test" });
    }
    setTesting(false);
  };

  if (!config) {
    return (
      <div className="space-y-6 p-6">
        <div className="h-12 w-64 animate-pulse rounded bg-slate-100" />
        <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
          <div className="h-64 animate-pulse rounded bg-slate-50" />
          <div className="h-64 animate-pulse rounded bg-slate-50" />
        </div>
      </div>
    );
  }

  const inputClass =
    "w-full rounded-lg border border-border bg-white px-3 py-2 text-sm tabular-nums";

  return (
    <div>
      <PageHeader
        title="Configuration"
        description="Set incident coordinates, model thresholds, and upload the datasets the system uses"
      />

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
        {/* ── Model Settings ────────────────────────── */}
        <Card>
          <CardHeader>
            <CardTitle>Model Settings</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* Coordinates */}
              <div className="grid grid-cols-2 gap-4">
                <Field label="Incident Latitude">
                  <input
                    type="number"
                    step="any"
                    value={config.incident_latitude}
                    onChange={(e) =>
                      update("incident_latitude", parseFloat(e.target.value) || 0)
                    }
                    className={inputClass}
                  />
                </Field>
                <Field label="Incident Longitude">
                  <input
                    type="number"
                    step="any"
                    value={config.incident_longitude}
                    onChange={(e) =>
                      update("incident_longitude", parseFloat(e.target.value) || 0)
                    }
                    className={inputClass}
                  />
                </Field>
              </div>

              {/* Tamil Nadu coastal presets */}
              <div>
                <div className="mb-1 text-xs font-medium uppercase tracking-wide text-muted">
                  Quick Presets
                </div>
                <div className="flex flex-wrap gap-2">
                  {PRESETS.map((p) => (
                    <button
                      key={p.label}
                      type="button"
                      onClick={() => {
                        update("incident_latitude", p.lat);
                        update("incident_longitude", p.lon);
                      }}
                      className="rounded-lg border border-border bg-slate-50 px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-100 transition-colors"
                    >
                      {p.label} <span className="text-muted ml-1">{p.lat}, {p.lon}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Threshold / Interval */}
              <div className="grid grid-cols-2 gap-4">
                <Field label="Detection Threshold (%)">
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    max="100"
                    value={config.detection_threshold}
                    onChange={(e) =>
                      update("detection_threshold", parseFloat(e.target.value) || 1)
                    }
                    className={inputClass}
                  />
                </Field>
                <Field label="Monitoring Interval (s)">
                  <input
                    type="number"
                    min="5"
                    max="300"
                    value={config.monitor_interval_seconds}
                    onChange={(e) =>
                      update("monitor_interval_seconds", parseInt(e.target.value) || 30)
                    }
                    className={inputClass}
                  />
                </Field>
              </div>

              {/* AIS CSV path */}
              <Field label="AIS CSV Path (relative to repo root)">
                <input
                  type="text"
                  value={config.ais_csv_path}
                  onChange={(e) => update("ais_csv_path", e.target.value)}
                  className={`${inputClass} font-mono`}
                />
              </Field>

              {/* Save */}
              <div className="flex items-center gap-3 pt-2">
                <Button onClick={save} loading={saving}>
                  Save Settings
                </Button>
                {saveMsg && (
                  <span
                    className={`text-xs ${saveMsg.ok ? "text-emerald-600" : "text-red-600"}`}
                  >
                    {saveMsg.text}
                  </span>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* ── Satellite Feed ──────────────────────── */}
        <Card>
          <CardHeader>
            <CardTitle>Satellite Feed</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <Field label="Feed Source">
                <select
                  value={config.feed_source}
                  onChange={(e) => update("feed_source", e.target.value)}
                  className={inputClass}
                >
                  <option value="simulator">Simulator (sample images)</option>
                  <option value="sentinel_hub">Sentinel Hub / Copernicus Data Space (live satellite)</option>
                </select>
              </Field>

              {config.feed_source === "sentinel_hub" && (
                <>
                  <Field label="Copernicus Username">
                    <input
                      type="text"
                      value={config.copernicus_username}
                      onChange={(e) => update("copernicus_username", e.target.value)}
                      className={inputClass}
                      placeholder="your.email@example.com"
                    />
                  </Field>

                  <Field label="Copernicus Password">
                    <input
                      type="password"
                      value={config.copernicus_password}
                      onChange={(e) => update("copernicus_password", e.target.value)}
                      className={inputClass}
                      placeholder="••••••••"
                    />
                  </Field>

                  <div className="text-xs text-muted">
                    Or set via env: COPERNICUS_CLIENT_ID / COPERNICUS_CLIENT_SECRET
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <Field label="Satellite Layer">
                      <select
                        value={config.satellite_layer}
                        onChange={(e) => update("satellite_layer", e.target.value)}
                        className={inputClass}
                      >
                        <option value="TRUE_COLOR">True Color (Sentinel-2)</option>
                        <option value="SAR">SAR (Sentinel-1)</option>
                      </select>
                    </Field>
                    <Field label="Frame Cache TTL (s)">
                      <input
                        type="number"
                        min="60"
                        max="3600"
                        value={config.frame_cache_ttl_seconds}
                        onChange={(e) =>
                          update("frame_cache_ttl_seconds", parseInt(e.target.value) || 600)
                        }
                        className={inputClass}
                      />
                    </Field>
                  </div>
                </>
              )}

              {/* Status badge */}
              <div className="flex items-center gap-2">
                <span className="text-xs text-muted">Test connection:</span>
                <Button variant="outline" size="sm" onClick={runTest} loading={testing}>
                  Test
                </Button>
                {testResults.satellite && (
                  <Badge
                    variant={
                      testResults.satellite.status === "success"
                        ? "success"
                        : testResults.satellite.status === "error"
                          ? "destructive"
                          : "outline"
                    }
                  >
                    {testResults.satellite.status === "success" ? "Connected" :
                     testResults.satellite.status === "error" ? "Failed" : "Skipped"}
                  </Badge>
                )}
              </div>
              {testResults.satellite?.message && (
                <div className="text-xs text-muted">{testResults.satellite.message}</div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* ── AIS Feed ──────────────────────── */}
        <Card>
          <CardHeader>
            <CardTitle>AIS Feed</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <Field label="AIS Source">
                <select
                  value={config.ais_source}
                  onChange={(e) => update("ais_source", e.target.value)}
                  className={inputClass}
                >
                  <option value="csv">Uploaded CSV (local file)</option>
                  <option value="simulated_live">Simulated Live (animate CSV)</option>
                  <option value="marinetraffic">MarineTraffic API (live)</option>
                  <option value="aishub">AISHub (free, live)</option>
                </select>
              </Field>

              {config.ais_source === "marinetraffic" && (
                <>
                  <Field label="MarineTraffic API Key">
                    <input
                      type="password"
                      value={config.marine_traffic_api_key}
                      onChange={(e) => update("marine_traffic_api_key", e.target.value)}
                      className={inputClass}
                      placeholder="Your MarineTraffic / Kpler API key"
                    />
                  </Field>
                </>
              )}

              {config.ais_source === "aishub" && (
                <>
                  <div className="grid grid-cols-2 gap-4">
                    <Field label="AISHub Username">
                      <input
                        type="text"
                        value={config.aishub_username}
                        onChange={(e) => update("aishub_username", e.target.value)}
                        className={inputClass}
                      />
                    </Field>
                    <Field label="AISHub API Key">
                      <input
                        type="password"
                        value={config.aishub_api_key}
                        onChange={(e) => update("aishub_api_key", e.target.value)}
                        className={inputClass}
                      />
                    </Field>
                  </div>
                  <div className="text-xs text-muted">
                    Free account at https://data.aishub.net — requires registering a station.
                  </div>
                </>
              )}

              <div className="grid grid-cols-2 gap-4">
                <Field label="AIS Bounding Box Span (deg)">
                  <input
                    type="number"
                    min="0.1"
                    max="20"
                    step="0.1"
                    value={config.ais_bbox_span}
                    onChange={(e) => update("ais_bbox_span", parseFloat(e.target.value) || 2)}
                    className={inputClass}
                  />
                </Field>
                <Field label="Refresh Interval (s)">
                  <input
                    type="number"
                    min="30"
                    max="3600"
                    value={config.ais_refresh_interval_seconds}
                    onChange={(e) =>
                      update("ais_refresh_interval_seconds", parseInt(e.target.value) || 300)
                    }
                    className={inputClass}
                  />
                </Field>
              </div>

              {/* Status badge */}
              <div className="flex items-center gap-2">
                <span className="text-xs text-muted">Test connection:</span>
                <Button variant="outline" size="sm" onClick={runTest} loading={testing}>
                  Test
                </Button>
                {testResults.ais && (
                  <Badge
                    variant={
                      testResults.ais.status === "success"
                        ? "success"
                        : testResults.ais.status === "error"
                          ? "destructive"
                          : "outline"
                    }
                  >
                    {testResults.ais.status === "success" ? "Connected" :
                     testResults.ais.status === "error" ? "Failed" : "Skipped"}
                  </Badge>
                )}
              </div>
              {testResults.ais?.message && (
                <div className="text-xs text-muted">{testResults.ais.message}</div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* ── Dataset uploads ──────────────────────── */}
        <Card>
          <CardHeader>
            <CardTitle>Dataset Uploads</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {DATASETS.map((ds) => (
              <UploadCard key={ds.key} dataset={ds} datasets={datasets} />
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
