from flask import * 
import socket
from ctypes import *
import ctypes
from modules.findSubdomains import findSubdomains
from modules.bannerGrabbing import bannerGrabbing
from threading import Lock
from flask_pymongo import PyMongo
import threading
from objects.Port import Port
from objects.Subdomain import Subdomain

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/recon'
mongo = PyMongo(app)

PSfunction = CDLL("/home/r3dvv0p/Desktop/DoAn/webapp/modules/tcp_port_scanner.so")
PSfunction.portScanner.argtypes = [POINTER(c_char), POINTER(c_int)]
# def webProbe(subdomain):

def scanHost(subdomain):
    a = subdomain.name
    print("starting scan ", subdomain.name)
    ip = socket.gethostbyname(a)
    subdomain.setIp(ip)
    tcp_scan(subdomain)


def tcp_scan(subdomain):
    ip = socket.gethostbyname(subdomain.name)
    portsObj = []
    ports = [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]
    ports_c = (c_int*10)(*ports)
    PSfunction.portScanner(ctypes.c_char_p(ip.encode('utf-8')),ports_c)

    for port in ports_c:
        if(port!=-1):
            portObj = Port("name","sercive")
            portObj.setPort(port)
            if port!=443:
                portObj.setService(bannerGrabbing.getService(ip,port))
            else:
                portObj.setService(bannerGrabbing.getService(subdomain.name,443))
            portsObj.append(portObj)
    subdomain.setPorts(portsObj)
   
def scan(domain):
    subdomain_list = findSubdomains.findSubdomains(domain,25)
    for subdoms in subdomain_list:
        ports = []
        subdomain = Subdomain("name", ports, "ip")
        subdomain.setName(f'{subdoms}')
        scanHost(subdomain)
        for port in subdomain.ports:
            mongo.db.subdomain.insert_one(dict(name=subdomain.name,ip=subdomain.ip,port=port.name,service=port.service))  
 
@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/recon", methods=["POST", "GET"])
def recon():          
    domain = "<Domain Not Defined>"
    if (request.method == "POST"):
        domain = request.form["name"]
    daemon = threading.Thread(target=scan, args=(domain,), daemon=True, name='Background')
    daemon.start()
    return render_template("recon.html",subDomain = domain) 

if __name__ == "__main__": 
    app.run(port=4949, debug=True)

    


