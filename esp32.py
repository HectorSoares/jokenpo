import serial
import time

try:
    esp32 = serial.Serial('COM4', 115200, timeout=1)
    #time.sleep(2)  # Espera o Arduino resetar
except serial.SerialException:
    print("Erro: Não foi possível abrir a porta COM4.")
    exit()

def papel():
    cmd = 'PAPEL\n'
    esp32.write(cmd.encode())

def tesoura():
    cmd = 'TESOURA\n'
    esp32.write(cmd.encode())

def pedra():
    cmd = 'PEDRA\n'
    esp32.write(cmd.encode())

def moverRobo(gesto):
    cmd = gesto + '\n'
    esp32.write(cmd.encode())
