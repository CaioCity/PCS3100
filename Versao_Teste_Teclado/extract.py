import mido
import random
import json
from constants import PATH_NOTAS_JSON

def dispersao(parametro : str, eventos : list):
    # Utilizada para Debug e Analise

    lista = []
    for e in eventos:
        lista.append(e[parametro])

    maximo = max(lista)
    minimo = min(lista)
    soma = sum(lista)
    media = soma/len(lista)
    
    soma = 0
    for i in lista:
        soma = (i-media)**2

    variancia = soma/len(lista)
    desv = variancia**(0.5)

    print(f"Dispersão de {parametro}:")
    print(f"Amplitude = {maximo - minimo}")
    print(f"Média = {media}")
    print(f"Variancia = {variancia}")
    print(f"desvio padrão = {desv}")

def reoganizar_colunas(grupos : list):
    coluna_anterior = grupos[0][0]['coluna']

    for i in range(1,len(grupos)):
        while grupos[i][0]['coluna'] == coluna_anterior:
            grupos[i][0]['coluna'] = (coluna_anterior + random.randint(1,4))%4
        coluna_anterior = grupos[i][0]['coluna']
    
    return grupos

def agrupar_notas(eventos : list):
    i_lista = 0
    inicio = eventos[0]['inicio']
    eventos_agrupados = [[eventos[0]]]

    for i in range(1,len(eventos)):
        if eventos[i]['inicio'] == inicio:
            eventos_agrupados[i_lista].append(eventos[i])
        else: 
            eventos_agrupados.append([])
            i_lista+=1
            eventos_agrupados[i_lista].append(eventos[i])
            inicio = eventos[i]['inicio']

    return reoganizar_colunas(eventos_agrupados)

def printar_eventos(eventos : list):
    # Utilizada para Debug e Analise
    for e in eventos: 
        print(f"Nota {e['nota']} | Início: {e['inicio']}s | Duração: {e['duracao']}s | Força: {e['intensidade']} | Coluna: {e['coluna']}")
    print(f"Número de notas: {len(eventos)}")

def carregar_eventos_midi(caminho_midi, colunas = 4):
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
                    coluna = (msg.note  + random.randint(0, colunas-1)) % colunas

                    eventos.append({
                        'nota': msg.note,
                        'inicio': round(inicio_s, 3),
                        'duracao': round(duracao, 3),
                        'intensidade': velocity,
                        'coluna': coluna
                    })

    return sorted(eventos, key=lambda x: x['inicio'])

def mid_to_json(file_name):
    # Usar o caminho do seu .mid aqui
    eventos = carregar_eventos_midi(file_name)

    for e in eventos:
        e["intensidade"] = 127

    agrupamentos = agrupar_notas(eventos)

    with open(PATH_NOTAS_JSON, "w", encoding="utf-8") as f:
        json.dump(agrupamentos, f, indent=2)
