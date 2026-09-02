import { useRef, useState } from "react";
import { cn } from "../../../lib/cn";
import { prefersReducedMotion } from "./WebGLDetect";

/**
 * CSS-3D pointer-tilt wrapper (zero-dependency).
 * Tilts the card in 3D toward the cursor; respects reduced motion.
 */
export default function Tilt({
  children,
  className,
  max = 6,
  scale = 1.02,
}) {
  const ref = useRef(null);
  const [transform, setTransform] = useState("");

  if (prefersReducedMotion()) {
    return (
      <div className={cn("[transform-style:preserve-3d]", className)}>
        {children}
      </div>
    );
  }

  const handleMove = (e) => {
    const el = ref.current;
    if (!el) return;
    const rect = el.getBoundingClientRect();
    const px = (e.clientX - rect.left) / rect.width;
    const py = (e.clientY - rect.top) / rect.height;
    const rx = (0.5 - py) * max;
    const ry = (px - 0.5) * max;
    setTransform(
      `perspective(800px) rotateX(${rx}deg) rotateY(${ry}deg) scale(${scale})`,
    );
  };

  const reset = () =>
    setTransform("perspective(800px) rotateX(0deg) rotateY(0deg)");

  return (
    <div
      ref={ref}
      className={cn(
        "[transform-style:preserve-3d] will-change-transform transition-transform duration-300 ease-out",
        className,
      )}
      style={{ transform }}
      onMouseMove={handleMove}
      onMouseLeave={reset}
    >
      {children}
    </div>
  );
}
