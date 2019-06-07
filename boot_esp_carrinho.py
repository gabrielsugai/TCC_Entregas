# This file is executed on every boot (including wake-boot from deepsleep)

#import esp

#esp.osdebug(None)

import uos, machine

#uos.dupterm(None, 1) # disable REPL on UART(0)

import gc

#import webrepl

#webrepl.start()

gc.collect()

from machine import Pin, PWM
from time import sleep
from machine import Timer

tim = Timer(-1)


pwm0 = PWM(Pin(4), freq=20000,duty=0)#esquerda - D2
pwm1 = PWM(Pin(0), freq=20000,duty=0)#direita - D3
inp1 = Pin(5, Pin.OUT)
inp2 = Pin(16, Pin.OUT)

ir1 = Pin(12, Pin.IN)
ir2 = Pin(14, Pin.IN)
ir3 = Pin(13, Pin.IN)

def varredura(var):
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
tim.init(period=30, mode=Timer.PERIODIC, callback=varredura)