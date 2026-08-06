import { useRef, useState } from "react";
import api from "../services/api";
import { API_URL } from "../config";
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
    window.open(`${API_URL}/report/generate`, "_blank");
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
                    <Field label="Risk Level" value={result.risk_level} />
                  </FieldGrid>

                  <Button
                    variant="outline"
                    size="sm"
                    className="mt-4"
                    onClick={downloadReport}
                    icon={<IconDownload />}
                  >
                    Download Incident Report
                  </Button>
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
