def dispersao(lista):
    maximo = max(lista)
    minimo = min(lista)
    print(f"Amplitude = {maximo - minimo}")
    soma = 0
    for i in lista:
        soma+=i
    media = soma/len(lista)
    print(f"Média = {media}")
    soma = 0
    for i in lista:
        soma = (i-media)**2
    variancia = soma/len(lista)
    desv = variancia**(0.5)
    print(f"Variancia = {variancia}")
    print(f"desvio padrão = {desv}")



import mido
import random
import json

def carregar_eventos_midi_sem_colunas_repetidas(caminho_midi, colunas=4):
    mid = mido.MidiFile(caminho_midi)
    ticks_por_beat = mid.ticks_per_beat
    tempo_bpm = 120
    eventos = []
    tempo_atual = 0
    tempos_notas_ativas = {}

    for track in mid.tracks:
        for msg in track:
            tempo_atual += msg.time
            if msg.type == 'set_tempo':
                tempo_bpm = mido.tempo2bpm(msg.tempo)

    segundos_por_tick = 60 / (tempo_bpm * ticks_por_beat)
    tempo_atual = 0
    ultima_coluna = -1

    for track in mid.tracks:
        for msg in track:
            tempo_atual += msg.time
            tempo_s = tempo_atual * segundos_por_tick

            if msg.type == 'note_on' and msg.velocity > 0:
                tempos_notas_ativas[msg.note] = (tempo_s, msg.velocity)
            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                if msg.note in tempos_notas_ativas:
                    inicio_s, velocity = tempos_notas_ativas.pop(msg.note)
                    duracao = tempo_s - inicio_s
                    tentativa = msg.note % colunas
                    if tentativa == ultima_coluna:
                        outras_colunas = [i for i in range(colunas) if i != ultima_coluna]
                        tentativa = random.choice(outras_colunas)
                    coluna = tentativa
                    ultima_coluna = coluna

                    eventos.append({
                        'nota': msg.note,
                        'inicio': round(inicio_s, 3),
                        'duracao': round(duracao, 3),
                        'intensidade': velocity,
                        'coluna': coluna
                    })

    return sorted(eventos, key=lambda x: x['inicio'])

# Usar o caminho do seu .mid aqui
eventos = carregar_eventos_midi_sem_colunas_repetidas("Happy_Birthday.mid")

# vdd = True
# for e in eventos:
#     if e["intensidade"]!= 50:
#         vdd = False
# print(vdd)

# duracao = []
# for e in eventos:
#     duracao.append(e["duracao"])
# duracao.pop()
# dispersao(duracao)

# for e in eventos: 
#     print(f"Nota {e['nota']} | Início: {e['inicio']}s | Duração: {e['duracao']}s | Força: {e['intensidade']} | Coluna: {e['coluna']}")
# print(f"Número de notas: {len(eventos)}")

with open("notas.json", "w", encoding="utf-8") as f:
    json.dump(eventos, f, indent=2)
