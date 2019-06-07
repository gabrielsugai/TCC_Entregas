import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import sys
from time import sleep

stepPin = 2
dirPin = 3

GPIO.setmode(GPIO.BCM)

GPIO.setup(stepPin, GPIO.OUT)
GPIO.setup(dirPin, GPIO.OUT)
 #liga pino GPIO.output(pino,1 ou 0)
 while True:
    GPIO.output(dirPin,1)
    for i in range(200):
        GPIO.output(stepPin,1)
        sleep(0.05)
        GPIO.output(stepPin,0)
        sleep(0.05)  

'''

para modificar o dados do usuario para em separação
http://tcc-entregas.onlinewebshop.net/views/esp.php?idu=01&sta=3

para modificar o dados do usuario para enviado
http://tcc-entregas.onlinewebshop.net/views/esp.php?idu=01&sta=3

para modificar o dados do usuario para separado
http://tcc-entregas.onlinewebshop.net/views/esp.php


'''