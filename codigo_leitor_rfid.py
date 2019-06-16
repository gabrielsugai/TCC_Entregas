import uos, machine
#uos.dupterm(None, 1) # disable REPL on UART(0)
import gc
#import webrepl
#webrepl.start()
gc.collect()
#################################################################

import network,time
from umqtt.simple import MQTTClient
from machine import Timer

tim = Timer(-1)

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('GABRIEL 2.4G','28182006')
print("Conectando...")
while not wlan.isconnected():
  time.sleep(2)
print('Network config:', wlan.ifconfig())

end_broker = '192.168.0.34'
server=end_broker
c = MQTTClient("umqtt_client_sugai", server)
aux_dados = 'aux'

def pub_mqtt(dados):
    c.connect()
    c.publish("robo1", dados)
    c.disconnect()
  
#Arquivo para teste do NodeMCU fazendo a leitura do Cartão RFID
from machine import Pin, SPI, Timer
import time

class MFRC522_Custom:

	def __init__(self, rst, cs):

		self.OK = 0
		self.NOTAGERR = 1
		self.ERR = 2

		self.REQIDL = 0x26
		self.REQALL = 0x52
		self.AUTHENT1A = 0x60
		self.AUTHENT1B = 0x61
		
		self.rst = Pin(rst, Pin.OUT)
		self.cs = Pin(cs, Pin.OUT)

		self.rst.value(0)
		self.cs.value(1)

		self.spi = SPI(1, baudrate=100000, polarity=0, phase=0)
		self.spi.init()

		self.rst.value(1)
		self.init()

	def _wreg(self, reg, val):

		self.cs.value(0)
		self.spi.write(b'%c' % int(0xff & ((reg << 1) & 0x7e)))
		self.spi.write(b'%c' % int(0xff & val))
		self.cs.value(1)

	def _rreg(self, reg):

		self.cs.value(0)
		self.spi.write(b'%c' % int(0xff & (((reg << 1) & 0x7e) | 0x80)))
		val = self.spi.read(1)
		self.cs.value(1)

		return val[0]

	def _sflags(self, reg, mask):
		self._wreg(reg, self._rreg(reg) | mask)

	def _cflags(self, reg, mask):
		self._wreg(reg, self._rreg(reg) & (~mask))

	def _tocard(self, cmd, send):

		recv = []
		bits = irq_en = wait_irq = n = 0
		stat = self.ERR

		if cmd == 0x0E:
			irq_en = 0x12
			wait_irq = 0x10
		elif cmd == 0x0C:
			irq_en = 0x77
			wait_irq = 0x30

		self._wreg(0x02, irq_en | 0x80)
		self._cflags(0x04, 0x80)
		self._sflags(0x0A, 0x80)
		self._wreg(0x01, 0x00)

		for c in send:
			self._wreg(0x09, c)
		self._wreg(0x01, cmd)

		if cmd == 0x0C:
			self._sflags(0x0D, 0x80)
