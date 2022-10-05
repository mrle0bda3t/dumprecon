
from requests import get
from random import choice
from threading import Thread
import threading
import os
import random
import requests
from urllib.parse import urlparse
import dns.resolver
UA_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources', 'user_agents.txt')

USER_AGENTS = [line.strip() for line in open(UA_FILE)]
listSubs = []
def get_request(link, timeout):
    head = {
        # 'User-Agent': '{}'.format(choice(USER_AGENTS)),
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Upgrade-Insecure-Requests': '1'}
    try:
        return get(link, headers=head, verify=False, timeout=timeout)
    except:
        return False
def crtsh(target, timeout=25):
    link = "https://crt.sh/?q=%25.{}&output=json".format(target)
    
    try:
        resp = get_request(link, timeout)
        if resp.text and resp.status_code == 200:
            for data in resp.json():
                sub = data['name_value']
                for xsub in sub.split('\n'):
                    for xxsub in xsub.split('\n'):
                        if xxsub.lower().replace("*.","") not in listSubs:
                            listSubs.append(xxsub.lower().replace("*.",""))              
    except:
        pass
    print("######-crtsh-######")
def dns_dumpster(target, timeout=25):
    link = "https://api.hackertarget.com/hostsearch/?q={}".format(target)
    try:
        resp = requests.get(link, timeout)
        if resp.text and resp.status_code == 200:
            for line in resp.text.splitlines():
                if line.count('.') > 1:
                    sub = dns_dumpster_extractor(line)
                    if sub.lower() not in listSubs:
                        listSubs.append(sub.lower()) 
    except:
        pass
    print("######-dns_dumster-######")
def dns_dumpster_extractor(line):
    try:
        return line.split(",")[0]
    except:
        return False
def archive_org(target, timeout):
    link = "http://web.archive.org/cdx/search/cdx?url=*.{}/*&output=json&collapse=urlkey".format(target)
    try:
        resp = get_request(link.format(target),timeout)
        if resp.text and resp.status_code == 200:
            for data in resp.json():
                sub = urlparse(data[2]).netloc
                if ":" in sub: # Parse out Port
                    sub = sub.split(":")[0]
                    if sub.lower() not in listSubs:
                        listSubs.append(sub.lower()) 
    except:
        pass
def brute(target, timeout):
    active_th = []
    wordlistlink = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources', 'subdomains.txt')
    wordlist = [line.strip() for line in open(wordlistlink)]
    for s in wordlist:
        th = threading.Thread(target=resolver, args=('{}.{}'.format(s, target),))
        th.daemon = True
        active_th.append(th)
        th.start()

        while len(active_th) > 15:
            for th in reversed(active_th):
                if not th.is_alive():
                    active_th.remove(th)

    while len(active_th) > 0:
        for th in reversed(active_th):
            if not th.is_alive():
                active_th.remove(th)
def resolver(sub):
    try:
        dns_query = dns_lookup(sub, 'A')
        if dns_query:
            listSubs.append(sub)
    except:
        pass
def dns_lookup(target, lookup_type):
    results = []
    try:
        res = dns.resolver.Resolver()
        res.timeout = 2
        res.lifetime = 2
        dns_query = res.query(target, lookup_type)
        dns_query.nameservers = ['1.1.1.1', '8.8.8.8']
        for name in dns_query:
            results.append(str(name))
    except:
        pass
    return results
def findSubdomains(domain, timeout):
    t1 = threading.Thread(target=crtsh, args=(domain,timeout))
    t2 = threading.Thread(target=dns_dumpster, args=(domain,timeout))
    t3 = threading.Thread(target=archive_org, args=(domain,timeout))
    t1.start()
    t2.start()
    t3.start()
    t1.join()
    t2.join()
    t3.join()
    brute(domain, timeout)
    return listSubs

