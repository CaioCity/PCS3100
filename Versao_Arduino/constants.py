import pygame


NOME_JOGO =  "PoliTiles"
LARGURA_TELA, ALTURA_TELA = 460, 600
ALTURA_LINHA_ACERTO = ALTURA_TELA - 100
STATUS_LEDS = True
MAX_ERROS = 5
PATH_DB = "DB.json"
PATH_NOTAS_JSON = "notas.json"
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
FONTE_MUITO_PEQUENA = pygame.font.SysFont("Algerian", 16)
FONTE_PEQUENA = pygame.font.SysFont("Algerian", 20)
FONTE = pygame.font.SysFont("Algerian", 24)
FONTE_GRANDE = pygame.font.SysFont("Algerian", 36)

# Imagens
PATH_IMAGEM_FUNDO_PRINCIPAL = "fundo.jpeg"

# Colunas e teclas
N_COLUNAS = 4
LARGURA_COLUNA = LARGURA_TELA // N_COLUNAS
TECLAS = [pygame.K_q, pygame.K_w, pygame.K_e, pygame.K_r]

# Sons
NOTA_VOLUME = 0.5
EFEITOS_SONOROS_VOLUME = 0.25
MUSICA_FUNDO_VOLUME = 0.25
pygame.mixer.init()
SONS = [
    pygame.mixer.Sound('Sons/piano1.wav'),
    pygame.mixer.Sound('Sons/piano2.wav'),
    pygame.mixer.Sound('Sons/piano3.wav'),
    pygame.mixer.Sound('Sons/piano4.wav')
] # Gerar um "som ao toque" para os botões no menu
PATH_MUSICA_FUNDO = 'Sons/moonlight-sonata-classical-piano-beethoven.mp3'

# Botoes Arduino
BOT_VERMELHO = "VERMELHO"
BOT_AMARELO = "AMARELO"
BOT_AZUL = "AZUL"
BOT_VERDE = "VERDE"
BOT_PRETO = "PRETO" 
BOTOES = [BOT_VERMELHO, BOT_AMARELO, BOT_AZUL, BOT_VERDE, BOT_PRETO]
