from math import sqrt
import math
import cv2
import mediapipe as mp
import random
from constantes import Gesto
import esp32

# --- Configurações gerais ---
MAX_FRAMES_PARADO = 10
MOVIMENTO_LIMIAR = 10
DIST_POLEGAR_FECHADO = 80
DIST_DEDO_FECHADO = 2
LARGURA_CAM = 640
ALTURA_CAM = 480
MODO_HARD = False

# --- Inicialização MediaPipe ---
hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
detector_maos = hands.Hands(max_num_hands=1)

def configurar_camera():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(3, LARGURA_CAM)
    cap.set(4, ALTURA_CAM)
    return cap

def detectar_mao_e_pontos(img):
    frame_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    resultados = detector_maos.process(frame_rgb)
    if resultados.multi_hand_landmarks:
        return resultados.multi_hand_landmarks
    return []

def extrair_pontos(landmarks, img):
    h, w, _ = img.shape
    pontos = []
    for ponto in landmarks.landmark:
        cx, cy = int(ponto.x * w), int(ponto.y * h)
        pontos.append((cx, cy))
    return pontos

def desenhar_pontos(img, landmarks):
    for l in landmarks:
        mp_drawing.draw_landmarks(img, l, hands.HAND_CONNECTIONS)

def classificar_dedos(pontos):
    minimo = status_dedo(pontos, 20)
    anelar = status_dedo(pontos, 16)
    medio = status_dedo(pontos, 12)
    indicador = status_dedo(pontos, 8)
    return minimo, anelar, medio, indicador

def classificar_gesto(minimo, anelar, medio, indicador):
    global MODO_HARD    
    if not minimo and not anelar and medio and not indicador:
        MODO_HARD = True
        return Gesto.DEDO_MEDIO
    elif not anelar and not minimo and not indicador and not medio:        
        return Gesto.PEDRA
    elif not anelar and not minimo and indicador and medio:        
        return Gesto.TESOURA
    elif anelar and minimo and indicador and medio:        
        return Gesto.PAPEL
    else:
        return Gesto.DESCONHECIDO

def distancia_euclidiana(x1, y1, x2, y2):
    distancia = round(math.sqrt((x2 - x1)**2 + (y2 - y1)**2))
    return distancia

def status_dedo(pontos, index):
    distancia = distancia_euclidiana(pontos[0][0],pontos[0][1],pontos[index][0],pontos[index][1])
    distancia_metacarpo = distancia_euclidiana(pontos[5][0],pontos[5][1],pontos[17][0],pontos[17][1])
    razao_distancia = round(distancia/distancia_metacarpo, 2)
    status = razao_distancia >= DIST_DEDO_FECHADO
    return int(status)

def gesto_maquina(gesto_jogador):
    global MODO_HARD
    if(MODO_HARD):
        return retorna_gesto_ganhador(gesto_jogador)
    return random.choice([Gesto.PEDRA, Gesto.PAPEL, Gesto.TESOURA])

def retorna_gesto_ganhador(gesto):
    if gesto == Gesto.PEDRA:
        return Gesto.PAPEL
    elif gesto == Gesto.PAPEL:
        return Gesto.TESOURA
    elif gesto == Gesto.TESOURA:
        return Gesto.PEDRA
    else: return Gesto.DEDO_MEDIO    

def comparar(gesto_jogador, gesto_bot):
    if gesto_jogador == gesto_bot:
        return "EMPATE"
    elif (retorna_gesto_ganhador(gesto_bot) == gesto_jogador):
        return "VOCE GANHOU!"
    else:
        return "MAQUINA GANHOU!"

# --- Execução principal ---
def main():
    cap = configurar_camera()
    x_prev = None
    movendo = False
    frames_parado = 0
    ultimo_gesto = ""
    gesto_bot = ""
    resultado = ""

    while True:
        success, img = cap.read()
        if not success:
            break

        landmarks = detectar_mao_e_pontos(img)
        if landmarks:
            desenhar_pontos(img, landmarks)
            pontos = extrair_pontos(landmarks[0], img)
            if pontos:
                x_atual = pontos[0][0]
                if x_prev is not None:
                    deslocamento = abs(x_atual - x_prev)
                    if deslocamento > MOVIMENTO_LIMIAR:
                        movendo = True
                        frames_parado = 0
                    elif movendo:
                        frames_parado += 1
                        if frames_parado > MAX_FRAMES_PARADO:            
                            minimo, anelar, medio, indicador = classificar_dedos(pontos)   
                            gesto_jogador = classificar_gesto(minimo, anelar, medio, indicador)
                            if gesto_jogador != Gesto.DESCONHECIDO:
                                gesto_bot = gesto_maquina(gesto_jogador)
                                esp32.moverRobo(gesto_bot.value)
                                resultado = comparar(gesto_jogador, gesto_bot)
                                print(f"Voce: {gesto_jogador} | Maquina: {gesto_bot} → {resultado}")
                                ultimo_gesto = gesto_jogador
                            movendo = False
                            frames_parado = 0
                x_prev = x_atual

        # Mostrar resultado na tela
        if ultimo_gesto:
            cv2.putText(img, f"Voce: {ultimo_gesto}", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(img, f"Maquina: {gesto_bot}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 230, 255), 2)
            cv2.putText(img, f"{resultado}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 50, 255), 3)
        
        cv2.imshow('Pedra Papel Tesoura', img)
        if cv2.waitKey(1) & 0xFF == 27:  # Tecla ESC para sair
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
