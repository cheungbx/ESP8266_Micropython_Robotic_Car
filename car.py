# Author: cheungbx  2020/04/30
# ESP8266 Micropython WIFI remote contorl and Autodrive car
#
# Pin layout from each module to the Wemos D1 Mini (ESP8266)
# ----------------------------------
# L298N motor module
# IN1->D5->GPIO-14
# IN2->D6->GPIO-12
# IN3->D1->GIO-5
# IN4->D2->GIO-4
# ENA -> +5V (use on board jumper)
# ENB -> +5V (use on board jumper)
# VCC -> +7.4V (two 3.7V rechargable LIPO battery in series)
# GND -> GND
# 5V  -> +5V
# -----------------------------------
# Ultrasound Sensor hcsr04
# GND  -> GND
# Echo -> D8->GPIO-15
# Trig -> D7->GPIO-13
# VCC  -> +5V
# -----------------------------------
# servo Motor
# (brown) GND  -> GND
# (red)   VCC  -> 3.3V
# (orange)Sig  -> D4->GPIO-3
# -----------------------------------

import socket
import machine
import time
from machine import Pin, PWM, ADC, time_pulse_us
from time import sleep, sleep_us, sleep_ms
import hcsr04
from hcsr04 import HCSR04

#HTML to send to browsers
html = """<!DOCTYPE html>
<html>
<head>
<title>ESP8266 MicroPython IoT Car </title>
<style>
body {background-color: black}
h1 {color:red}

button {
        color: red;
        height: 200px;
        width: 200px;
        background:black;
        border: 3px solid #4CAF50; /* Green */
        border-radius: 50%;
        font-size: 250%;
        position: center;
}
</style>
</head>
<body>
<center><h1>ESP8266 Micropython Car Control</h1>
<form>
<div><button name="CMD" value="l" type="submit">L</button>
<button name="CMD" value="forward" type="submit">Forward</button>
<button name="CMD" value="r" type="submit">R</button></div>
<div><button name="CMD" value="left" type="submit">Left</button>
<button name="CMD" value="stop" type="submit">Stop</button>
<button name="CMD" value="right" type="submit">Right</button></div>
<div><button name="CMD" value="back" type="submit">Back</button></div>
<div><button name="CMD" value="slow" type="submit">Slow</button>
<button name="CMD" value="mid" type="submit">Mid</button>
<button name="CMD" value="fast" type="submit">Fast</button></div>
<div><button name="CMD" value="man" type="submit">MAN</button>
<button name="CMD" value="auto" type="submit">AUTO</button></div>
</form>
</center>
</body>
</html>
"""



#skip D4 - built-in LED)

class HCSR04:
    """
    Driver to use the untrasonic sensor HC-SR04.
    The sensor range is between 2cm and 4m.
    The timeouts received listening to echo pin are converted to OSError('Out of range')
    """
    # echo_timeout_us is based in chip range limit (400cm)
    def __init__(self, trigger_pin, echo_pin, echo_timeout_us=500*2*30):
        """
        trigger_pin: Output pin to send pulses
        echo_pin: Readonly pin to measure the distance. The pin should be protected with 1k resistor
        echo_timeout_us: Timeout in microseconds to listen to echo pin.
        By default is based in sensor limit range (4m)
        """
        self.echo_timeout_us = echo_timeout_us
        # Init trigger pin (out)
        self.trigger = Pin(trigger_pin, mode=Pin.OUT, pull=None)
        self.trigger.value(0)

        # Init echo pin (in)
        self.echo = Pin(echo_pin, mode=Pin.IN, pull=None)

    def _send_pulse_and_wait(self):
        """
        Send the pulse to trigger and listen on echo pin.
        We use the method `machine.time_pulse_us()` to get the microseconds until the echo is received.
        """
        self.trigger.value(0) # Stabilize the sensor
        time.sleep_us(5)
        self.trigger.value(1)
        # Send a 10us pulse.
        time.sleep_us(10)
        self.trigger.value(0)
        try:
            pulse_time = machine.time_pulse_us(self.echo, 1, self.echo_timeout_us)
            return pulse_time
        except OSError as ex:
            if ex.args[0] == 110: # 110 = ETIMEDOUT
                raise OSError('Out of range')
            raise ex

    def distance_mm(self):
        pulse_time = self._send_pulse_and_wait()
        mm = pulse_time * 100 // 582
        return mm

    def distance_cm(self):
        pulse_time = self._send_pulse_and_wait()
        cms = (pulse_time / 2) / 29.1
        return cms

sensor = HCSR04(trigger_pin=13, echo_pin=15)


def setMotor(MotorPin, val):
  MotorPin.freq(50)
  MotorPin.duty(val)

Lmotor1 = PWM(Pin(14))
Lmotor2 = PWM(Pin(12))
Rmotor1 = PWM(Pin(5))
Rmotor2 = PWM(Pin(4))

minSpeed = 300
midSpeed = 700
maxSpeed = 1024
speed = midSpeed

servo = machine.PWM(machine.Pin(2), freq=50)
servo.duty(77) #centre

