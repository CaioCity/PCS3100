import json
import os
from constants import PATH_DB 

# Verifica se o arquivo já existe; se não, cria com um dicionário vazio
if not os.path.exists(PATH_DB):
    with open(PATH_DB, 'w') as f:
        json.dump({}, f, indent=4)


def adicionar_musica(nome : str, arquivo : str):
    with open(PATH_DB, 'r') as f:
        dados = json.load(f)

    dados[len(dados)] = {
        "nome": nome,
        "arquivo": "sons/" + arquivo,
        "recorde": 0
    }

    with open(PATH_DB, 'w') as f:
        json.dump(dados, f, indent=4)


def remover_musica(indice_para_remover : int):
    try:
        # Carrega os dados do JSON
        with open(PATH_DB, 'r', encoding='utf-8') as f:
            dados = json.load(f)

        # Converte para uma lista ordenada de entradas (valores), ignorando as chaves originais
        lista_entradas = [dados[chave] for chave in sorted(dados, key=lambda x: int(x))]

        # Verifica se o índice a ser removido é válido
        if 0 <= indice_para_remover < len(lista_entradas):
            removido = lista_entradas.pop(indice_para_remover)
            print(f"Entrada removida: {removido}")
        else:
            print(f"Índice {indice_para_remover} fora do intervalo.")
            return

        # Recria o dicionário com os índices corrigidos
        dados_reindexados = {str(i): entrada for i, entrada in enumerate(lista_entradas)}

        # Salva novamente o arquivo
        with open(PATH_DB, 'w', encoding='utf-8') as f:
            json.dump(dados_reindexados, f, indent=4, ensure_ascii=False)
    except FileNotFoundError:
        print(f"Arquivo '{PATH_DB}' não encontrado.")
    except json.JSONDecodeError:
        print("Erro ao decodificar o JSON.")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")


def obter_nome_musica(numero : int):
    with open(PATH_DB, 'r') as f:
        dados = json.load(f)

    chave = str(numero) 
    if chave in dados:
        return dados[chave]["nome"]
    return None


def obter_recorde_musica(numero : int):
    with open(PATH_DB, 'r') as f:
        dados = json.load(f)

    chave = str(numero) 
    if chave in dados:
        return dados[chave]["recorde"]
    return None


def obter_arquivo_musica(numero : int):
    with open(PATH_DB, 'r') as f:
        dados = json.load(f)

    chave = str(numero) 
    if chave in dados:
        return dados[chave]["arquivo"]
    return None


def obter_titulos():
    with open(PATH_DB, 'r') as f:
        dados = json.load(f)

    titulos = []
    for numero in sorted(dados, key=lambda x: int(x)):  # ordena por número
        titulos.append(dados[numero]["nome"])

    return titulos


def atualizar_recorde(numero : int, pontuacao : int):
    with open(PATH_DB, 'r') as f:
        dados = json.load(f)

    chave = str(numero)
    if chave in dados:
        dados[chave]['recorde'] = pontuacao
        with open(PATH_DB, 'w') as f:
            json.dump(dados, f, indent=4)


def obter_lista_recordes():
    with open(PATH_DB, 'r') as f:
        dados = json.load(f)

    recordes = []
    for numero in sorted(dados, key=lambda x: int(x)):  # garante ordem numérica
        recordes.append(dados[numero]["recorde"])

    return recordes

def resetar_recordes():
    with open(PATH_DB, 'r') as f:
        dados = json.load(f)

    for musica in dados.values():
        musica["recorde"] = 0  # zera o recorde

    with open(PATH_DB, 'w') as f:
        json.dump(dados, f, indent=4)
from constants import PATH_DB 

# Verifica se o arquivo já existe; se não, cria com um dicionário vazio
if not os.path.exists(PATH_DB):
    with open(PATH_DB, 'w') as f:
        json.dump({}, f, indent=4)


def adicionar_musica(nome : str, arquivo : str):
    with open(PATH_DB, 'r') as f:
        dados = json.load(f)

    dados[len(dados)] = {
        "nome": nome,
        "arquivo": arquivo,
        "recorde": 0
    }

    with open(PATH_DB, 'w') as f:
        json.dump(dados, f, indent=4)


def remover_musica(indice_para_remover : int):
    try:
        # Carrega os dados do JSON
        with open(PATH_DB, 'r', encoding='utf-8') as f:
            dados = json.load(f)

        # Converte para uma lista ordenada de entradas (valores), ignorando as chaves originais
        lista_entradas = [dados[chave] for chave in sorted(dados, key=lambda x: int(x))]

        # Verifica se o índice a ser removido é válido
        if 0 <= indice_para_remover < len(lista_entradas):
            removido = lista_entradas.pop(indice_para_remover)
            print(f"Entrada removida: {removido}")
        else:
            print(f"Índice {indice_para_remover} fora do intervalo.")
            return

        # Recria o dicionário com os índices corrigidos
        dados_reindexados = {str(i): entrada for i, entrada in enumerate(lista_entradas)}

        # Salva novamente o arquivo
        with open(PATH_DB, 'w', encoding='utf-8') as f:
            json.dump(dados_reindexados, f, indent=4, ensure_ascii=False)
    except FileNotFoundError:
        print(f"Arquivo '{PATH_DB}' não encontrado.")
    except json.JSONDecodeError:
        print("Erro ao decodificar o JSON.")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")


def obter_nome_musica(numero : int):
    with open(PATH_DB, 'r') as f:
        dados = json.load(f)

    chave = str(numero) 
    if chave in dados:
        return dados[chave]["nome"]
    return None


def obter_recorde_musica(numero : int):
    with open(PATH_DB, 'r') as f:
        dados = json.load(f)

    chave = str(numero) 
    if chave in dados:
        return dados[chave]["recorde"]
    return None


def obter_arquivo_musica(numero : int):
    with open(PATH_DB, 'r') as f:
        dados = json.load(f)

    chave = str(numero) 
    if chave in dados:
        return dados[chave]["arquivo"]
    return None


def obter_titulos():
    with open(PATH_DB, 'r') as f:
        dados = json.load(f)

    titulos = []
    for numero in sorted(dados, key=lambda x: int(x)):  # ordena por número
        titulos.append(dados[numero]["nome"])

    return titulos


def atualizar_recorde(numero : int, pontuacao : int):
    with open(PATH_DB, 'r') as f:
        dados = json.load(f)

    chave = str(numero)
    if chave in dados:
        dados[chave]['recorde'] = pontuacao
        with open(PATH_DB, 'w') as f:
            json.dump(dados, f, indent=4)


def obter_lista_recordes():
    with open(PATH_DB, 'r') as f:
        dados = json.load(f)

    recordes = []
    for numero in sorted(dados, key=lambda x: int(x)):  # garante ordem numérica
        recordes.append(dados[numero]["recorde"])

    return recordes

def resetar_recordes():
    with open(PATH_DB, 'r') as f:
        dados = json.load(f)

    for musica in dados.values():
        musica["recorde"] = 0  # zera o recorde

    with open(PATH_DB, 'w') as f:
        json.dump(dados, f, indent=4)
