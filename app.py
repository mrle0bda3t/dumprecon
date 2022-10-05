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
import requests

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/recon'
mongo = PyMongo(app)

PSfunction = CDLL("/home/r3dvv0p/Desktop/DoAn/webapp/modules/tcp_port_scanner.so")
PSfunction.portScanner.argtypes = [POINTER(c_char), POINTER(c_int)]
def webProbe(subdomain):
    for port in subdomain.ports:
        if port.name in (443,8443,80,80880):
            if port.name==443 or port.name==8443:
                single_entry_url = "https://" + subdomain.name+":"+str(port.name)
            elif port.name==80 or port.name==8080:
                single_entry_url = "http://" + subdomain.name+":"+str(port.name)
            try:
                response = requests.get(single_entry_url, timeout=5, allow_redirects=False)
                if response.status_code == 200: 
                    print(response.url + " resolved")
                    port.setUrl(response.url)
                elif (response.status_code == 301) or (response.status_code == 302):
                    print(response.url + " redirected to " + str(response.headers['Location']))
                    response.url = response.headers['Location']
                    port.setUrl(response.url)
                else: 
                    print(response.url + " caused " + response.status_code)
                    port.setUrl("status code : " + response.status_code)
            except requests.Timeout:
                print(single_entry_url + " request timed out")
                pass
            except requests.ConnectionError:
                print(single_entry_url + " url does not resolve")
                pass
            except:
                pass
        else:
            port.setUrl("unknown")
def scanHost(subdomain):
    a = subdomain.name
    print("Starting scan : ", subdomain.name)
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
            portObj = Port("name","sercive","url")
            portObj.setPort(port)
            if port!=443:
                portObj.setService(bannerGrabbing.getService(ip,port))
            else:
                portObj.setService(bannerGrabbing.getService(subdomain.name,443))
            portsObj.append(portObj)
    subdomain.setPorts(portsObj)
    webProbe(subdomain)

def scan(domain):
    subdomain_list = findSubdomains.findSubdomains(domain,25)
    for subdoms in subdomain_list:
        ports = []
        subdomain = Subdomain("name", ports, "ip")
        subdomain.setName(f'{subdoms}')
        scanHost(subdomain)
        for port in subdomain.ports:
            print(port.url)
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

    


