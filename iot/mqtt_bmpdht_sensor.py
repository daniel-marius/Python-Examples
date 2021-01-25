import sys
import urllib

import Adafruit_BMP.BMP085 as BMP085
import Adafruit_DHT
import httplib
import paho.mqtt.client as mqtt

# Settings for Connection

host = "iot.eclipse.org"
topic = "kwf/demo/sensor"
port = 1883

sensor2 = BMP085.BMP085()
sensor_args = {'11': Adafruit_DHT.DHT11,
               '22': Adafruit_DHT.DHT22,
               '2302': Adafruit_DHT.AM2302}
if len(sys.argv) == 3 and sys.argv[1] in sensor_args:
    sensor = sensor_args[sys.argv[1]]
    pin = sys.argv[2]
else:
    print('usage: sudo ./Adafruit_DHT.py [11|22|2302] GPIOpin#')
    print('example: sudo ./Adafruit_DHT.py 2302 4 - Read from an AM2302 connected to GPIO #4')
humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)


def function(var, var2):
    params = urllib.urlencode({'field1': var, 'field2': var2, 'key': 'API_KEY...'})
    headers = {"Content-typZZe": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    conn = httplib.HTTPConnection("api.thingspeak.com:80")
    conn.request("POST", "/update", params, headers)
    response = conn.getresponse()
    print(response.status, response.reason)
    data = response.read()
    print(data)
    conn.close()


def function2(var, var2, var3, var4):
    params = urllib.urlencode({'field1': var, 'field2': var2, 'field3': var3, 'field4': var4, 'key': 'API_KEY...'})
    headers = {"Content-typZZe": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    conn = httplib.HTTPConnection("api.thingspeak.com:80")
    conn.request("POST", "/update", params, headers)
    response = conn.getresponse()
    print(response.status, response.reason)
    data = response.read()
    print(data)
    conn.close()


def on_connect(client, userdata, rc):
    print("Connected with rc: " + str(rc))
    client.publish(topic)
    # client.subscribe("kwf/demo/sensor")


def on_message(client, userdata, msg):
    # print ("Topic: "+ msg.topic+"\nMessage: "+str(msg.payload))
    print("Received message: " + str(msg.payload) + " on topic " + msg.topic + " with QoS " + str(msg.qos))
    json_data = msg.payload
    print("JSON Data: " + json_data)
    if "bmp" in msg.payload:
        print('Temp = {0:0.2f} *C'.format(sensor2.read_temperature()))
        print('Pressure = {0:0.2f} Pa'.format(sensor2.read_pressure()))
        print('Altitude = {0:0.2f} m'.format(sensor2.read_altitude()))
        print('Sealevel Pressure = {0:0.2f} Pa'.format(sensor2.read_sealevel_pressure()))
        client.publish(msg.topic, sensor2.read_temperature(), msg.qos, True)
        function2(sensor2.read_temperature(), sensor2.read_pressure(), sensor2.read_altitude(),
                  sensor2.read_sealevel_pressure())

    if "dht11" in msg.payload:
        print('Temp = {0:0.1f} *C  Humidity={1:0.1f}%'.format(temperature, humidity))
        client.publish(msg.topic, temperature, msg.qos, True)
        function(temperature, humidity)


def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed OK")


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_subscribe = on_subscribe

print("Connecting to: " + host + " " + topic)
print("Running on Port: ", port)
client.connect(host, port, 60)
client.subscribe(topic, 0)

# rc=0
# while rc==0:
# rc=client.loop()

# print("rc: "+str(rc))
client.loop_forever()
