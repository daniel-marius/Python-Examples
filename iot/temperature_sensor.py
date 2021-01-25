import glob
import os
import time
import urllib

import httplib

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'


def function(var):
    params = urllib.urlencode({'field1': var, 'field2': var, 'key': 'API_KEY...'})
    headers = {"Content-typZZe": "application/x-www-form-urlencode", "Accept": "text/plain"}
    conn = httplib.HTTPConnection("api.thingspeak.com:80")
    conn.request("POST", "/update", params, headers)
    response = conn.getresponse()
    print(response.status, response.reason)
    data = response.read()
    print(data)
    conn.close()


def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines


def read_temp():
    lines = read_temp_raw()

    while lines[0].strip()[-3:] != 'YES':
        time.sleep(1.2)
        lines = read_temp_raw()

    equals_pos = lines[1].find('t=')

    if equals_pos != -1:
        temp_string = lines[1][equals_pos + 2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        temp_k = temp_c + 273.15
        function(temp_c)
        return temp_c, temp_f, temp_k


while True:
    print(read_temp())
    time.sleep(1)
