/** Map backend risk / severity strings to Badge & chart tones. */

export function riskTone(level) {
  const l = String(level ?? "").toUpperCase();
  if (l === "HIGH" || l === "CRITICAL") return "danger";
  if (l === "MEDIUM") return "warning";
  if (l === "LOW") return "success";
  return "neutral";
}

export function riskColor(level) {
  const l = String(level ?? "").toUpperCase();
  if (l === "HIGH" || l === "CRITICAL") return "#dc2626";
  if (l === "MEDIUM") return "#d97706";
  if (l === "LOW") return "#059669";
  return "#64748b";
}

export function severityTone(severity) {
  const s = String(severity ?? "").toUpperCase();
  if (s === "CRITICAL") return "danger";
  if (s === "HIGH") return "warning";
  if (s === "MEDIUM") return "info";
  return "success";
}
