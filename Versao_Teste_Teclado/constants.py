import pygame


NOME_JOGO =  "PoliTiles"
LARGURA_TELA, ALTURA_TELA = 460, 600
ALTURA_LINHA_ACERTO = ALTURA_TELA - 100
MAX_ERROS = 5
PATH_MUSICA_DEFAULT = "Happy_Birthday.mid"
FPS = 60

# Cores
MARROM = (176, 106, 0)
PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)
AZUL = (65, 132, 233)
BEGE = (220,220,150)
VERMELHO = (200, 50, 50)
VERDE = (0, 200, 0)
CINZA = (100, 100, 100)
AMARELO = (255, 255, 0)

# Fontes
pygame.font.init()
FONTE_PEQUENA = pygame.font.SysFont("Algerian", 20)
FONTE = pygame.font.SysFont("Algerian", 24)
FONTE_GRANDE = pygame.font.SysFont("Algerian", 36)
ARIAL20 = pygame.font.SysFont("Arial", 20)

# Imagens
PATH_IMAGEM_FUNDO_PRINCIPAL = "fundo.jpeg"

# Colunas e teclas
N_COLUNAS = 4
LARGURA_COLUNA = LARGURA_TELA // N_COLUNAS
TECLAS = [pygame.K_q, pygame.K_w, pygame.K_e, pygame.K_r]

# Sons
NOTA_VOLUME = 0.5
EFEITOS_SONOROS_VOLUME = 0.10
MUSICA_FUNDO_VOLUME = 0.10
pygame.mixer.init()
SONS = [
    pygame.mixer.Sound('piano1.wav'),
    pygame.mixer.Sound('piano2.wav'),
    pygame.mixer.Sound('piano3.wav'),
    pygame.mixer.Sound('piano4.wav')
] # Gerar um "som ao toque" para os botões no menu
PATH_MUSICA_FUNDO = 'moonlight-sonata-classical-piano-beethoven.mp3'