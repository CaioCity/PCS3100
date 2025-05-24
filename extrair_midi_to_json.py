import mido
import random
import json

def dispersao(parametro : str, eventos : list):

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
        if grupos[i][0]['coluna'] == coluna_anterior:
            grupos[i][0]['coluna'] = (coluna_anterior+2)%4
        coluna_anterior = grupos[i][0]['coluna']
    
    return grupos


def agrupar_notas(eventos : list):
    i_lista = 0
    inicio = None
    eventos_agrupados = []

    for i in range(0,len(eventos)):
        if eventos[i]['inicio'] == inicio:
            eventos_agrupados[i_lista].append(eventos[i])
        else: 
            eventos_agrupados.append([])
            eventos_agrupados[i_lista].append(eventos[i])
            inicio = eventos[i]['inicio']
            i_lista+=1
    
    return reoganizar_colunas(eventos_agrupados)


def regular_comprimento(eventos : list):
    # O comprimento a ser regulado nao eh o comprimento de onda da nota
    # Trata-se do comprimento da nota a ser gerada na interface gráfica do jogo
    duracao_media = 0
    for e in eventos:
        duracao_media += e["duracao"]
    duracao_media/=len(eventos)

    for e in eventos:
        e["M_altura"] = e["duracao"]/duracao_media


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
                    tentativa = (msg.note  + random.randint(0, colunas-1)) % colunas
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


def printar_eventos(eventos):
    for e in eventos: 
        print(f"Nota {e['nota']} | Início: {e['inicio']}s | Duração: {e['duracao']}s | Força: {e['intensidade']} | Coluna: {e['coluna']}")
    print(f"Número de notas: {len(eventos)}")


# Usar o caminho do seu .mid aqui
eventos = carregar_eventos_midi_sem_colunas_repetidas("Happy_Birthday.mid")

for e in eventos:
    e["intensidade"] = 127

# dispersao("intensidade", eventos)

regular_comprimento(eventos)

# printar_eventos(eventos)

agrupamentos = agrupar_notas(eventos)
# print(f"Número de grupos: {len(agrupamentos)}")

with open("notas.json", "w", encoding="utf-8") as f:
    json.dump(agrupamentos, f, indent=2)
