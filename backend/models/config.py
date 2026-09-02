"""
Configuration model for system settings.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON
from backend.database import Base


class Config(Base):
    """
    System configuration stored in database.

    Allows runtime configuration changes without environment variables.
    Each config entry has a key and JSON value.
    """
    __tablename__ = "config"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, index=True, nullable=False)
    value = Column(JSON, nullable=False)
    description = Column(String(500), nullable=True)
    updated_by = Column(Integer, nullable=True)  # User ID who last updated
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Config(key='{self.key}')>"

    def to_dict(self):
        """Convert config to dictionary."""
        return {
            "key": self.key,
            "value": self.value,
            "description": self.description,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class AlertHistory(Base):
    """
    Alert history for audit trail.
    """
    __tablename__ = "alert_history"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, index=True, nullable=False)
    alert_type = Column(String(50), nullable=False)  # dashboard, email, sms
    status = Column(String(50), default="sent")  # sent, failed, pending
    recipient = Column(String(255), nullable=True)
    message = Column(JSON, nullable=True)
    sent_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "incident_id": self.incident_id,
            "alert_type": self.alert_type,
            "status": self.status,
            "recipient": self.recipient,
            "message": self.message,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
        }
