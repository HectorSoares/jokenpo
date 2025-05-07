from enum import Enum

# --- Enums para gestos e modos ---
class Gesto(Enum):
    PEDRA = [0,0,0,0,0]
    PAPEL = [1,1,1,1,1]
    TESOURA = [0,0,1,1,0]
    DESCONHECIDO = [1,0,0,0,1]
    DEDO_MEDIO = [0,0,1,0,0]
