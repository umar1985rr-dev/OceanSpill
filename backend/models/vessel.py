"""
Vessel model for AIS data caching.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Index
from backend.database import Base


class Vessel(Base):
    """
    AIS vessel position data.

    Caches vessel positions from AIS feeds to reduce API calls
    and enable historical tracking.
    """
    __tablename__ = "vessels"

    id = Column(Integer, primary_key=True, index=True)
    mmsi = Column(String(20), index=True, nullable=False)
    vessel_name = Column(String(255), nullable=True)
    imo = Column(String(20), nullable=True)
    vessel_type = Column(String(50), nullable=True)

    # Position data
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    sog = Column(Float, default=0.0)  # Speed over ground (knots)
    cog = Column(Float, default=0.0)  # Course over ground (degrees)
    heading = Column(Float, nullable=True)

    # Timestamps
    base_datetime = Column(DateTime, nullable=False)
    data_source = Column(String(50), default="csv")  # csv, aishub, marinetraffic, simulated_live

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Index for efficient queries
    __table_args__ = (
        Index('idx_vessel_mmsi_datetime', 'mmsi', 'base_datetime'),
        Index('idx_vessel_position', 'latitude', 'longitude'),
    )

    def __repr__(self):
        return f"<Vessel(mmsi='{self.mmsi}', name='{self.vessel_name}')>"

    def to_dict(self):
        """Convert vessel to dictionary."""
        return {
            "id": self.id,
            "MMSI": self.mmsi,
            "VesselName": self.vessel_name,
            "IMO": self.imo,
            "VesselType": self.vessel_type,
            "LAT": self.latitude,
            "LON": self.longitude,
            "SOG": self.sog,
            "COG": self.cog,
            "Heading": self.heading,
            "BaseDateTime": self.base_datetime.isoformat() if self.base_datetime else None,
            "source": self.data_source,
        }
