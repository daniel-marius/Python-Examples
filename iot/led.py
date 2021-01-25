import time

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

leds = [17, 27, 18]

for i in leds:
    GPIO.setup(i, GPIO.OUT)
    GPIO.output(i, False)

try:

    while True:
        GPIO.output(leds[0], True)
        time.sleep(10)

        GPIO.output(leds[1], True)
        time.sleep(2)

        GPIO.output(leds[0], False)
        GPIO.output(leds[1], False)
        GPIO.output(leds[2], True)
        time.sleep(10)

        GPIO.output(leds[1], True)
        GPIO.output(leds[2], False)
        time.sleep(2)

        GPIO.output(leds[1], False)

except KeyboardInterrupt:
    GPIO.cleanup()
