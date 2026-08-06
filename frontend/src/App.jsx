import { BrowserRouter, Routes, Route } from "react-router-dom";

import Layout from "./components/layout/Layout";
import Dashboard from "./pages/Dashboard";
import MarineMap from "./pages/MarineMap";
import LiveMonitoring from "./pages/LiveMonitoring";
import ImageDetection from "./pages/ImageDetection";
import Reports from "./pages/Reports";
import SystemPage from "./pages/SystemPage";
import Config from "./pages/Config";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="live-monitoring" element={<LiveMonitoring />} />
          <Route path="marine-map" element={<MarineMap />} />
          <Route path="image-detection" element={<ImageDetection />} />
          <Route path="reports" element={<Reports />} />
          <Route path="system" element={<SystemPage />} />
          <Route path="config" element={<Config />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
