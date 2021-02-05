import socket
import threading
from queue import Queue

target = '192.168.1.12'
queue = Queue()
open_ports = []


def port_scan(target_port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((target, target_port))
        banner = sock.recv(1024)
        if banner:
            print(str(banner.decode("utf-8")))
        return True
    except:
        return False


def fill_queue(port_list):
    for port in port_list:
        queue.put(port)


def worker():
    while not queue.empty():
        port = queue.get()
        if port_scan(port):
            print("Port {} is open!".format(port))
            open_ports.append(port)
        else:
            pass


port_list = range(1, 1024)
fill_queue(port_list)
thread_list = []

for t in range(10):
    thread = threading.Thread(target=worker)
    thread_list.append(thread)

for t in thread_list:
    t.start()

for t in thread_list:
    t.join()

print("Open ports are: ", open_ports)
