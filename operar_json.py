import pygame.midi
import json
import time

# Inicializa pygame e módulo midi
pygame.init()
pygame.midi.init()

# Abre o dispositivo MIDI padrão
player = pygame.midi.Output(pygame.midi.get_default_output_id())

# Define o instrumento (0 = piano)
player.set_instrument(0)

# Carrega notas do JSON
with open("notas_Happy_Birthday.json", "r") as f:
    notas = json.load(f)

def tocar_nota_por_index(index):
    # if index < 0 or index >= len(notas):
    #     print("Índice fora do intervalo!")
    #     return

    nota_info = notas[index]
    
    nota = nota_info["nota"]
    duracao = nota_info["duracao"]
    intensidade = nota_info.get("intensidade", 100)

    # print(f"Tocando nota {nota} | Duração: {duracao}s | Intensidade: {intensidade}")

    player.note_on(nota, intensidade)
    time.sleep(duracao)
    player.note_off(nota, intensidade)

# Exemplo: Tocar todas as notas
for j in range(100):
    for i in range(len(notas)):
        tocar_nota_por_index(i)

# Finaliza o MIDI
del player
pygame.midi.quit()
pygame.quit()
