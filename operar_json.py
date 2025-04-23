import pygame
import pygame.midi
import json

# Inicializa pygame e MIDI
pygame.init()
pygame.midi.init()
screen = pygame.display.set_mode((640, 480))
clock = pygame.time.Clock()

player = pygame.midi.Output(pygame.midi.get_default_output_id())
player.set_instrument(0)

# Carrega as notas
with open("notas.json", "r") as f:
    notas = json.load(f)

# Variáveis de controle
start_ticks = pygame.time.get_ticks()
nota_index = 0
notas_tocando = []  # lista de notas ativas com seus tempos de desligar

running = True
while running:
    now = pygame.time.get_ticks() - start_ticks  # tempo atual em ms
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Tocar nova nota se for hora
    while nota_index < len(notas):
        nota = notas[nota_index]
        inicio_ms = int(nota[0]["inicio"] * 1000)

        if now >= inicio_ms:
            player.note_on(nota[0]["nota"], nota[0]["intensidade"])
            fim_nota = now + int(nota[0]["duracao"] * 1000)
            notas_tocando.append((nota[0]["nota"], nota[0]["intensidade"], fim_nota))
            nota_index += 1
        else:
            break  # espera o momento certo

    # Desliga notas que passaram do tempo
    for nota in notas_tocando[:]:
        if now >= nota[2]:
            player.note_off(nota[0], nota[1])
            notas_tocando.remove(nota)

    # Aqui você pode desenhar as colunas e blocos caindo com base em nota["coluna"]

    pygame.display.flip()
    clock.tick(60)

# Encerramento
del player
pygame.midi.quit()
pygame.quit()
