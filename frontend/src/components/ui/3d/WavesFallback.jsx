/** Static SVG wave bands used when WebGL is unavailable. */
export default function WavesFallback({ className }) {
  return (
    <svg
      viewBox="0 0 200 60"
      preserveAspectRatio="none"
      className={className}
      aria-hidden="true"
    >
      <path
        d="M0 30c15-8 30-8 45 0s30 8 45 0 30-8 45 0 30 8 45 0"
        fill="none"
        stroke="#14b8a6"
        strokeWidth="2"
      />
      <path
        d="M0 45c15-8 30-8 45 0s30 8 45 0 30-8 45 0 30 8 45 0"
        fill="none"
        stroke="#0d9488"
        strokeWidth="2"
        opacity="0.5"
      />
    </svg>
  );
}
