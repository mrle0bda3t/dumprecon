import socket
import ssl
def parseService(s):
    for item in s.split("\n"):
        if "server" in item.lower():
            return item.strip()
def getService(ip, port):
    payload1 = b''
    payload2 = b'GET / HTTP/1.0\r\n\r\n'
    payload3 = b'OPTIONS / HTTP/1.0\r\n\r\n'
    payload4 = b'OPTIONS / RTSP/1.0\r\n\r\n'
    payload5 = b'GET /nice%20ports%2C/Tri%6Eity.txt%2ebak HTTP/1.0\r\n\r\n'
    payload6 = b'\x6C\0\x0B\0\0\0\0\0\0\0\0\0'
    allData = ""

    if port!=443:
        payloads_list = [payload1, payload2, payload3, payload4, payload5, payload6]
        for payload in payloads_list:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(10)
                sock.connect((ip, port))
                sock.send(payload)
                data = sock.recv(1024).decode("ISO-8859-1")
                if "<!" in data:
                    allData+=data.split("<!")[0]
                else:
                    allData+=data
            except socket.timeout as e:
                print(str(e))
            except Exception as e:
                print(str(e))
            finally:
                sock.close()
    else:
        payloads_list = [payload1, payload2, payload3, payload4, payload5]
        host = (ip, 443)
        purpose = ssl.Purpose.SERVER_AUTH
        context = ssl.create_default_context(purpose=purpose)
        for payload in payloads_list:
            try:
                with socket.create_connection(host) as sock:
                    with context.wrap_socket(sock, server_hostname=host[0]) as wrapped:
                        wrapped.send(payload)
                        data = wrapped.recv(2048).decode("ISO-8859-1")
                        if "<!" in data:
                            allData+=data.split("<!")[0]
                        else:
                            allData+=data
            except socket.timeout as e:
                print(str(e))
            except Exception as e:
                print(str(e))
            finally:
                sock.close()
    try:
        result = parseService(allData).lower().split("server")[1]
    except Exception as e:
        result = "unknown"
    print(port," ",result)
    return result


