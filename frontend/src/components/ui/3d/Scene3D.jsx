import { useEffect, useRef, useState } from "react";
import { Canvas } from "@react-three/fiber";
import { prefersReducedMotion } from "./WebGLDetect";

/**
 * Shared R3F canvas wrapper.
 * Lightweight by default: capped DPR, no shadows, paused when off-screen
 * or when the user prefers reduced motion.
 */
export default function Scene3D({ children, className, style }) {
  const ref = useRef(null);
  const [visible, setVisible] = useState(true);
  const [motion] = useState(() => !prefersReducedMotion());

  useEffect(() => {
    if (!motion || typeof IntersectionObserver === "undefined") return;

    const el = ref.current;
    if (!el) return;
    const io = new IntersectionObserver(([entry]) =>
      setVisible(entry.isIntersecting),
    );
    io.observe(el);
    return () => io.disconnect();
  }, [motion]);

  const frameloop = motion && visible ? "always" : "never";

  return (
    <div ref={ref} className={className} style={style} aria-hidden="true">
      <Canvas
        frameloop={frameloop}
        dpr={[1, 1.5]}
        gl={{ antialias: true, alpha: true }}
        camera={{ position: [0, 0, 4], fov: 45 }}
      >
        {children}
      </Canvas>
    </div>
  );
}
