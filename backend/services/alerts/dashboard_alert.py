class DashboardAlert:

    def send(self, alert):

        return {

            "type": "Dashboard",

            "status": "SUCCESS",

            "title": alert.title,

            "message": alert.message,

            "severity": alert.severity,

        }