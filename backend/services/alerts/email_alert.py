class EmailAlert:

    def send(self, alert):

        return {

            "type": "Email",

            "status": "SIMULATED",

            "recipient": "alerts@example.com",

            "title": alert.title,

        }