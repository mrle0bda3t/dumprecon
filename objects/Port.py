class Port:
    def __init__(self, name, service, url):
        self.name = name
        self.service = service
        self.url = url
    def setPort(self, name):
        self.name = name
    def setService(self, service):
        self.service = service
    def setUrl(self, url):
        self.url = url