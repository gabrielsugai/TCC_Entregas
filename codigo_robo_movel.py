import uos, machine
import gc
gc.collect()
from machine import Pin, PWM
from time import sleep
from machine import Timer
from umqtt.simple import MQTTClient
import network

tim2 = Timer(-1)
pwm0 = PWM(Pin(4), freq=20000,duty=0)#esquerda - D2
pwm1 = PWM(Pin(0), freq=20000,duty=0)#direita - D3
inp1 = Pin(5, Pin.OUT)
inp2 = Pin(16, Pin.OUT)
ir1 = Pin(12, Pin.IN)
ir2 = Pin(14, Pin.IN)
ir3 = Pin(13, Pin.IN)

tim = Timer(-1)

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('GABRIEL 2.4G','28182006')
print("Conectando...")
while not wlan.isconnected():
  sleep(2)
print('Network config:', wlan.ifconfig())

end_broker = '192.168.0.34'
acao = ('seguir')
##############################################################################

def varredura(var):
    global inp1, inp2, pwm0, pwm1, ir1, ir2, ir3
    if ir1.value()== 0 and ir2.value()== 0 and ir3.value()== 0:
        inp1.value(1)
        inp2.value(0)
        pwm0.duty(650)
        pwm1.duty(650)
    elif ir1.value()!= 0 and ir2.value()== 0 and ir3.value()== 0:
        inp1.value(1)
        inp2.value(0)
        pwm0.duty(700)
        pwm1.duty(0)
    elif ir1.value()!= 0 and ir2.value()!= 0 and ir3.value()== 0:
        inp1.value(1)
        inp2.value(0)
        pwm0.duty(800)
        pwm1.duty(0)
    elif ir1.value()== 0 and ir2.value()== 0 and ir3.value()!= 0:
        inp1.value(1)
        inp2.value(0)
        pwm0.duty(0)
        pwm1.duty(700)
    elif ir1.value()== 0 and ir2.value()!= 0 and ir3.value()!= 0:
        inp1.value(1)
        inp2.value(0)
        pwm0.duty(0)
        pwm1.duty(800)
 
def avancar(topic, msg):
  global acao
  print((topic, msg))
  if msg == b'seguir':
    acao = 'seguir'
    inp1.value(1)
    inp2.value(0)
    pwm0.duty(900)
    pwm1.duty(900)
    inp1.value(1)
    inp2.value(0)
    pwm0.duty(900)
    pwm1.duty(900)
  else:
    acao = 'parar'

def main(server=end_broker):
    global c
    c = MQTTClient("umqtt_client_seguidor_linha", server)
    c.set_callback(avancar) #callback é a funcao chamada quando chegar uma mensagem mqtt
    c.connect()
    c.subscribe("robo1")

def checar_msng():
    global c
    c.check_msg()
    #c.disconnect()
    sleep(0.02)

main()

while True:
  checar_msng()
  if acao == 'seguir':
    checar_msng()
    tim2.init(period=30, mode=Timer.PERIODIC, callback=varredura)
  if acao == 'parar':
    checar_msng()
    inp1.value(0)
    inp2.value(0)