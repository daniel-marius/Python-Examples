import time
import urllib

import httplib
import spidev


def function(var, var2):
    params = urllib.urlencode({'field1': var, 'field2': var2, 'key': 'API_KEY...'})
    headers = {"Content-typZZe": "application/x-www-form-urlencode", "Accept": "text/plain"}
    conn = httplib.HTTPConnection("api.thingspeak.com:80")
    conn.request("POST", "/update", params, headers)
    response = conn.getresponse()
    print(response.status, response.reason)
    data = response.read()
    print(data)
    conn.close()


def get_adc(device=0, channel=0):
    spi = spidev.SpiDev()
    spi.open(0, device)
    command = [1, (2 + channel) << 6, 0]
    reply = spi.xfer2(command)
    value = reply[1] & 31
    value = value << 6
    value = value + (reply[2] >> 2)
    spi.close()
    return value


air_channel = 0
light_channel = 1
device = 0

while True:
    try:
        air_quality = get_adc(device, air_channel)
        light_level = get_adc(device, light_channel)
        function(air_quality, light_level)
        if air_quality > 700:
            print("High Pollution")
        elif air_quality > 300:
            print("Low Pollution")
        else:
            print("Air Fresh")
        print("Air value: ", air_quality)
        print("Light value: ", light_level)
        time.sleep(1)
    except IOError:
        print("Error")
