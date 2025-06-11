import json
import os
from constants import PATH_DB 

# Verifica se o arquivo já existe; se não, cria com um dicionário vazio
if not os.path.exists(PATH_DB):
    with open(PATH_DB, 'w') as f:
        json.dump({}, f, indent=2)


def alterar_DB(dados):
    if not PATH_DB.endswith(".json"):
        raise ValueError(f"Extensão inválida: '{PATH_DB}' não é um arquivo JSON.")
    
    try:
        with open(PATH_DB, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=2)
        print(f"Arquivo '{PATH_DB}' salvo com sucesso.")
        return True
    
    except PermissionError:
        print("Erro: Sem permissão para escrever no arquivo.")
    except TypeError as e:
        print(f"Erro ao converter os dados em JSON: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")


def abrir_DB():
    if not PATH_DB.endswith(".json"):
        raise ValueError(f"Extensão inválida: '{PATH_DB}' não é um arquivo JSON.")
    
    try:
        with open(PATH_DB, 'r', encoding='utf-8') as f:
            return json.load(f) 

    except FileNotFoundError:
        print("Erro: Arquivo JSON não encontrado.")
    except PermissionError:
        print("Erro: Sem permissão para abrir o arquivo JSON.")
    except json.JSONDecodeError:
        print("Erro: Conteúdo do arquivo JSON está malformado.")
    except Exception as e:
        print(f"Erro inesperado: {e}")
        

def adicionar_musica(nome : str, arquivo : str):
    dados = abrir_DB()

    if dados == None:
        return False

    dados[len(dados)] = {
        "nome": nome,
        "arquivo": "sons/" + arquivo,
        "recorde": 0
    }

    operacao_sucedida = alterar_DB(dados)
    if operacao_sucedida == None:
        return False   
    return True


def remover_musica(indice_para_remover : int):
    dados = abrir_DB()

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

    alterar_DB(dados_reindexados)
    # with open(PATH_DB, 'w', encoding='utf-8') as f:
    #     json.dump(dados_reindexados, f, indent=4, ensure_ascii=False)


def obter_nome_musica(numero : int):
    dados = abrir_DB()

    chave = str(numero) 
    if chave in dados:
        return dados[chave]["nome"]
    return None


def obter_recorde_musica(numero : int):
    dados = abrir_DB()

    chave = str(numero) 
    if chave in dados:
        return dados[chave]["recorde"]
    return None


def obter_arquivo_musica(numero : int):
    dados = abrir_DB()
    
    chave = str(numero) 
    if chave in dados:
        return dados[chave]["arquivo"]
    return None


def obter_titulos():
    dados = abrir_DB()

    titulos = []
    for numero in sorted(dados, key=lambda x: int(x)):  # ordena por número
        titulos.append(dados[numero]["nome"])

    return titulos


def atualizar_recorde(numero : int, pontuacao : int):
    dados = abrir_DB()

    chave = str(numero)
    if chave in dados:
        dados[chave]['recorde'] = pontuacao
        alterar_DB(dados)


def obter_lista_recordes():
    dados = abrir_DB()

    recordes = []
    for numero in sorted(dados, key=lambda x: int(x)):  # garante ordem numérica
        recordes.append(dados[numero]["recorde"])

    return recordes


def resetar_recordes():
    dados = abrir_DB()
    if dados == None:
        return False
    
    for musica in dados.values():
        musica["recorde"] = 0  # zera o recorde

    operacao_sucedida = alterar_DB(dados)
    if operacao_sucedida == None:
        return False
    return True
