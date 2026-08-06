class EmailAlert:

    def send(self, alert):

        return {

            "type": "Email",

            "status": "SIMULATED",

            "recipient": "authority@oceanspill.ai",

            "title": alert.title,

        }