import asyncio
import logging
import math
import threading
import uuid

from datetime import datetime

from backend.config import settings

from backend.services.satellite_feed import create_feed

from backend.services.monitoring.state import MonitoringState

from backend.services.oil_detector.detect import detect_oil_spill

from backend.services.oil_detector.postprocess import postprocess_prediction

from backend.services.oil_detector.overlay import generate_overlay

from backend.services.alerts.service import AlertService

from backend.services.report_generator import ReportGenerator

from backend.services.report_generator.models import IncidentReport

from backend.services.drift_prediction.predictor import DriftPredictor

from backend.services.drift_prediction.models import SpillData

from backend.services.drift_prediction.data_loader import (
    EnvironmentalDataLoader,
)

from backend.services.impact_analysis import (
    ImpactInput,
    RiskScoringEngine,
)

from backend.services.cleanup_recommender import (
    CleanupRecommendationEngine,
    CleanupInput,
)

from backend.services.database import IncidentService, AlertHistoryService
from backend.database import SessionLocal


def _load_ais_dataframe():
    """
    Load the AIS dataframe for the configured source (runtime config
    ``ais_source``: csv / marinetraffic / aishub).

    The provider layer handles caching, TTL refresh and thread-safety;
    this entry point is kept so the existing ``/ais/*`` call sites in
    ``backend/api/ais.py`` don't change.
    """

    from backend.services.ais_analysis.provider import get_ais_data

    return get_ais_data()


def _risk_level(spill_percentage):

    if spill_percentage < 3:

        return "LOW"

    if spill_percentage < 8:

        return "MEDIUM"

    return "HIGH"


def _direction(delta_lat, delta_lon):

    angle = math.degrees(
        math.atan2(delta_lon, delta_lat)
    )

    directions = [
        "N", "NE", "E", "SE", "S", "SW", "W", "NW",
    ]

    index = int(((angle + 360) % 360) / 45) % 8

    return directions[index]


