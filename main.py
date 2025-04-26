from math import sqrt
import math
import cv2
import mediapipe as mp
import random
from interface_pygame import atualizar_tela, mover_robo
from constantes import Gesto

# --- Configurações gerais ---
MAX_FRAMES_PARADO = 10
MOVIMENTO_LIMIAR = 10
DIST_POLEGAR_FECHADO = 80
DIST_DEDO_FECHADO = 70
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

def classificar_gesto(pontos):
    global MODO_HARD    

    dist_indicador = distancia_euclidiana(pontos[0][0],pontos[0][1],pontos[8][0],pontos[8][1])
    dist_medio = distancia_euclidiana(pontos[0][0],pontos[0][1],pontos[12][0],pontos[12][1])
    dist_anelar = distancia_euclidiana(pontos[0][0],pontos[0][1],pontos[16][0],pontos[16][1])
    dist_minimo = distancia_euclidiana(pontos[0][0],pontos[0][1],pontos[20][0],pontos[20][1])

    minimo_fechado = dist_minimo <= DIST_DEDO_FECHADO
    anelar_fechado = dist_anelar <= DIST_DEDO_FECHADO
    indicador_fechado = dist_indicador <= DIST_DEDO_FECHADO
    medio_fechado = dist_medio <= DIST_DEDO_FECHADO


    if minimo_fechado and anelar_fechado and not medio_fechado and indicador_fechado:
        MODO_HARD = True
        return Gesto.DEDO_MEDIO
    elif anelar_fechado and minimo_fechado and indicador_fechado and medio_fechado:
        return Gesto.PEDRA
    elif anelar_fechado and minimo_fechado and not indicador_fechado and not medio_fechado:
        return Gesto.TESOURA
    elif not anelar_fechado and not minimo_fechado and not indicador_fechado and not medio_fechado:
        return Gesto.PAPEL
    else:
        return Gesto.DESCONHECIDO

def distancia_euclidiana(x1, y1, x2, y2):
    distancia = round(math.sqrt((x2 - x1)**2 + (y2 - y1)**2))
    return distancia

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
    elif (gesto_jogador == Gesto.PEDRA and gesto_bot == Gesto.TESOURA) or \
         (gesto_jogador == Gesto.TESOURA and gesto_bot == Gesto.PAPEL) or \
         (gesto_jogador == Gesto.PAPEL and gesto_bot == Gesto.PEDRA):
        return "VOCE GANHOU!"
    else:
        return "MAQUINA GANHOU!"

# --- Execução principal ---
def main():
    cap = configurar_camera()
    prevX = None
    movendo = False
    framesParado = 0
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
            ind = distancia_euclidiana(pontos[8][0],pontos[8][1],pontos[0][0],pontos[0][1])
            print(ind)
            if pontos:
                x_atual = pontos[0][0]
                if prevX is not None:
                    deslocamento = abs(x_atual - prevX)
                    if deslocamento > MOVIMENTO_LIMIAR:
                        movendo = True
                        framesParado = 0
                    elif movendo:
                        framesParado += 1
                        if framesParado > MAX_FRAMES_PARADO:
                            
                            gesto_jogador = classificar_gesto(pontos)
                            if gesto_jogador != Gesto.DESCONHECIDO:
                                print(MODO_HARD)
                                gesto_bot = gesto_maquina(gesto_jogador)
                                mover_robo(gesto_bot);
                                resultado = comparar(gesto_jogador, gesto_bot)
                                print(f"Voce: {gesto_jogador} | Maquina: {gesto_bot} → {resultado}")
                                ultimo_gesto = gesto_jogador
                            movendo = False
                            framesParado = 0
                prevX = x_atual

        # Mostrar resultado na tela
        if ultimo_gesto:
            cv2.putText(img, f"Voce: {ultimo_gesto}", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(img, f"Maquina: {gesto_bot}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 230, 255), 2)
            cv2.putText(img, f"{resultado}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 50, 255), 3)
        
        atualizar_tela(MODO_HARD)
        cv2.imshow('Pedra Papel Tesoura', img)
        if cv2.waitKey(1) & 0xFF == 27:  # Tecla ESC para sair
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
