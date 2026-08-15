import os

from dataclasses import dataclass


def _env_float(key, default):

    value = os.getenv(key)

    if value is None:

        return default

    return float(value)


def _env_int(key, default):

    value = os.getenv(key)

    if value is None:

        return default

    return int(value)


def _env_bool(key, default):

    value = os.getenv(key)

    if value is None:

        return default

    return value.strip().lower() in ("1", "true", "yes", "on")


@dataclass
class Settings:
    """Central application settings, read from environment variables."""

    # ----------------------------------------------------------
    # Application
    # ----------------------------------------------------------

    app_name: str

    debug: bool

    host: str

    port: int

    # ----------------------------------------------------------
    # Satellite feed
    # ----------------------------------------------------------

    # "simulator" or "sentinel_hub"
    feed_source: str

    # Directory the simulator streams frames from
    simulator_images_dir: str

    # Location embedded in every simulated frame
    incident_latitude: float

    incident_longitude: float

    # ----------------------------------------------------------
    # Monitoring loop
    # ----------------------------------------------------------

    monitor_enabled: bool

    monitor_interval_seconds: int

    # Spill percentage above which an incident is declared
    detection_threshold: float

    # ----------------------------------------------------------
    # Display
    # ----------------------------------------------------------

    currency: str

    # ----------------------------------------------------------
    # Email alerts
    # ----------------------------------------------------------

    smtp_host: str

    smtp_port: int

    email_address: str

    email_password: str

    email_recipients: str

    # ----------------------------------------------------------
    # SMS alerts
    # ----------------------------------------------------------

    sms_provider: str

    twilio_account_sid: str

    twilio_auth_token: str

    twilio_from: str

    sms_recipients: str


def load_settings():

    return Settings(
        app_name=os.getenv("APP_NAME", "OceanSpill"),
        debug=_env_bool("DEBUG", True),
        host=os.getenv("HOST", "0.0.0.0"),
        port=_env_int("PORT", 8000),
        feed_source=os.getenv("FEED_SOURCE", "simulator"),
        simulator_images_dir=os.getenv(
            "SIMULATOR_IMAGES_DIR",
            "dataset/samples/satellite_images",
        ),
        incident_latitude=_env_float("INCIDENT_LATITUDE", 13.08),
        incident_longitude=_env_float("INCIDENT_LONGITUDE", 80.27),
        monitor_enabled=_env_bool("MONITOR_ENABLED", True),
        monitor_interval_seconds=_env_int("MONITOR_INTERVAL_SECONDS", 30),
        detection_threshold=_env_float("DETECTION_THRESHOLD", 1.0),
        currency=os.getenv("CURRENCY", "₹"),
        smtp_host=os.getenv("SMTP_HOST", "smtp.gmail.com"),
        smtp_port=_env_int("SMTP_PORT", 587),
        email_address=os.getenv("EMAIL_ADDRESS", ""),
        email_password=os.getenv("EMAIL_PASSWORD", ""),
        email_recipients=os.getenv("EMAIL_RECIPIENTS", ""),
        sms_provider=os.getenv("SMS_PROVIDER", "SIMULATED"),
        twilio_account_sid=os.getenv("TWILIO_ACCOUNT_SID", ""),
        twilio_auth_token=os.getenv("TWILIO_AUTH_TOKEN", ""),
        twilio_from=os.getenv("TWILIO_FROM", ""),
        sms_recipients=os.getenv("SMS_RECIPIENTS", ""),
    )


settings = load_settings()
