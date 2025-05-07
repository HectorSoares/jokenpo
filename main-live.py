import cv2
import mediapipe as mp
import math
import esp32  # deve ter função moverRobo(status_str)

DIST_DEDO_FECHADO = 2
LARGURA_CAM = 640
ALTURA_CAM = 480

# Inicialização MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
detector_maos = mp_hands.Hands(max_num_hands=1)

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

def distancia_euclidiana(x1, y1, x2, y2):
    return round(math.sqrt((x2 - x1)**2 + (y2 - y1)**2))

def status_dedo(pontos, index):
    base = pontos[0]
    dedo = pontos[index]
    metacarpo = distancia_euclidiana(pontos[5][0], pontos[5][1], pontos[17][0], pontos[17][1])
    dist = distancia_euclidiana(base[0], base[1], dedo[0], dedo[1])
    razao = round(dist / metacarpo, 2)
    return int(razao >= DIST_DEDO_FECHADO)

def obter_status_dedos(pontos):
    return (
        status_dedo(pontos, 20),  # mínimo
        status_dedo(pontos, 16),  # anelar
        status_dedo(pontos, 12),  # médio
        status_dedo(pontos, 8),   # indicador
        0                         # polegar fixo em 0
    )

def main():
    cap = configurar_camera()
    ultimo_status = None

    while True:
        ret, img = cap.read()
        if not ret:
            break

        landmarks = detectar_mao(img)
        if landmarks:
            desenhar_pontos(img, landmarks)
            pontos = extrair_pontos(landmarks, img)
            status = obter_status_dedos(pontos)

            if status != ultimo_status:
                comando = ''.join(str(b) for b in status)
                esp32.moverRobo(comando)
                print(f"Enviado: {comando}")
                ultimo_status = status

        cv2.imshow("Controle do Robo", img)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
