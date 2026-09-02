/** Static SVG globe used when WebGL is unavailable. */
export default function GlobeFallback({ className }) {
  return (
    <svg
      viewBox="0 0 200 200"
      className={className}
      role="img"
      aria-label="Ocean globe — 3D preview unavailable"
    >
      <circle cx="100" cy="100" r="80" fill="#0e7490" opacity="0.12" />
      <circle
        cx="100"
        cy="100"
        r="80"
        fill="none"
        stroke="#0d9488"
        strokeWidth="2"
      />
      <ellipse
        cx="100"
        cy="100"
        rx="80"
        ry="30"
        fill="none"
        stroke="#5eead4"
        strokeWidth="1"
        opacity="0.4"
      />
      <ellipse
        cx="100"
        cy="100"
        rx="30"
        ry="80"
        fill="none"
        stroke="#5eead4"
        strokeWidth="1"
        opacity="0.4"
      />
      <circle cx="100" cy="82" r="5" fill="#f87171" />
    </svg>
  );
}
