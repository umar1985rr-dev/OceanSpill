from backend.services.monitoring.state import MonitoringState

from backend.services.monitoring.service import MonitoringService

# Application-wide singleton used by the API layer.
monitoring_service = MonitoringService()
