# -*- coding: utf-8 -*-

from time import sleep
import sys
import random
import cloud4rpi
import ds18b20
import rpi
import RPi.GPIO as GPIO  # pylint: disable=F0401
import FaBo9Axis_MPU9250
import time
import serial
import pynmea2

# Put your device token here. To get the token,
# sign up at https://cloud4rpi.io and create a device.
DEVICE_TOKEN = '' #Removed for security reasons

mpu9250 = FaBo9Axis_MPU9250.MPU9250()
serialStream = serial.Serial("/dev/ttyAMA0", 9600, timeout=0.5)

# Constants
LED_PIN = 12
DATA_SENDING_INTERVAL = 5  # secs
DIAG_SENDING_INTERVAL = 60  # secs
POLL_INTERVAL = 0.5  # 500 ms

# Configure GPIO library
GPIO.setmode(GPIO.BOARD)
GPIO.setup(LED_PIN, GPIO.OUT)


# Handler for the button or switch variable
def led_control(value=None):
    GPIO.output(LED_PIN, value)
    return GPIO.input(LED_PIN)
###########################################
def check_acc_x():
    accel= mpu9250.readAccel()
    return ( accel['x'] )

def check_acc_y():
    accel= mpu9250.readAccel()
    return ( accel['y'] )

def check_acc_z():
    accel= mpu9250.readAccel()
    return ( accel['z'] )

##########################################
def check_gyro_x():
    gyro = mpu9250.readGyro()
    return ( gyro['x'] )

def check_gyro_y():
    gyro = mpu9250.readGyro()
    return ( gyro['y'] )

def check_gyro_z():
    gyro = mpu9250.readGyro()
    return ( gyro['z'] )
##########################################
def check_mag_x():
    mag = mpu9250.readMagnet()
    return ( mag['x'] )

def check_mag_y():
    mag = mpu9250.readMagnet()
    return ( mag['y'] )

def check_mag_z():
    mag = mpu9250.readMagnet()
    return ( mag['z'] )
#########################################

def check_lat():
    sentence = serialStream.readline()
    if sentence.find('GNGGA') > 0:
       data = pynmea2.parse(sentence)
    return data.latitude

def check_long():
    sentence = serialStream.readline()
    if sentence.find('GNGGA') > 0:
       data = pynmea2.parse(sentence)
    return data.longitude

########################################

def main():

    variables = {
        'Acc_x': {
            'type': 'numeric',
	    'bind': check_acc_x 
        },

        'Acc_y': {
            'type': 'numeric',
            'bind': check_acc_y
        },

        'Acc_z': {
            'type': 'numeric',
            'bind': check_acc_z
        },

        'Gyro_x': {
            'type': 'numeric',
            'bind': check_gyro_x
        },

        'Gyro_y': {
            'type': 'numeric',
            'bind': check_gyro_y
        },

        'Gyro_z': {
            'type': 'numeric',
            'bind': check_gyro_z
        },

        'Mag_x': {
            'type': 'numeric',
            'bind': check_mag_x
        },

        'Mag_y': {
            'type': 'numeric',
            'bind': check_mag_y
        },

        'Mag_z': {
            'type': 'numeric',
            'bind': check_mag_z
        },

        'latitude': {
            'type': 'numeric',
            'bind': check_lat
        },

        'longitude': {
            'type': 'numeric',
            'bind': check_long
        },

        'CPU Temp': {
            'type': 'numeric',
            'bind': rpi.cpu_temp
        },
    }

    diagnostics = {
        'CPU Temp': rpi.cpu_temp,
        'IP Address': rpi.ip_address,
        'Host': rpi.host_name,
        'Operating System': rpi.os_name
    }
    device = cloud4rpi.connect(DEVICE_TOKEN)

    # Use the following 'device' declaration
    # to enable the MQTT traffic encryption (TLS).
    #
    # tls = {
    #     'ca_certs': '/etc/ssl/certs/ca-certificates.crt'
    # }
    # device = cloud4rpi.connect(DEVICE_TOKEN, tls_config=tls)

    try:
        device.declare(variables)
        device.declare_diag(diagnostics)

        device.publish_config()

        # Adds a 1 second delay to ensure device variables are created
        sleep(1)

        data_timer = 0
        diag_timer = 0


        while True:

            if data_timer <= 0:
                device.publish_data()
                data_timer = DATA_SENDING_INTERVAL

            if diag_timer <= 0:
                device.publish_diag()
                diag_timer = DIAG_SENDING_INTERVAL

            sleep(POLL_INTERVAL)
            diag_timer -= POLL_INTERVAL
            data_timer -= POLL_INTERVAL

    except KeyboardInterrupt:
        cloud4rpi.log.info('Keyboard interrupt received. Stopping...')

    except Exception as e:
        error = cloud4rpi.get_error_message(e)
        cloud4rpi.log.exception("ERROR! %s %s", error, sys.exc_info()[0])

    finally:
        sys.exit(0)


if __name__ == '__main__':
    main()
