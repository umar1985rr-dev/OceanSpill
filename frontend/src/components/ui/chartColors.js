/**
 * Categorical chart palette — one system for every chart.
 * Validated with the dataviz palette validator (CVD-safe, normal-vision
 * floor ΔE 22.6). Teal/cyan pair was rejected (ΔE 6.9 — too close).
 */
export const CHART_COLORS = [
  "#0d9488", // teal-600
  "#2563eb", // blue-600
  "#d97706", // amber-600
  "#7c3aed", // violet-600
];

export const chartByIdx = (i) => CHART_COLORS[i % CHART_COLORS.length];

/** Status colors for the risk meter (reserved, not categorical). */
export const riskBandColor = (score) =>
  score >= 75 ? "#dc2626" : score >= 40 ? "#d97706" : "#059669";
