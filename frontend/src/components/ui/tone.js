/** Map backend risk / severity strings to Badge & chart tones. */

export function normalizeRiskLevel(level) {
  return String(level ?? "").replace(/[^A-Za-z]/g, "").toUpperCase();
}

export function riskTone(level) {
  const l = normalizeRiskLevel(level);
  if (l === "HIGH" || l === "CRITICAL") return "danger";
  if (l === "MEDIUM") return "warning";
  if (l === "LOW") return "success";
  return "neutral";
}

export function riskColor(level) {
  const l = normalizeRiskLevel(level);
  if (l === "HIGH" || l === "CRITICAL") return "#dc2626";
  if (l === "MEDIUM") return "#d97706";
  if (l === "LOW") return "#059669";
  return "#64748b";
}

export function severityTone(severity) {
  const s = normalizeRiskLevel(severity);
  if (s === "CRITICAL") return "danger";
  if (s === "HIGH") return "warning";
  if (s === "MEDIUM") return "info";
  return "success";
}
