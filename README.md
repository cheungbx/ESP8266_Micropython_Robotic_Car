# ESP8266_Micropython_Robotic_Car

![car1](https://github.com/cheungbx/esp8266_Micropython_Robotic_Car/blob/master/car1.jpg) 
![car2](https://github.com/cheungbx/esp8266_Micropython_Robotic_Car/blob/master/car2.jpg) 
![car3](https://github.com/cheungbx/esp8266_Micropython_Robotic_Car/blob/master/webpage.jpg) 
#
# Author: cheungbx  2020/04/30
# ESP8266 Micropython WIFI remote control and Autodrive car
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
