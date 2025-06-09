import json
import os

# Caminho do arquivo JSON
DB_FILE = "DB.json"

# Verifica se o arquivo já existe; se não, cria com um dicionário vazio
if not os.path.exists(DB_FILE):
    with open(DB_FILE, 'w') as f:
        json.dump({}, f, indent=4)


def adicionar_musica(nome, arquivo):
    with open(DB_FILE, 'r') as f:
        dados = json.load(f)

    dados[len(dados)] = {
        "nome": nome,
        "arquivo": arquivo,
        "recorde": 0
    }

    with open(DB_FILE, 'w') as f:
        json.dump(dados, f, indent=4)


def obter_nome_musica(numero):
    with open(DB_FILE, 'r') as f:
        dados = json.load(f)

    chave = str(numero) 
    if chave in dados:
        return dados[chave]["nome"]
    return None


def obter_recorde_musica(numero : int):
    with open(DB_FILE, 'r') as f:
        dados = json.load(f)

    chave = str(numero) 
    if chave in dados:
        return dados[chave]["recorde"]
    return None


def obter_arquivo_musica(numero : int):
    with open(DB_FILE, 'r') as f:
        dados = json.load(f)

    chave = str(numero) 
    if chave in dados:
        return dados[chave]["arquivo"]
    return None


def obter_titulos():
    with open(DB_FILE, 'r') as f:
        dados = json.load(f)

    titulos = []
    for numero in sorted(dados, key=lambda x: int(x)):  # ordena por número
        titulos.append(dados[numero]["nome"])

    return titulos


def atualizar_recorde(musica, pontuacao):
    with open(DB_FILE, 'r') as f:
        dados = json.load(f)

    chave = str(musica)
    if chave in dados:
        dados[chave]['recorde'] = pontuacao
        with open(DB_FILE, 'w') as f:
            json.dump(dados, f, indent=4)


def obter_lista_recordes():
    with open(DB_FILE, 'r') as f:
        dados = json.load(f)

    recordes = []
    for numero in sorted(dados, key=lambda x: int(x)):  # garante ordem numérica
        recordes.append(dados[numero]["recorde"])

    return recordes

def resetar_recordes():
    with open(DB_FILE, 'r') as f:
        dados = json.load(f)

    for musica in dados.values():
        musica["recorde"] = 0  # zera o recorde

    with open(DB_FILE, 'w') as f:
        json.dump(dados, f, indent=4)