def stop(t=0):
  setMotor(Lmotor1, 0)
  setMotor(Lmotor2, 0)
  setMotor(Rmotor1, 0)
  setMotor(Rmotor2, 0)
  if t > 0 :
    sleep_ms(t)

def forward(t=0):
  setMotor(Lmotor1, 0)
  setMotor(Lmotor2, speed)
  setMotor(Rmotor1, 0)
  setMotor(Rmotor2, speed)
  if t > 0 :
    sleep_ms(t)


def back(t=0):
  setMotor(Lmotor1, speed)
  setMotor(Lmotor2, 0)
  setMotor(Rmotor1, speed)
  setMotor(Rmotor2, 0)
  if t > 0 :
    sleep_ms(t)


def right (t=0):
  setMotor(Lmotor1, 0)
  setMotor(Lmotor2, speed)
  setMotor(Rmotor1, speed)
  setMotor(Rmotor2, 0)
  if t > 0 :
    sleep_ms(t)


def left (t=0):
  setMotor(Lmotor1, speed)
  setMotor(Lmotor2, 0)
  setMotor(Rmotor1, 0)
  setMotor(Rmotor2, speed)
  if t > 0 :
    sleep_ms(t)

def right_cruise (t=0):
  setMotor(Lmotor1, 0)
  setMotor(Lmotor2, speed)
  setMotor(Rmotor1, 0)
  setMotor(Rmotor2, 0)
  if t > 0 :
    sleep_ms(t)

def left_cruise (t=0):
  setMotor(Lmotor1, 0)
  setMotor(Lmotor2, 0)
  setMotor(Rmotor1, 0)
  setMotor(Rmotor2, speed)
  if t > 0 :
    sleep_ms(t)

def forward_distance () :

  servo.duty(77) #centre
  return sensor.distance_cm()

def right_distance () :

  servo.duty(40)
  return sensor.distance_cm()

def left_distance () :

  servo.duty(120)
  return sensor.distance_cm()


def autoDrive () :

  servo_rest = 250
  # check distance from obstacles in cm.
  fd = forward_distance()
  print('forward ', fd)
  # then take actions in milli seconds
  if fd < 10 :
     stop(100)
     back(200)
     print ("+Auto Stop back")
  elif fd < 25 :
      stop(100)
      ld=left_distance ()
      sleep_ms (servo_rest)
      rd=right_distance ()
      sleep_ms (servo_rest)
      print('L ',ld, ' R ', rd)

      if ld < 15 and rd < 15 :
        # backward
        back(800)
        left(300)
        print ("+Auto back left")

      elif ld > rd :
        # left
        back(100)
        left(300)
        print ("+Auto left")

      else : # ld <= rd
        # right
        back(100)
        left(300)
        print ("+Auto right")



  else  : # >= 25
    # forward
    forward (100)
    print ("+Auto forward")




stop()

#Setup Socket WebServer
#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s = socket.socket()

#new?
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

s.bind(('', 80))
s.listen(5)
print("Listening, connect your browser to http://<this_host>:80/")

counter = 0
action = 0
auto=False
while True:
    if auto :
        autoDrive()
    else :
        conn, addr = s.accept()
        print("Got a connection from %s" % str(addr))
        request = conn.recv(1024)
        print("Content = %s" % str(request))
        request = str(request)

        #print("Data: " + str(CMD_forward))
        #print("Data: " + str(CMD_back))
        #print("Data: " + str(CMD_left))
        #print("Data: " + str(CMD_right))
        #print("Data: " + str(CMD_stop))

        if request.find('/?CMD=forward') == 6:
            print('+forward')
            action = 1
        elif request.find('/?CMD=back') == 6:
            print('+back')
            action = 2
        elif request.find('/?CMD=left') == 6:
            print('+left')
            action = 3
        elif request.find('/?CMD=right') == 6:
            print('+right')
            action = 4
        elif request.find('/?CMD=l') == 6:
            print('+L')
            action = 5
        elif request.find('/?CMD=r') == 6:
            print('+R')
            action = 6
        elif request.find('/?CMD=stop') == 6:
            print('+stop')
            action = 0
        elif request.find('/?CMD=fast') == 6:
            print('+fast=')
            speed = maxSpeed
            print (speed)
        elif request.find('/?CMD=slow') == 6:
            print('+slow=')
            speed = minSpeed
            print (speed)
        elif request.find('/?CMD=mid') == 6:
            print('+mid=')
            speed = midSpeed
            print (speed)
        elif request.find('/?CMD=man') == 6:
            auto=False
            action = 0
            print('+manual=')
        elif request.find('/?CMD=auto') == 6:
            auto=True
            action = 0
            print('+autoDrive')

        if action == 0:
            stop ()
        elif action == 1:
            forward()
        elif action == 2:
            back()
        elif action == 3:
            left()
        elif action == 4:
            right()
        elif action == 5:
            left_cruise()
        elif action == 6:
            right_cruise()

        response = html
        conn.send(response)
        conn.close()
