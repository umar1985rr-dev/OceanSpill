import logging

from datetime import datetime

from backend.config import settings

from backend.services.alerts.models import Alert

from backend.services.alerts.dashboard_alert import DashboardAlert

from backend.services.alerts.email_alert import EmailAlert

from backend.services.alerts.sms_alert import SMSAlert

from backend.services.monitoring.state import MonitoringState


class AlertService:
    """
    Fans a detected incident out to every configured channel:

    - Dashboard history (always recorded)
    - Email via SMTP (only when credentials are configured)
    - SMS via Twilio (only when credentials are configured)

    Unconfigured channels degrade gracefully instead of failing.
    """

    def __init__(self, state=None):

        self.state = state or MonitoringState()

        self.dashboard = DashboardAlert()

        self.email = EmailAlert()

        self.sms = SMSAlert()

        self.logger = logging.getLogger(__name__)

    def dispatch(self, incident):

        severity = incident.get("risk_level", "UNKNOWN")

        title = f"Oil Spill Detected at {incident.get('latitude')}, {incident.get('longitude')}"

        message = (
            f"{incident.get('spill_area_km2')} km² spill, "
            f"{incident.get('confidence')}% confidence, "
            f"risk {severity}."
        )

        alert = Alert(
            title=title,
            message=message,
            severity=severity,
        )

        record = {
            "sent_at": datetime.now().isoformat(),
            "title": title,
            "message": message,
            "severity": severity,
            "channels": [],
        }

        # -----------------------------
        # Dashboard (always)
        # -----------------------------

        record["channels"].append(
            self.dashboard.send(alert)
        )

        # -----------------------------
        # Email (if configured)
        # -----------------------------

        if settings.email_address and settings.email_password:

            record["channels"].append(
                self.email.send(alert)
            )

        else:

            self.logger.info(
                "Email alerts not configured - skipped"
            )

        # -----------------------------
        # SMS (if configured)
        # -----------------------------

        if (
            settings.sms_provider.upper() != "SIMULATED"
            and settings.twilio_account_sid
        ):

            record["channels"].append(
                self.sms.send(alert)
            )

        else:

            self.logger.info(
                "SMS alerts not configured - skipped"
            )

        self.state.add_alert(record)

        return record