class MonitoringService:
    """
    Polls the satellite feed every N seconds, runs U-Net
    detection on each frame and - when a spill is found - runs
    the full response pipeline and generates an incident report.
    """

    def __init__(self, state=None):

        self.state = state or MonitoringState()

        # Unique id per process instance. Clients use it to detect that the
        # backend was (re)started even if the persisted version is unchanged.
        self.instance_id = uuid.uuid4().hex

        self.feed = create_feed()

        self._feed_source = self.feed.status().get("source")

        self._last_frame_path = None

        self.interval = settings.monitor_interval_seconds

        self.threshold = settings.detection_threshold

        # Allow runtime config overrides (set via /config PUT)
        try:
            from backend.api.config_store import get_config as _rc
            _rc_data = _rc()
            self.interval = int(_rc_data.get("monitor_interval_seconds", self.interval))
            self.threshold = float(_rc_data.get("detection_threshold", self.threshold))
        except Exception:
            pass

        self.alert_service = AlertService(self.state)

        self.environment = EnvironmentalDataLoader()

        self._running = False

        self._task = None

        self.logger = logging.getLogger(__name__)

    # ----------------------------------------------------------
    # Control
    # ----------------------------------------------------------

    def start(self):
        """
        Start the monitoring loop.

        Must be called from within a running asyncio loop (the
        FastAPI lifespan or an async endpoint). Runs the loop in
        the main thread, which avoids torch/OpenCV thread
        deadlocks on Windows.
        """

        if self._running:

            return

        self._sync_feed()

        self.state.set_feed_status(self.feed.status())

        self._running = True

        loop = asyncio.get_running_loop()

        self._task = loop.create_task(self._loop())

        self.state.set_running(True)

        self.state.bump_version()

        self.logger.info(
            "Monitoring started: %s every %ss",
            self.feed.status().get("source"),
            self.interval,
        )

    def stop(self):

        self._running = False

        if self._task:

            self._task.cancel()

            self._task = None

        self.feed.disconnect()

        self.state.set_running(False)

        self.state.bump_version()

        self.logger.info("Monitoring stopped")

    async def _loop(self):

        while self._running:

            try:

                self._sync_feed()

                # tick() is synchronous — U-Net inference, weather API,
                # impact analysis, report generation, DB writes — and
                # can block for seconds. Run it in the default
                # threadpool so the event loop stays free to serve
                # HTTP requests. Without this, every endpoint freezes
                # during detection, causing "Backend offline" in the
                # browser.
                await asyncio.to_thread(self.tick)

            except Exception as exc:

                self.logger.exception(
                    "Monitoring loop error: %s",
                    exc,
                )

            await asyncio.sleep(self.interval)

    def _sync_feed(self):

        """
        Rebuild the feed when the desired feed_source changes.

        The feed source is set through the /config UI at runtime; the
        monitoring loop calls this each tick so a switch applies live,
        without restarting the backend.
        """

        try:

            from backend.api.config_store import get_config as _rc

            desired = _rc().get(
                "feed_source",
                settings.feed_source,
            )

        except Exception:

            desired = settings.feed_source

        if desired == self._feed_source:

            return

        old = self.feed

        try:

            new_feed = create_feed()

            new_feed.connect()

            self.feed = new_feed

            self._feed_source = desired

            self.state.set_feed_status(self.feed.status())

            self.logger.info("Feed switched to %s", desired)

            if old is not None and old is not new_feed:

                old.disconnect()

        except Exception as exc:

            self.logger.warning(
                "Feed switch to %s failed: %s",
                desired,
                exc,
            )

            # Keep the old feed running; monitoring must not die.
            if old is not None:

                self._feed_source = old.status().get("source")

    def tick(self):

        # Skip if a previous tick is still running
        if self.state.data["is_processing"]:

            return

        # Apply runtime config changes (interval / threshold) live,
        # so UI edits take effect without a backend restart.
        try:

            from backend.api.config_store import get_config as _rc

            _rc_data = _rc()

            self.interval = int(
                _rc_data.get(
                    "monitor_interval_seconds",
                    self.interval,
                )
            )

            self.threshold = float(
                _rc_data.get(
                    "detection_threshold",
                    self.threshold,
                )
            )

        except Exception:

            pass

        self.state.set_processing(True)

        try:

            frame = self.feed.get_frame()

            self.state.set_current_frame(
                self._frame_to_dict(frame)
            )

            self.state.set_last_checked(datetime.now())

            # Live feeds re-serve a cached tile during their download
            # TTL (same frame_id / path). Skip re-processing an
            # unchanged frame so we don't raise duplicate incidents.
            if (
                frame.source == "sentinel_hub"
                and frame.image_path == self._last_frame_path
            ):

                return

            self._last_frame_path = frame.image_path

            prediction = detect_oil_spill(frame.image_path)

            mask, spill_percentage = postprocess_prediction(prediction)

            generate_overlay(frame.image_path, mask)

            confidence = round(
                min(99.9, 92 + spill_percentage),
                2,
            )

            spill_area = round(
                spill_percentage * 0.75,
                2,
            )

            risk_score = min(
                100,
                int(spill_percentage * 8),
            )

            risk_level = _risk_level(spill_percentage)

            self.logger.info(
                "Frame %s: spill %.2f%%",
                frame.frame_id,
                spill_percentage,
            )

            if spill_percentage > self.threshold:

                incident = self._process_incident(
                    frame,
                    spill_percentage,
                    spill_area,
                    confidence,
                    risk_score,
                    risk_level,
                )

                self.state.add_incident(incident)

                self.state.set_last_detection(incident)

                self.alert_service.dispatch(incident)

                # Notify clients a new detection + report is available.
                self.state.bump_version()

                self.logger.warning(
                    "Oil spill detected on frame %s -> report %s",
                    frame.frame_id,
                    incident.get("report_path"),
                )

        except Exception as exc:

            self.logger.exception(
                "Monitoring tick failed: %s",
                exc,
            )

        finally:

            self.state.set_processing(False)

    # ----------------------------------------------------------
    # Detection pipeline
    # ----------------------------------------------------------

    def _process_incident(
        self,
        frame,
        spill_percentage,
        spill_area,
        confidence,
        risk_score,
        risk_level,
    ):

        timestamp = datetime.now()

        incident_id = (
            f"INC-{timestamp.strftime('%Y%m%d-%H%M%S')}"
            f"-F{frame.frame_id}"
        )

        # -----------------------------
        # Weather + current context
        # -----------------------------

        weather = {}

        current_speed = 0.0

        current_direction = 0.0

        try:

            weather = self.environment.load_live_weather(
                frame.latitude,
                frame.longitude,
            )

            current = self.environment.get_nearest_current(
                frame.latitude,
                frame.longitude,
            )

            current_speed = float(current["current_speed"])

            current_direction = float(current["current_direction"])

        except Exception as exc:

            self.logger.warning(
                "Weather/current unavailable: %s",
                exc,
            )

        # -----------------------------
        # Impact analysis
        # -----------------------------

        impact_input = ImpactInput(
            latitude=frame.latitude,
            longitude=frame.longitude,
            spill_area=spill_area,
            predicted_path=[],
            risk_zones=[],
            timestamp=timestamp,
        )

        impact = {}

        try:

            risk = RiskScoringEngine().calculate(impact_input)

            env_report = risk["Environmental Report"]

            eco_report = risk["Economic Report"]

            impact = {
                "risk_score": risk["Risk Score"],
                "risk_level": risk["Risk Level"],
                "environmental": env_report,
                "economic": eco_report,
            }

        except Exception as exc:

            self.logger.warning("Impact analysis failed: %s", exc)

            env_report = {}

            eco_report = {}

        # -----------------------------
        # Drift prediction
        # -----------------------------

        drift = []

        try:

            spill_data = SpillData(
                latitude=frame.latitude,
                longitude=frame.longitude,
                area=spill_area,
                timestamp=timestamp,
            )

            drift = DriftPredictor().predict(
                spill_data,
                hours=24,
            )

        except Exception as exc:

            self.logger.warning("Drift prediction failed: %s", exc)

        # -----------------------------
        # Cleanup recommendation
        # -----------------------------

        cleanup = {}

        try:

            distance_to_coast = env_report.get(
                "Nearest Coastline",
                {},
            ).get("distance", 10.0)

            cleanup = CleanupRecommendationEngine().recommend(
                CleanupInput(
                    spill_area=spill_area,
                    distance_to_coast=distance_to_coast,
                    risk_level=risk_level,
                    wind_speed=weather.get("wind_speed", 0),
                    current_speed=current_speed,
                )
            )

        except Exception as exc:

            self.logger.warning("Cleanup recommendation failed: %s", exc)

        # -----------------------------
        # AIS suspect ranking
        # -----------------------------

        suspect = None

        try:

            ranked = self._ais_ranking(
                frame.latitude,
                frame.longitude,
                timestamp,
            )

            if ranked is not None and not ranked.empty:

                suspect = ranked.iloc[0]

        except Exception as exc:

            self.logger.warning("AIS analysis failed: %s", exc)

        # -----------------------------
        # Incident record
        # -----------------------------

        incident = {
            "id": incident_id,
            "detected_at": timestamp.isoformat(),
            "frame_id": frame.frame_id,
            "image_path": frame.image_path,
            "latitude": frame.latitude,
            "longitude": frame.longitude,
            "spill_percentage": round(spill_percentage, 2),
            "spill_area_km2": spill_area,
            "confidence": confidence,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "weather": weather,
            "current_speed": current_speed,
            "current_direction": current_direction,
            "impact": impact,
            "drift": drift,
            "cleanup": cleanup,
            "suspect_vessel": self._suspect_summary(suspect),
            "report_path": None,
        }

        # -----------------------------
        # Incident report
        # -----------------------------

        try:

            report = IncidentReport(
                project_name=settings.app_name,
                project_goal=(
                    "Detect marine oil spills using AI-powered "
                    "satellite image analysis and provide rapid "
                    "environmental response support."
                ),
                project_objectives=[
                    "Detect oil spills using a trained U-Net segmentation model",
                    "Estimate spill extent and affected area",
                    "Predict spill drift using weather conditions",
                    "Assess environmental and economic impact",
                    "Identify the most probable AIS vessel responsible",
                    "Recommend cleanup strategies",
                    "Automatically generate incident reports",
                ],
                spill_location=(
                    f"{frame.latitude}, {frame.longitude}"
                ),
                detection_time=timestamp.isoformat(),
                spill_detected=True,
                confidence=confidence,
                spill_area=spill_area,
                risk_score=risk_score,
                risk_level=risk_level,
                weather={
                    "Wind Speed": (
                        f"{weather.get('wind_speed', 'N/A')} km/h"
                    ),
                    "Wind Direction": (
                        f"{weather.get('wind_direction', 'N/A')} deg"
                    ),
                    "Current Speed": (
                        f"{current_speed} m/s"
                    ),
                    "Current Direction": (
                        f"{current_direction} deg"
                    ),
                },
                drift_prediction=self._drift_summary(drift),
                environmental_summary=self._env_summary(env_report),
                economic_summary=self._eco_summary(eco_report),
                suspected_vessel=self._suspect_summary(suspect),
                recommendations=(
                    cleanup.get("Recommendations", [])
                ),
            )

            output_file = ReportGenerator().generate(report)

            incident["report_path"] = str(output_file)

        except Exception as exc:

            self.logger.warning("Report generation failed: %s", exc)

        # Persist incident to database
        try:
            db = SessionLocal()
            incident_service = IncidentService(db)
            incident_service.create(incident)
            # Also log alert history
            if incident.get("report_path"):
                alert_service = AlertHistoryService(db)
                alert_service.create(
                    incident_id=incident_service.get_by_incident_id(incident["id"]).id,
                    alert_type="dashboard",
                    status="sent",
                    message={"incident_id": incident["id"]}
                )
            db.close()
        except Exception as exc:
            self.logger.warning("Database persistence failed: %s", exc)

        return incident

    # ----------------------------------------------------------
    # Helpers
    # ----------------------------------------------------------

    def _frame_to_dict(self, frame):

        return {
            "frame_id": frame.frame_id,
            "image_path": frame.image_path,
            "latitude": frame.latitude,
            "longitude": frame.longitude,
            "timestamp": frame.timestamp.isoformat(),
            "source": frame.source,
        }

    def _ais_ranking(self, latitude, longitude, timestamp):

        from backend.services.ais_analysis.models import SpillLocation

        from backend.services.ais_analysis.nearby import NearbyVesselFinder

        from backend.services.ais_analysis.movement import MovementAnalyzer

        from backend.services.ais_analysis.ranking import SuspectRanker

        dataframe = _load_ais_dataframe()

        spill = SpillLocation(
            latitude=latitude,
            longitude=longitude,
            timestamp=timestamp,
        )

        nearby = NearbyVesselFinder().find_nearby(
            dataframe,
            spill,
            radius_km=20,
        )

        if nearby.empty:

            return None

        analyzed = MovementAnalyzer().analyze(nearby)

        ranked = SuspectRanker().rank(analyzed)

        return ranked

    def _drift_summary(self, drift):

        if not drift:

            return {

                "Direction": "N/A",

                "Estimated Drift": "N/A",

                "Time": "N/A",

            }

        first = drift[0]

        last = drift[-1]

        delta_lat = last["latitude"] - first["latitude"]

        delta_lon = last["longitude"] - first["longitude"]

        return {

            "Direction": _direction(delta_lat, delta_lon),

            "Estimated Drift": (
                f"{len(drift)} hourly steps"
            ),

            "Time": f"{last['hour']} Hours",

        }

    def _env_summary(self, env_report):

        if not env_report:

            return {}

        return {

            "Nearest Coast": (
                f"{env_report['Nearest Coastline']['distance']} km"
            ),

            "Protected Marine Area": (
                f"{env_report['Nearest Protected Area']['distance']} km"
            ),

            "Fishing Zone": (
                f"{env_report['Nearest Fishing Zone']['distance']} km"
            ),

        }

    def _eco_summary(self, eco_report):

        if not eco_report:

            return {}

        return {

            "Cleanup Cost": (
                f"${eco_report['Cleanup Cost ($)']}"
            ),

            "Economic Loss": (
                f"${eco_report['Total Economic Loss ($)']}"
            ),

        }

    def _suspect_summary(self, vessel):

        if vessel is None:

            return {

                "Ship Name": "N/A",

                "MMSI": "N/A",

                "Type": "N/A",

                "Distance": "N/A",

                "Heading": "N/A",

                "Speed": "N/A",

                "Suspicion Score": "N/A",

            }

        return {

            "Ship Name": str(
                vessel.get("VesselName", vessel.get("MMSI", "N/A"))
            ),

            "MMSI": str(vessel.get("MMSI", "N/A")),

            "Type": str(vessel.get("VesselType", "N/A")),

            "Distance": (
                f"{vessel.get('Distance_km', 'N/A')} km"
            ),

            "Heading": str(vessel.get("COG", "N/A")),

            "Speed": (
                f"{vessel.get('SOG', 'N/A')} knots"
            ),

            "Suspicion Score": str(
                vessel.get("SuspectScore", "N/A")
            ),

        }
