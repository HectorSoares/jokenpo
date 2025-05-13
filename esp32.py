import serial
import time

try:
    esp32 = serial.Serial('COM4', 115200, timeout=1)
    #time.sleep(2)  # Espera o Arduino resetar
except serial.SerialException:
    print("Erro: Não foi possível abrir a porta COM4.")
    exit()

def moverRobo(status_dedos):
    comando = ''.join(str(d) for d in status_dedos) + '\n'
    print(comando)
    esp32.write(comando.encode())
    esp32.flush()
