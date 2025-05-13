import cv2
import mediapipe as mp
import math
import time
import esp32  # deve ter função moverRobo(status_str)

DIST_DEDO_FECHADO = 2
DIST_DEDAO_FECHADO = 1.5
LARGURA_CAM = 640
ALTURA_CAM = 480

# Inicialização MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
detector_maos = mp_hands.Hands(max_num_hands=1)

# Definição dos modos
MODOS = ["controle_robo", "jogo_pedra_papel_tesoura"]
modo_atual = MODOS[0]  # Inicia com o modo de controle do robô

# Configuração para detecção de gestos
GESTOS_RECONHECIDOS = ["PEDRA", "PAPEL", "TESOURA"]
ultima_sequencia = []
tempo_ultimo_gesto = 0
intervalo_tempo = 5  # segundos para considerar uma nova sequência
valor_minimo = 3
valor_maximo = 0
gesto_anterior = []

def configurar_camera():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(3, LARGURA_CAM)
    cap.set(4, ALTURA_CAM)
    return cap

def detectar_mao(img):
    frame_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    resultados = detector_maos.process(frame_rgb)
    if resultados.multi_hand_landmarks:
        return resultados.multi_hand_landmarks[0]
    return None

def extrair_pontos(landmarks, img):
    h, w, _ = img.shape
    return [(int(pt.x * w), int(pt.y * h)) for pt in landmarks.landmark]

def desenhar_pontos(img, landmarks):
    mp_drawing.draw_landmarks(img, landmarks, mp_hands.HAND_CONNECTIONS)

def distancia_euclidiana(x, y):
    return round(math.sqrt((x[0] - y[0])**2 + (x[1] - y[1])**2))

def status_dedo(pontos, index, dedao = False):
    global valor_maximo, valor_minimo
    base = pontos[0 if not dedao else 17]
    dedo = pontos[index]
    metacarpo = distancia_euclidiana(pontos[5], pontos[17])
    dist = distancia_euclidiana(base, dedo)
    razao = round(dist / metacarpo, 2)
    return int(razao >= (DIST_DEDO_FECHADO if not dedao else DIST_DEDAO_FECHADO))

def obter_status_dedos(pontos):
    return (
        status_dedo(pontos, 20),  # mínimo
        status_dedo(pontos, 16),  # anelar
        status_dedo(pontos, 12),  # médio
        status_dedo(pontos, 8),   # indicador
        status_dedo(pontos, 4, True)   # polegar fixo em 0
    )

def classificar_gesto(minimo, anelar, medio, indicador):
    if not minimo and not anelar and medio and not indicador:
        return "PEDRA"
    elif anelar and minimo and indicador and medio:
        return "PAPEL"
    elif not anelar and not minimo and indicador and medio:
        return "TESOURA"
    else:
        return "DESCONHECIDO"

def alternar_modo():
    global modo_atual
    if modo_atual == MODOS[0]:
        modo_atual = MODOS[1]
        print("Modo alterado para: Jogo Pedra, Papel e Tesoura")
    else:
        modo_atual = MODOS[0]
        print("Modo alterado para: Controle do Robô")

def main():
    global ultima_sequencia, tempo_ultimo_gesto, gesto_anterior
    cap = configurar_camera()

    while True:
        
        ret, img = cap.read()
        if not ret:
            break

        landmarks = detectar_mao(img)
        if landmarks:
            desenhar_pontos(img, landmarks)
            pontos = extrair_pontos(landmarks, img)
            status = obter_status_dedos(pontos)
            if(gesto_anterior != status):
                gesto_anterior = status
                if modo_atual == MODOS[0]:  # Modo Controle do Robô
                    comando = ''.join(str(b) for b in status)
                    esp32.moverRobo(comando)

                else:  # Modo Jogo Pedra, Papel, Tesoura
                    gesto = classificar_gesto(*status)
                    if gesto != "DESCONHECIDO":
                        agora = time.time()

                        if agora - tempo_ultimo_gesto <= intervalo_tempo:  # Sequência no intervalo
                            ultima_sequencia.append(gesto)
                            if len(ultima_sequencia) == 3:
                                if ultima_sequencia == ["PEDRA", "PAPEL", "TESOURA"]:
                                    alternar_modo()
                                ultima_sequencia = []
                        else:  # Reiniciar sequência após timeout
                            ultima_sequencia = [gesto]

                        tempo_ultimo_gesto = agora

        cv2.imshow("Controle do Robo", img)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
