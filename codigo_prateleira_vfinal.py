import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import sys
from time import sleep
import requests

#################################################configs###################################
stepPin = 2
dirPin = 3
GPIO.setmode(GPIO.BCM)
GPIO.setup(stepPin, GPIO.OUT)
GPIO.setup(dirPin, GPIO.OUT)
#liga pino GPIO.output(pino,1 ou 0)
pulsos = 0
i=0
passos = 55
Broker = "192.168.0.34"
Porta = 1883
Ka = 60
TopicoSubscribe = "robo1"
client = mqtt.Client()
recebido = ''
conexao = ''
pedido = []
pedidos = [0]
acao = ''
id_user = 0
qtd_desejada = 0
sem_pedidos = 0
ultimo_pedido = ''
############################################funcoes#############################################
def checar_pedidos():
    global pedido, pedidos, ultimo_pedido
    if not pedidos:
        pedidos.append(0)
    r = requests.get('http://tcc-entregas.onlinewebshop.net/views/esp.php')
    #print(r.content)
    if not r.content:
        print('Sem pedidos')
    elif r.content:
        x = str(r.content)
        x = x[2:(len(x)-1)]
        pedido = x.split(",")
    if pedido:
        if pedido != ultimo_pedido:
            ultimo_pedido = pedido
            #print(pedido)
            pedido_final = len(pedidos)
            #print(ultimo_pedido)
            if pedido != pedidos[(pedido_final)-1]:
                print("Novo Pedido adicionado a fila!")
                pedidos.append(pedido)
                print(pedidos)
                if pedidos[0] == 0:
                    del(pedidos[0])
                else:
                    pass
            else:
                pass
def liga_motor():
    global pulsos, passos, qtd_desejada, id_user
    x = requests.get('http://tcc-entregas.onlinewebshop.net/views/esp.php?idu='+str(id_user)+'&sta=2')
    for i in range((passos*qtd_desejada)):
        GPIO.output(dirPin,0)
        GPIO.output(stepPin,1)
        sleep(0.01)
        GPIO.output(stepPin,0)
        sleep(0.01)
        pulsos +=1
    if pulsos >=110:
        pulsos = 0
        for j in range(110):
            GPIO.output(dirPin,1)
            GPIO.output(stepPin,1)
            sleep(0.01)
            GPIO.output(stepPin,0)
            sleep(0.01) 
#Callback - conexao ao broker realizada
def connect(client, userdata, flags, rc):
    print("[STATUS] Conectado ao Broker.")
    #subscribe no topico
    client.subscribe(TopicoSubscribe)
#Callback - mensagem recebida do broker
def mnsg(client, userdata, msg):
    global conexao, acao
    MensagemRecebida = str(msg.payload)
    recebido = MensagemRecebida[2:((len(MensagemRecebida)-1))]
    conexao = recebido
    print(conexao)
    if conexao == '0xda1a9691':
        acao = 'esperando'
    elif conexao == '0x7e772623':
        acao = ''
        liga_motor()
        client.publish("robo1", "seguir")
    elif conexao == '0x7a307490':
        acao = 'aguardando'
    else:
        pass   


def conexao_mqtt():
    global client
    print("[STATUS] Inicializando MQTT...")
    #inicializa MQTT:
    client.on_connect = connect
    client.connect(Broker, Porta, Ka)
    client.loop_start()

conexao_mqtt()

def checar_msngs():
    global client
    client.on_message = mnsg


while True:
    checar_pedidos()
    checar_msngs()
    print(pedidos)
    if not pedidos or pedidos == [0]:
        sem_pedidos = +1
    else:
        sem_pedidos = 0
    
    if sem_pedidos == 0 and acao == 'esperando':
        id_user = int(pedidos[0][1])
        qtd_desejada = int(pedidos[0][3])
        sleep(0.5)
        client.publish("robo1", "seguir") 
    elif acao == 'aguardando':
        x = requests.get('http://tcc-entregas.onlinewebshop.net/views/esp.php?idu='+str(id_user)+'&sta=3')
        del(pedidos[0])
        sleep(1)
        client.publish("robo1", "seguir")