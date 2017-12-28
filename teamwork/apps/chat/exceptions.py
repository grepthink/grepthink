import json



"""
Exception class that catches websocket errors and
sends it back to the client
"""
class ClientError(Exception):
    def init(self, code):
        super(ClientError, self).init(code)
        self.code = code
        
    def send_to(self, channel):
        channel.send({
            "text": json.dumps({
                "error": self.code,
            }),
        })