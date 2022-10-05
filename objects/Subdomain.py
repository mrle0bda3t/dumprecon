class Subdomain:
    def __init__(self, name, ports, ip):
        self.name = name
        self.ports = ports
        self.ip = ip
    def setPorts(self, ports):
        self.ports = ports
    def setName(self, name):
        self.name = name
    def setIp(self, ip):
        self.ip = ip