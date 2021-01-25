import time
import urllib

import RPi.GPIO as GPIO
import httplib

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(21, GPIO.OUT)
GPIO.setup(23, GPIO.OUT)
GPIO.setup(24, GPIO.OUT)

PinPIR = 17

print
"PIR Module Test (CTRL-C to exit)"

GPIO.setup(PinPIR, GPIO.IN)

Current_State = 0
Previous_State = 0


def function(var):
    params = urllib.urlencode({'field1': var, 'field2': var, 'key': '86ZD2627TMUR1D6M'})
    headers = {"Content-typZZe": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    conn = httplib.HTTPConnection("api.thingspeak.com:80")
    conn.request("POST", "/update", params, headers)
    response = conn.getresponse()
    print(response.status, response.reason)
    data = response.read()
    print(data)
    conn.close()


try:
    print("Waiting for PIR to settle ...")
    while GPIO.input(PinPIR) == 1:
        Current_State = 0
    print("Ready")
    while True:
        Current_State = GPIO.input(PinPIR)
        if Current_State == 1 and Previous_State == 0:
            print("Motion detected")
            Previous_State = 1
            for i in range(0, 3):
                x = input("Enter a Number: ")
                function(x)

                print("Lights and Sound On")
                GPIO.output(21, GPIO.HIGH)
                GPIO.output(23, GPIO.HIGH)
                GPIO.output(24, GPIO.HIGH)

                time.sleep(1)

                print("Lights and Sound Off")
                GPIO.output(21, GPIO.LOW)
                GPIO.output(23, GPIO.LOW)
                GPIO.output(24, GPIO.LOW)

        elif Current_State == 0 and Previous_State == 1:
            print("Ready")
            Previous_State = 0

        time.sleep(0.1)
except KeyboardInterrupt:
    print("Quit")

    GPIO.cleanup()
