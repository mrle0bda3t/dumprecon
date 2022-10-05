class Port:
    def __init__(self, name, service):
        self.name = name
        self.service = service
    def setPort(self, name):
        self.name = name
    def setService(self, service):
        self.service = service