#MUDANDO AQUI!
		i = 100
		while True:
			n = self._rreg(0x04)
			i -= 1
			if ~((i != 0) and ~(n & 0x01) and ~(n & wait_irq)):
				break

		self._cflags(0x0D, 0x80)

		if i:
			if (self._rreg(0x06) & 0x1B) == 0x00:
				stat = self.OK

				if n & irq_en & 0x01:
					stat = self.NOTAGERR
				elif cmd == 0x0C:
					n = self._rreg(0x0A)
					lbits = self._rreg(0x0C) & 0x07
					if lbits != 0:
						bits = (n - 1) * 8 + lbits
					else:
						bits = n * 8

					if n == 0:
						n = 1
					elif n > 16:
						n = 16

					for _ in range(n):
						recv.append(self._rreg(0x09))
			else:
				stat = self.ERR

		return stat, recv, bits

	def _crc(self, data):

		self._cflags(0x05, 0x04)
		self._sflags(0x0A, 0x80)

		for c in data:
			self._wreg(0x09, c)

		self._wreg(0x01, 0x03)

		i = 0xFF
		while True:
			n = self._rreg(0x05)
			i -= 1
			if not ((i != 0) and not (n & 0x04)):
				break

		return [self._rreg(0x22), self._rreg(0x21)]

	def init(self):

		self.reset()
		self._wreg(0x2A, 0x8D)
		self._wreg(0x2B, 0x3E)
		self._wreg(0x2D, 30)
		self._wreg(0x2C, 0)
		self._wreg(0x15, 0x40)
		self._wreg(0x11, 0x3D)
		self.antenna_on()

	def reset(self):
		self._wreg(0x01, 0x0F)

	def antenna_on(self, on=True):

		if on and ~(self._rreg(0x14) & 0x03):
			self._sflags(0x14, 0x03)
		else:
			self._cflags(0x14, 0x03)

	def request(self, mode):

		self._wreg(0x0D, 0x07)
		(stat, recv, bits) = self._tocard(0x0C, [mode])

		if (stat != self.OK) | (bits != 0x10):
			stat = self.ERR

		return stat, bits

	def anticoll(self):

		ser_chk = 0
		ser = [0x93, 0x20]

		self._wreg(0x0D, 0x00)

		(stat, recv, bits) = self._tocard(0x0C, ser)

		if stat == self.OK:
			if len(recv) == 5:
				for i in range(4):
					ser_chk = ser_chk ^ recv[i]
				if ser_chk != recv[4]:
					stat = self.ERR
			else:
				stat = self.ERR

		return stat, recv

	def select_tag(self, ser):

		buf = [0x93, 0x70] + ser[:5]
		buf += self._crc(buf)
		(stat, recv, bits) = self._tocard(0x0C, buf)
		return self.OK if (stat == self.OK) and (bits == 0x18) else self.ERR

	def auth(self, mode, addr, sect, ser):
		return self._tocard(0x0E, [mode, addr] + sect + ser[:4])[0]

	def stop_crypto1(self):
		self._cflags(0x08, 0x08)

	def read(self, addr):

		data = [0x30, addr]
		data += self._crc(data)
		(stat, recv, _) = self._tocard(0x0C, data)
		return recv if stat == self.OK else None

	def write(self, addr, data):

		buf = [0xA0, addr]
		buf += self._crc(buf)
		(stat, recv, bits) = self._tocard(0x0C, buf)

		if not (stat == self.OK) or not (bits == 4) or not ((recv[0] & 0x0F) == 0x0A):
			stat = self.ERR
		else:
			buf = []
			for i in range(16):
				buf.append(data[i])
			buf += self._crc(buf)
			(stat, recv, bits) = self._tocard(0x0C, buf)
			if not (stat == self.OK) or not (bits == 4) or not ((recv[0] & 0x0F) == 0x0A):
				stat = self.ERR

		return stat
    
	def lerCartao(self):
		(stat, tag_type) = self.request(self.REQIDL)
		saida = ""
		if stat == self.OK:
			(stat, raw_uid) = self.anticoll()
			if stat == self.OK:
				saida = "0x%02x%02x%02x%02x" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3]) 
		return saida
    
#Programa principal
fazerLeitura = 0

#Interrupção de tempo
def intTimer(sender):
  global fazerLeitura 
  fazerLeitura = 1  

#Configura a interrupção de tempo
timer_leitura = Timer(-1)
timer_leitura.init(period = 100, mode=Timer.PERIODIC, callback = intTimer)

#Cria um leitor
rdr = MFRC522_Custom(4, 15)

led = Pin(2, Pin.OUT)

while True:
  while True:
    led.value(1)
    time.sleep(0.1)
    led.value(0)
    time.sleep(0.1)
    if fazerLeitura == 1:
      fazerLeitura = 0
      dados = rdr.lerCartao()
      if dados != "":
        if dados != aux_dados:
          aux_dados = dados
          print(dados)
          pub_mqtt(dados)
        else:
          pass