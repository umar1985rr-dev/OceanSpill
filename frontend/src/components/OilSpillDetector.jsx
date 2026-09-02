import { useRef, useState } from "react";
import { useCallback } from "react";
import api from "../services/api";
import { API_BASE, API_URL, POLL_INTERVAL } from "../config";
import { riskTone } from "./ui/tone";
import { usePolling } from "../hooks/usePolling";
import Button from "./ui/Button";
import Badge from "./ui/Badge";
import { Card, CardHeader, CardTitle, CardContent } from "./ui/Card";
import EmptyState from "./ui/EmptyState";
import ErrorState from "./ui/ErrorState";
import { Field, FieldGrid } from "./ui/Field";
import { IconUpload, IconImage, IconDownload } from "./ui/icons";

function OilSpillDetector() {
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const inputRef = useRef(null);

  // The model writes original / mask / overlay images into <api>/outputs/*
  // (relative paths returned by the prediction endpoint). Resolve them to
  // absolute URLs here.
  const imageUrl = (path) => {
    if (!path) return null;
    // The backend returns Windows-native paths (outputs\original.png) —
    // normalize to forward slashes so every browser loads them.
    const normalized = path.replace(/\\/g, "/");
    return normalized.startsWith("/")
      ? `${API_URL}${normalized}`
      : `${API_URL}/${normalized}`;
  };

  // Poll monitoring status to know if there's a real latest incident
  const statusFetcher = useCallback(
    () => api.get("/monitoring/status").then((r) => r.data),
    [],
  );
  const { data: status } = usePolling(statusFetcher, POLL_INTERVAL);
  const hasLatestIncident = status?.last_detection != null;

  const handleChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setImage(file);
    setPreview(URL.createObjectURL(file));
    setError("");
    setResult(null);
  };

  const analyze = async () => {
    if (!image) {
      setError("Please upload an image first.");
      return;
    }
    const formData = new FormData();
    formData.append("file", image);
    setLoading(true);
    setError("");
    try {
      const response = await api.post("/detection/predict", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setResult(response.data);
    } catch {
      setError("Prediction failed. Check that the backend service is running.");
    }
    setLoading(false);
  };

  const downloadReport = () => {
    window.open(`${API_BASE}/report/generate`, "_blank");
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Analyze a Satellite Image</CardTitle>
      </CardHeader>
      <CardContent className="space-y-5">
        <input
          ref={inputRef}
          type="file"
          accept="image/*"
          onChange={handleChange}
          className="hidden"
          aria-label="Upload satellite image"
        />

        <button
          type="button"
          onClick={() => inputRef.current?.click()}
          className="flex w-full flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed border-slate-300 p-8 text-center transition-colors hover:border-primary hover:bg-slate-50"
        >
          <IconUpload className="text-muted" />
          <span className="text-sm font-medium">Choose a satellite image</span>
          <span className="text-xs text-muted">
            PNG or JPEG · oil spill segmentation via U-Net
          </span>
        </button>

        {error && <ErrorState message={error} />}

        {!preview && (
          <EmptyState
            title="Upload an image to begin"
            description="The model segments oil-affected pixels and estimates spill area, confidence and risk."
            icon={<IconImage />}
          />
        )}

        {preview && (
          <div className="flex flex-col gap-4 sm:flex-row sm:items-start">
            <img
              src={preview}
              alt="Uploaded satellite image preview"
              className="w-full max-w-[280px] rounded-lg border border-border"
            />

            <div className="flex-1 space-y-4">
              <Button onClick={analyze} loading={loading} icon={<IconImage />}>
                Analyze Image
              </Button>

              {result && (
                <div className="rounded-lg bg-slate-50 p-4">
                  <div className="mb-3 flex items-center justify-between">
                    <div className="text-sm font-semibold">
                      Prediction Result
                    </div>
                    <Badge
                      variant={result.oil_detected ? "danger" : "success"}
                    >
                      {result.oil_detected ? "OIL DETECTED" : "NO OIL"}
                    </Badge>
                  </div>

                  <FieldGrid>
                    <Field
                      label="Confidence"
                      value={`${result.confidence}%`}
                      mono
                    />
                    <Field
                      label="Spill Area"
                      value={`${result.spill_area_km2} km²`}
                      mono
                    />
                    <Field label="Risk Score" value={result.risk_score} mono />
                    <Field
                      label="Risk Level"
                      value={
                        <Badge variant={riskTone(result.risk_level)}>
                          {result.risk_level}
                        </Badge>
                      }
                    />
                  </FieldGrid>

                  {/* Segmentation previews — original / mask / overlay */}
                  {result.images &&
                    (result.images.original ||
                      result.images.mask ||
                      result.images.overlay) && (
                      <div className="mt-4">
                        <div className="mb-2 text-xs font-medium uppercase tracking-wide text-muted">
                          Segmentation Output
                        </div>
                        <div className="grid grid-cols-3 gap-2">
                          {[
                            { key: "original", label: "Original" },
                            { key: "mask", label: "Mask" },
                            { key: "overlay", label: "Overlay" },
                          ]
                            .filter(({ key }) => result.images[key])
                            .map(({ key, label }) => (
                              <figure key={key}>
                                <img
                                  src={imageUrl(result.images[key])}
                                  alt={`${label} segmentation preview`}
                                  className="aspect-square w-full rounded-lg border border-border object-cover"
                                  loading="lazy"
                                />
                                <figcaption className="mt-1 text-center text-xs text-muted">
                                  {label}
                                </figcaption>
                              </figure>
                            ))}
                        </div>
                      </div>
                    )}

                  {hasLatestIncident && (
                    <Button
                      variant="outline"
                      size="sm"
                      className="mt-4"
                      onClick={downloadReport}
                      icon={<IconDownload />}
                    >
                      Download Latest Incident Report
                    </Button>
                  )}
                </div>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export default OilSpillDetector;
