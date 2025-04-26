
import pygame

from constantes import Gesto
# Cores
COR_LIGADO = (0, 255, 0)  
COR_HARD = (255, 0, 0) # Vermelho
COR_DESLIGADO = (150, 150, 150)  # Cinza
COR_FUNDO = (30, 30, 30)

# Tela
LARGURA, ALTURA = 600, 300
pygame.init()
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Mão Robótica - Pygame")

# Posições dos dedos (círculos)
posicoes_dedos = [(100 + i * 90, 100) for i in range(5)]
estados_dedos = [0, 0, 0, 0, 0]  # Todos desligados inicialmente

def atualizar_mao(polegar, indicador, medio, anelar, minimo):
    global estados_dedos
    estados_dedos = [polegar, indicador, medio, anelar, minimo]

def mover_robo(gesto):
    if gesto == Gesto.PEDRA:
        atualizar_mao(0, 0, 0, 0, 0)
    elif gesto == Gesto.PAPEL:
        atualizar_mao(1, 1, 1, 1, 1)
    elif gesto == Gesto.TESOURA:
        atualizar_mao(0, 1, 1, 0, 0)
    elif gesto == Gesto.DEDO_MEDIO:
        atualizar_mao(0, 0, 1, 0, 0)
    else:
        atualizar_mao(0, 0, 0, 0, 0)

def desenhar_interface():
    tela.fill(COR_FUNDO)
    for i, (x, y) in enumerate(posicoes_dedos):
        cor = COR_LIGADO if estados_dedos[i] else COR_DESLIGADO
        pygame.draw.circle(tela, cor, (x, y), 30)
    pygame.display.flip()

def atualizar_tela(hard):
    if hard:
        global COR_LIGADO
        COR_LIGADO = COR_HARD
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            exit()
    desenhar_interface()
