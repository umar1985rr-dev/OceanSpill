import {
  IconDashboard,
  IconRadio,
  IconMap,
  IconImage,
  IconFileText,
  IconActivity,
  IconLayers,
} from "../ui/icons";

export const NAV_ITEMS = [
  { to: "/", label: "Command Dashboard", icon: IconDashboard, end: true },
  { to: "/live-monitoring", label: "Live Monitoring", icon: IconRadio },
  { to: "/marine-map", label: "Marine Map", icon: IconMap },
  { to: "/image-detection", label: "Image Detection", icon: IconImage },
  { to: "/reports", label: "Reports", icon: IconFileText },
  { to: "/system", label: "System Health", icon: IconActivity },
  { to: "/config", label: "Configuration", icon: IconLayers },
];
