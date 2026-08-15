import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { Float } from "@react-three/drei";
import Scene3D from "./Scene3D";
import GlobeFallback from "./GlobeFallback";
import { supportsWebGL } from "./WebGLDetect";

function latLonToVec3(lat, lon, radius) {
  const phi = (90 - lat) * (Math.PI / 180);
  const theta = (lon + 180) * (Math.PI / 180);
  return [
    -radius * Math.sin(phi) * Math.cos(theta),
    radius * Math.cos(phi),
    radius * Math.sin(phi) * Math.sin(theta),
  ];
}

function SpillMarker({ lat, lon }) {
  const position = latLonToVec3(lat, lon, 1.06);
  return (
    <mesh position={position}>
      <sphereGeometry args={[0.055, 12, 12]} />
      <meshBasicMaterial color="#f87171" />
    </mesh>
  );
}

function GlobeBody({ marker }) {
  const ref = useRef(null);
  useFrame((_, delta) => {
    if (ref.current) ref.current.rotation.y += delta * 0.12;
  });

  return (
    <group ref={ref}>
      <mesh>
        <sphereGeometry args={[1, 32, 32]} />
        <meshStandardMaterial color="#0e7490" roughness={0.35} metalness={0.2} />
      </mesh>
      {/* graticule wireframe overlay */}
      <mesh>
        <sphereGeometry args={[1.002, 24, 16]} />
        <meshBasicMaterial color="#5eead4" wireframe transparent opacity={0.22} />
      </mesh>
      {marker && <SpillMarker lat={marker.lat} lon={marker.lon} />}
    </group>
  );
}

/**
 * Lightweight 3D ocean globe. Lazy-load this component so the three.js
 * bundle stays off the critical path. Falls back to SVG without WebGL.
 */
export default function OceanGlobe({
  lat = 29.78,
  lon = -90.1,
  className,
  size = 220,
}) {
  const webgl = supportsWebGL();
  if (!webgl) {
    return <GlobeFallback className={className} />;
  }
  return (
    <Scene3D className={className} style={{ width: size, height: size }}>
      <ambientLight intensity={0.7} />
      <directionalLight position={[3, 2, 4]} intensity={1.1} />
      <Float speed={1.2} rotationIntensity={0.15} floatIntensity={0.4}>
        <GlobeBody marker={{ lat, lon }} />
      </Float>
    </Scene3D>
  );
}
