import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import Scene3D from "./Scene3D";
import WavesFallback from "./WavesFallback";
import { supportsWebGL } from "./WebGLDetect";

function WavePlane() {
  const ref = useRef(null);
  useFrame((state) => {
    const mesh = ref.current;
    if (!mesh) return;
    const pos = mesh.geometry.attributes.position;
    const t = state.clock.elapsedTime;
    for (let i = 0; i < pos.count; i++) {
      const x = pos.getX(i);
      const y = pos.getY(i);
      pos.setZ(
        i,
        Math.sin(x * 2 + t * 1.5) * 0.15 + Math.cos(y * 2 + t * 1.2) * 0.12,
      );
    }
    pos.needsUpdate = true;
  });

  return (
    <mesh
      ref={ref}
      rotation={[-Math.PI / 2, 0, 0]}
      position={[0, -0.2, 0]}
    >
      <planeGeometry args={[5, 3, 40, 24]} />
      <meshStandardMaterial
        color="#14b8a6"
        roughness={0.4}
        metalness={0.1}
        wireframe
        transparent
        opacity={0.85}
      />
    </mesh>
  );
}

/**
 * Small animated 3D wave surface. Lazy-load this component. Falls back to
 * an SVG band when WebGL is unavailable.
 */
export default function OceanWaves({ className, height = 140 }) {
  const webgl = supportsWebGL();
  if (!webgl) {
    return <WavesFallback className={className} />;
  }
  return (
    <Scene3D className={className} style={{ width: "100%", height }}>
      <ambientLight intensity={0.6} />
      <directionalLight position={[0, 3, 4]} intensity={1} />
      <WavePlane />
    </Scene3D>
  );
}
