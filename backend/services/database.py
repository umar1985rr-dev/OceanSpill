"""
Database service layer for CRUD operations.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from backend.models.incident import Incident
from backend.models.vessel import Vessel
from backend.models.config import Config, AlertHistory


class IncidentService:
    """Service for incident database operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, incident_data: dict) -> Incident:
        """Create a new incident record."""
        incident = Incident(
            incident_id=incident_data.get("id"),
            detected_at=datetime.fromisoformat(incident_data.get("detected_at"))
            if incident_data.get("detected_at")
            else datetime.utcnow(),
            latitude=incident_data.get("latitude"),
            longitude=incident_data.get("longitude"),
            spill_percentage=incident_data.get("spill_percentage"),
            spill_area_km2=incident_data.get("spill_area_km2"),
            confidence=incident_data.get("confidence"),
            risk_score=incident_data.get("risk_score"),
            risk_level=incident_data.get("risk_level"),
            frame_id=incident_data.get("frame_id"),
            image_path=incident_data.get("image_path"),
            source=incident_data.get("source", "monitoring"),
            wind_speed=incident_data.get("weather", {}).get("wind_speed"),
            wind_direction=incident_data.get("weather", {}).get("wind_direction"),
            current_speed=incident_data.get("current_speed"),
            current_direction=incident_data.get("current_direction"),
            impact_data=incident_data.get("impact"),
            drift_data=incident_data.get("drift"),
            cleanup_data=incident_data.get("cleanup"),
            suspect_vessel=incident_data.get("suspect_vessel"),
            report_path=incident_data.get("report_path"),
        )
        self.db.add(incident)
        self.db.commit()
        self.db.refresh(incident)
        return incident

    def get_by_id(self, incident_id: int) -> Optional[Incident]:
        """Get incident by database ID."""
        return self.db.query(Incident).filter(Incident.id == incident_id).first()

    def get_by_incident_id(self, incident_id: str) -> Optional[Incident]:
        """Get incident by incident_id string."""
        return (
            self.db.query(Incident).filter(Incident.incident_id == incident_id).first()
        )

    def list(
        self,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        risk_level: Optional[str] = None,
    ):
        """List incidents with pagination and filters."""
        query = self.db.query(Incident)

        if status:
            query = query.filter(Incident.status == status)
        if risk_level:
            query = query.filter(Incident.risk_level == risk_level)

        total = query.count()
        incidents = (
            query.order_by(Incident.detected_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return incidents, total

    def update_status(
        self,
        incident_id: int,
        status: str,
        resolved_by: Optional[int] = None,
        resolution_notes: Optional[str] = None,
    ) -> Optional[Incident]:
        """Update incident status."""
        incident = self.get_by_id(incident_id)
        if not incident:
            return None

        incident.status = status
        if status == "resolved":
            incident.resolved_at = datetime.utcnow()
            incident.resolved_by = resolved_by
            incident.resolution_notes = resolution_notes

        self.db.commit()
        self.db.refresh(incident)
        return incident

    def update_report_path(self, incident_id: int, report_path: str) -> Optional[Incident]:
        """Update incident report path."""
        incident = self.get_by_id(incident_id)
        if not incident:
            return None

        incident.report_path = report_path
        self.db.commit()
        self.db.refresh(incident)
        return incident


class VesselService:
    """Service for vessel database operations."""

    def __init__(self, db: Session):
        self.db = db

    def create_or_update(self, vessel_data: dict) -> Vessel:
        """Create or update a vessel record (upsert by MMSI + datetime)."""
        mmsi = vessel_data.get("MMSI") or vessel_data.get("mmsi")
        base_datetime = vessel_data.get("BaseDateTime") or vessel_data.get("base_datetime")

        if isinstance(base_datetime, str):
            base_datetime = datetime.fromisoformat(base_datetime)

        vessel = (
            self.db.query(Vessel)
            .filter(Vessel.mmsi == mmsi, Vessel.base_datetime == base_datetime)
            .first()
        )

        if vessel:
            # Update existing
            vessel.vessel_name = vessel_data.get("VesselName") or vessel_data.get("vessel_name")
            vessel.imo = vessel_data.get("IMO") or vessel_data.get("imo")
            vessel.vessel_type = vessel_data.get("VesselType") or vessel_data.get("vessel_type")
            vessel.latitude = vessel_data.get("LAT") or vessel_data.get("latitude")
            vessel.longitude = vessel_data.get("LON") or vessel_data.get("longitude")
            vessel.sog = vessel_data.get("SOG") or vessel_data.get("sog", 0.0)
            vessel.cog = vessel_data.get("COG") or vessel_data.get("cog", 0.0)
            vessel.heading = vessel_data.get("Heading") or vessel_data.get("heading")
            vessel.data_source = vessel_data.get("source", "csv")
            vessel.updated_at = datetime.utcnow()
        else:
            # Create new
            vessel = Vessel(
                mmsi=mmsi,
                vessel_name=vessel_data.get("VesselName") or vessel_data.get("vessel_name"),
                imo=vessel_data.get("IMO") or vessel_data.get("imo"),
                vessel_type=vessel_data.get("VesselType") or vessel_data.get("vessel_type"),
                latitude=vessel_data.get("LAT") or vessel_data.get("latitude"),
                longitude=vessel_data.get("LON") or vessel_data.get("longitude"),
                sog=vessel_data.get("SOG") or vessel_data.get("sog", 0.0),
                cog=vessel_data.get("COG") or vessel_data.get("cog", 0.0),
                heading=vessel_data.get("Heading") or vessel_data.get("heading"),
                base_datetime=base_datetime,
                data_source=vessel_data.get("source", "csv"),
            )
            self.db.add(vessel)

        self.db.commit()
        self.db.refresh(vessel)
        return vessel

    def bulk_upsert(self, vessels: list[dict]) -> int:
        """Bulk upsert vessels. Returns count of processed records."""
        count = 0
        for v in vessels:
            self.create_or_update(v)
            count += 1
        return count

    def get_latest_by_mmsi(self, mmsi: str) -> Optional[Vessel]:
        """Get the latest position for a vessel."""
        return (
            self.db.query(Vessel)
            .filter(Vessel.mmsi == mmsi)
            .order_by(Vessel.base_datetime.desc())
            .first()
        )

    def get_vessels_nearby(
        self, lat: float, lon: float, radius_km: float = 20
    ) -> list[Vessel]:
        """Get vessels within radius (approximate - uses bounding box)."""
        # Rough degree to km conversion
        lat_delta = radius_km / 111.0
        lon_delta = radius_km / (111.0 * abs(lat) * 0.01745)

        return (
            self.db.query(Vessel)
            .filter(
                Vessel.latitude.between(lat - lat_delta, lat + lat_delta),
                Vessel.longitude.between(lon - lon_delta, lon + lon_delta),
            )
            .order_by(Vessel.base_datetime.desc())
            .limit(100)
            .all()
        )


class ConfigService:
    """Service for configuration database operations."""

    def __init__(self, db: Session):
        self.db = db

    def get(self, key: str) -> Optional[Config]:
        """Get config by key."""
        return self.db.query(Config).filter(Config.key == key).first()

    def get_value(self, key: str, default=None):
        """Get config value by key."""
        config = self.get(key)
        return config.value if config else default

    def set(self, key: str, value: dict, description: str = None, updated_by: int = None):
        """Set config value."""
        config = self.get(key)
        if config:
            config.value = value
            if description:
                config.description = description
            if updated_by:
                config.updated_by = updated_by
        else:
            config = Config(key=key, value=value, description=description, updated_by=updated_by)
            self.db.add(config)

        self.db.commit()
        self.db.refresh(config)
        return config

    def list(self) -> list[Config]:
        """List all config entries."""
        return self.db.query(Config).all()


class AlertHistoryService:
    """Service for alert history database operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        incident_id: int,
        alert_type: str,
        status: str = "sent",
        recipient: str = None,
        message: dict = None,
    ) -> AlertHistory:
        """Create an alert history record."""
        alert = AlertHistory(
            incident_id=incident_id,
            alert_type=alert_type,
            status=status,
            recipient=recipient,
            message=message,
        )
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        return alert

    def get_by_incident(self, incident_id: int) -> list[AlertHistory]:
        """Get alert history for an incident."""
        return (
            self.db.query(AlertHistory)
            .filter(AlertHistory.incident_id == incident_id)
            .order_by(AlertHistory.sent_at.desc())
            .all()
        )

    def list(self, page: int = 1, page_size: int = 50) -> tuple[list[AlertHistory], int]:
        """List all alert history with pagination."""
        query = self.db.query(AlertHistory)
        total = query.count()
        alerts = (
            query.order_by(AlertHistory.sent_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return alerts, total