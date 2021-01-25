import json
import os
import smtplib
import time
import xml.dom.minidom
from datetime import datetime

import RPi.GPIO as GPIO


class Sensor:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

    @staticmethod
    def print_details():
        print("Motion Sensor\n")

        print("Print sensor details from TXT file:\n")

        if os.path.exists('config.txt'):
            with open('config.txt', 'r') as f:
                print(f.read())
        else:
            print("Path does not exists !\n")

        print("Print sensor details from XML file:\n")

        if os.path.exists('config.xml'):
            dom_tree = xml.dom.minidom.parse("config.xml")
            config = dom_tree.documentElement
            config2 = config.getElementsByTagName('specifications')
            print("Specifications: \n")
            for c in config2:
                specification1 = c.getElementsByTagName('specification1')[0]
                print(specification1.childNodes[0].data)
                specification2 = c.getElementsByTagName('specification2')[0]
                print(specification2.childNodes[0].data)
                specification3 = c.getElementsByTagName('specification3')[0]
                print(specification3.childNodes[0].data)
                specification4 = c.getElementsByTagName('specification4')[0]
                print(specification4.childNodes[0].data)
                specification5 = c.getElementsByTagName('specification5')[0]
                print(specification5.childNodes[0].data + "\n")

            config3 = config.getElementsByTagName('applications')
            print("Applications: \n")
            for c in config3:
                application1 = c.getElementsByTagName('application1')[0]
                print(application1.childNodes[0].data)
                application2 = c.getElementsByTagName('application2')[0]
                print(application2.childNodes[0].data)
                application3 = c.getElementsByTagName('application3')[0]
                print(application3.childNodes[0].data)
                application4 = c.getElementsByTagName('application4')[0]
                print(application4.childNodes[0].data)
                application5 = c.getElementsByTagName('application5')[0]
                print(application5.childNodes[0].data + "\n")
        else:
            print("Path does not exists !\n")

        print("Print sensor details from JSON file:\n")

        if os.path.exists('config.json'):
            with open('config.json', 'r') as f:
                print(json.load(f))
        else:
            print("Path does not exists !\n")

    @staticmethod
    def sensor_motion():
        pin_pir = ""
        current_state = ""
        previous_state = ""
        number_motions = ""
        current_sensor_value = ""
        new_sensor_value = ""

        if os.path.exists('config.xml'):
            dom_tree = xml.dom.minidom.parse("config.xml")
            config = dom_tree.documentElement
            config2 = config.getElementsByTagName('values')

            for c in config2:
                v1 = c.getElementsByTagName('PinPIR')[0]
                pin_pir = int(v1.childNodes[0].data)
                v2 = c.getElementsByTagName('CurrentState')[0]
                current_state = int(v2.childNodes[0].data)
                v3 = c.getElementsByTagName('PreviousState')[0]
                previous_state = int(v3.childNodes[0].data)
                v4 = c.getElementsByTagName('NumberMotions')[0]
                number_motions = int(v4.childNodes[0].data)
                v5 = c.getElementsByTagName('CurrentSensorValue')[0]
                current_sensor_value = int(v5.childNodes[0].data)
                v6 = c.getElementsByTagName('NewSensorValue')[0]
                new_sensor_value = int(v6.childNodes[0].data)
        else:
            print("Path does not exists !\n")

        if pin_pir < 0 or current_state != 0 or previous_state != 0 or number_motions != 0 or current_sensor_value != 5 or new_sensor_value != 5:
            exit(0)

        GPIO.setup(pin_pir, GPIO.IN)

        try:
            print("Wainting for PIR to settle ...\n")
            while GPIO.input(pin_pir) == 1:
                current_state = 0

                print("Ready\n")
                while True:
                    current_state = GPIO.input(pin_pir)

                    if current_state == 1 and previous_state == 0:
                        print("Motion detected!\n")
                        number_motions += 1
                        print("Number of motions is: ", number_motions, "\n")
                        if number_motions == current_sensor_value:

                            # Email addresses
                            email_to = ""
                            email_from = ""

                            # SMTP email server settings
                            email_server = ""
                            email_port = ""
                            email_user = ""
                            email_password = ""

                            if os.path.exists('config.xml'):
                                dom_tree = xml.dom.minidom.parse("config.xml")
                                config = dom_tree.documentElement
                                config2 = config.getElementsByTagName('email')

                                for c in config2:
                                    email1 = c.getElementsByTagName('email_to')[0]
                                    email_to = email1.childNodes[0].data
                                    email2 = c.getElementsByTagName('email_from')[0]
                                    email_from = email2.childNodes[0].data
                                    email3 = c.getElementsByTagName('mail_server')[0]
                                    mail_server = email3.childNodes[0].data
                                    email4 = c.getElementsByTagName('mail_port')[0]
                                    mail_port = email4.childNodes[0].data
                                    email5 = c.getElementsByTagName('mail_user')[0]
                                    mail_user = email5.childNodes[0].data
                                    email6 = c.getElementsByTagName('mail_password')[0]
                                    mail_password = email6.childNodes[0].data
                            else:
                                print("Path does not exists !\n")

                            if email_to == "" or email_from == "" or email_server == "" or email_port == "" or email_user == "" or email_password == "":
                                exit(0)

                            # Create and send email
                            subject = "Motion sensor value is: " + str(current_sensor_value)
                            header = 'To: ' + email_to + '\n' + 'From: ' + email_from + '\n' + 'Subject: ' + subject
                            body = 'From within a Python script\n'
                            message = header + '\n' + body
                            print(message)

                            smtp = smtplib.SMTP(email_server, email_port)
                            smtp.ehlo()
                            smtp.starttls()
                            smtp.ehlo()
                            smtp.login(email_user, email_password)
                            smtp.sendmail(email_from, email_to, message)
                            smtp.quit()
                            current_sensor_value += new_sensor_value

                        previous_state = 1
                    elif current_state == 0 and previous_state == 1:
                        previous_state = 0

                    time.sleep(0.1)
        except KeyboardInterrupt:
            print("Quit")

            GPIO.cleanup()


if __name__ == "__main__":
    s = Sensor()
    s.print_details()
    print("\nDatetime: " + str(datetime.now()))
    print("\n")
    s.sensor_motion()
