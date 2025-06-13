import pygame
import pygame.midi
import serial 
import threading
import json
import sys
import extract
import db_functions
from constants import PATH_IMAGEM_FUNDO_PRINCIPAL, PATH_MUSICA_FUNDO, PATH_NOTAS_JSON
from constants import NOME_JOGO, MAX_ERROS, FPS, STATUS_LEDS
from constants import VERDE, AZUL, AMARELO, VERMELHO, PRETO, CINZA, BRANCO, MARROM, BEGE
from constants import FONTE_MUITO_PEQUENA, FONTE_PEQUENA, FONTE, FONTE_GRANDE
from constants import ALTURA_TELA, LARGURA_TELA, ALTURA_LINHA_ACERTO, LARGURA_COLUNA, N_COLUNAS
from constants import NOTA_VOLUME, EFEITOS_SONOROS_VOLUME, MUSICA_FUNDO_VOLUME, SONS
from constants import BOT_VERMELHO, BOT_AMARELO, BOT_AZUL, BOT_VERDE, BOT_PRETO, BOTOES




############################
# Init pygame e Constantes #
############################

# Inicialização Pygame
pygame.init()
pygame.midi.init()
player = pygame.midi.Output(pygame.midi.get_default_output_id())
player.set_instrument(0)

# Tela
TELA = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
pygame.display.set_caption(NOME_JOGO)
clock = pygame.time.Clock()

# Fundo
FUNDO_CARREGADO = pygame.image.load(PATH_IMAGEM_FUNDO_PRINCIPAL)  # JPG, PNG, BMP, etc.
FUNDO_CARREGADO = pygame.transform.scale(FUNDO_CARREGADO, (LARGURA_TELA, ALTURA_TELA))  
# ^ Redimensiona para caber na tela

# Sons
notas_ativas = []
pygame.mixer.music.load(PATH_MUSICA_FUNDO)
pygame.mixer.music.set_volume(MUSICA_FUNDO_VOLUME)
for s in SONS:
    s.set_volume(EFEITOS_SONOROS_VOLUME)

# Identificador da música selecionada
Numero_musica = 0

###################
#  FIM INIT + CTE #
###################














################################
# ARDUINO E COMUNICACAO SERIAL #
################################


# Conectar à porta COM
arduino = serial.Serial('COM3', 9600)

pygame.time.delay(750) # esperar arduino iniciar

LER = True  
USEREVENT_BOTAO = pygame.USEREVENT + 1

# Ler a porta serial em thread separada
def ler_serial():
    global LER
    while LER:
        if arduino.in_waiting > 0:
            dado = arduino.readline().decode().strip()
            print("Recebido:", dado)
            evento = pygame.event.Event(USEREVENT_BOTAO, {'botao': dado})
            pygame.event.post(evento)


# Inicia a thread de leitura serial
threading.Thread(target=ler_serial, daemon=True).start()


#################
#  FIM ARDUINO  #
#################












#####################
# FUNCOES E CLASSES #
#####################

def tocar_nota(index : int):
    agora = pygame.time.get_ticks()
    for nota in notasjson[index]:
        velocidade = max(0, min(127, int(nota["intensidade"] * NOTA_VOLUME)))
        duracao_ms = int(nota["duracao"] * 1000)

        player.note_on(nota["nota"], velocidade)

        # Adiciona a nota à lista de notas ativas
        notas_ativas.append({
            "nota": nota["nota"],
            "velocidade": velocidade,
            "desligar_em": agora + duracao_ms
        })
    return


# Função que gerencia as durações das notas
def atualizar_notas():
    agora = pygame.time.get_ticks()
    for nota in notas_ativas[:]:  # copia da lista para remover com segurança
        if agora >= nota["desligar_em"]:
            player.note_off(nota["nota"], nota["velocidade"])
            notas_ativas.remove(nota)


class Nota:
    def __init__(self, index : int):
        self.index = index
        self.coluna = notasjson[index][0]['coluna']
        self.raio = LARGURA_COLUNA/2
        self.x = self.coluna * LARGURA_COLUNA + LARGURA_COLUNA/2 + 1
        self.y = - self.raio*2
        self.largura = LARGURA_COLUNA
        self.altura = - self.y
        self.velocidade = 5
        self.cor = None
        match self.coluna:
            case 0:
                self.cor = VERMELHO
            case 1:
                self.cor = AMARELO
            case 2:
                self.cor = AZUL
            case 3:
                self.cor = VERDE

    def atualizar(self):
        self.y += self.velocidade

    def desenhar(self, TELA):
        pygame.draw.circle(TELA, self.cor, (self.x,self.y), self.raio)

    # Retorna True se a nota tiver sido acertada
    def colidiu(self):
        return self.y + self.raio >= ALTURA_LINHA_ACERTO and self.y - self.raio <= ALTURA_LINHA_ACERTO
    
    def calcular_pontos(self):
        return int(100* (ALTURA_LINHA_ACERTO - (self.y - self.raio))/(2*self.raio))


def mostrar_erro(coluna):
    for i in range(1000):
        pygame.draw.rect(TELA, VERMELHO, (coluna*LARGURA_COLUNA, 0, LARGURA_COLUNA, ALTURA_TELA))


def desenhar_texto(texto, fonte, cor, centro):
    render = fonte.render(texto, True, cor)
    rect = render.get_rect(center=centro)
    TELA.blit(render, rect)


def desenhar_direcionais():
    pygame.draw.rect(TELA, MARROM, (10, int(ALTURA_TELA*0.85) - 30, 175, 110)) 
    desenhar_texto("PRETO: SELECIONAR", FONTE_MUITO_PEQUENA, PRETO, (LARGURA_TELA//10 + 44, int(ALTURA_TELA*0.83)))
    desenhar_texto("VERMELHO: ESQUERDA", FONTE_MUITO_PEQUENA, VERMELHO, (LARGURA_TELA//10 + 52, int(ALTURA_TELA*0.83) + 20))
    desenhar_texto("AMARELO: CIMA", FONTE_MUITO_PEQUENA, AMARELO, (LARGURA_TELA//10 + 30, int(ALTURA_TELA*0.83) + 40))
    desenhar_texto("AZUL: BAIXO", FONTE_MUITO_PEQUENA, AZUL, (LARGURA_TELA//10 + 16, int(ALTURA_TELA*0.83) + 60))
    desenhar_texto("VERDE: DIREITA", FONTE_MUITO_PEQUENA, VERDE, (LARGURA_TELA//10 + 27, int(ALTURA_TELA*0.83) + 80)) 


def esperar_tecla(botao):
    esperando = True
    while esperando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == USEREVENT_BOTAO and evento.botao == botao:
                esperando = False


def abrir_arquivo(file):
    if not file.endswith(".json"):
        print(f"Extensão inválida: '{file}' não é um arquivo JSON.")
        return None
    
    try:
        with open(file, 'r', encoding='utf-8') as f:
            return json.load(f) 

    except FileNotFoundError:
        print("Erro: Arquivo JSON não encontrado.")
    except PermissionError:
        print("Erro: Sem permissão para abrir o arquivo JSON.")
    except json.JSONDecodeError:
        print("Erro: Conteúdo do arquivo JSON está malformado.")
    except Exception as e:
        print(f"Erro inesperado: {e}")


#####################
#    FIM FUNCOES    #
#####################












###################
#      TELAS      #
###################


def menu_principal():
    global LER
    global Numero_musica

    pygame.mixer.music.play(-1)

    opcoes = ["Jogar", "Músicas", "Tutorial", "Configurações", "Sair"]
    N_opcoes = len(opcoes)
    selecao = 0
    
    SAIR_DO_JOGO = False

    while SAIR_DO_JOGO == False:

        # Desenha o fundo personalizado para essa tela
        TELA.blit(FUNDO_CARREGADO, (0, 0))

        desenhar_texto(NOME_JOGO, FONTE_GRANDE, MARROM, (LARGURA_TELA//2, ALTURA_TELA//3 - 10))
        desenhar_direcionais()
        
        for i, opcao in enumerate(opcoes):
            cor = BRANCO if i == selecao else CINZA
            desenhar_texto(opcao, FONTE, cor, (LARGURA_TELA//2, ALTURA_TELA//2 - 50 + i*40))

        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                SAIR_DO_JOGO = True
            if evento.type == USEREVENT_BOTAO:
                if evento.botao == BOT_AMARELO: 
                    SONS[0].play()
                    selecao = (selecao - 1) % N_opcoes
                elif evento.botao == BOT_AZUL: 
                    SONS[2].play()
                    selecao = (selecao + 1) % N_opcoes
                elif evento.botao == BOT_PRETO:
                    SONS[3].play()
                    match selecao:
                        case 0:
                            pygame.mixer.music.pause()
                            jogar()
                            pygame.mixer.music.unpause()
                        case 1:
                            Numero_musica = selecionar_musica(Numero_musica)
                        case 2:
                            tutorial()
                        case 3:
                            pygame.mixer.music.pause()
                            configuracoes()
                            pygame.mixer.music.unpause()
                        case 4:
                            SAIR_DO_JOGO = True


def selecionar_musica(index : int):

    opcoes = db_functions.obter_titulos()
    N_opcoes = len(opcoes)
    recordes = db_functions.obter_lista_recordes()

    if index >= N_opcoes:
        index = 0

    if N_opcoes == 0:
        TELA.fill(BEGE)
        desenhar_texto("Sem Músicas", FONTE_GRANDE, VERMELHO, (LARGURA_TELA//2, ALTURA_TELA//3))
        desenhar_texto("Adicione músicas nas configurações", FONTE_PEQUENA, CINZA, (LARGURA_TELA//2, ALTURA_TELA*1//2))
        desenhar_texto("Pressione o botão preto para sair", FONTE_PEQUENA, CINZA, (LARGURA_TELA//2, ALTURA_TELA*2//3))
        pygame.display.flip()
        esperar_tecla(BOT_PRETO)
        return 0

    while True:
        TELA.fill(BEGE)
        desenhar_texto("Músicas", FONTE_GRANDE, MARROM, (LARGURA_TELA//2, ALTURA_TELA//3))
        desenhar_texto("Pressione o botão preto para sair", FONTE_PEQUENA, CINZA, (LARGURA_TELA//2, 2*ALTURA_TELA//3))

        desenhar_direcionais()

        desenhar_texto("<  " + opcoes[index] + "  >", FONTE, BRANCO, (LARGURA_TELA//2, ALTURA_TELA//2))
        desenhar_texto("Recorde : " + str(recordes[index]) + " pontos", FONTE, CINZA, (LARGURA_TELA//2, ALTURA_TELA//2 + 40))
        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == USEREVENT_BOTAO:
                if evento.botao == BOT_AMARELO or evento.botao == BOT_VERMELHO:
                    index = (index - 1) % N_opcoes
                elif evento.botao == BOT_AZUL or evento.botao == BOT_VERDE:
                    index = (index + 1) % N_opcoes
                elif evento.botao == BOT_PRETO:
                    return index


def tutorial():
    TELA.fill(BEGE)
    desenhar_texto("Tutorial", FONTE_GRANDE, MARROM, (LARGURA_TELA//2, ALTURA_TELA*2//20 - 10))
    desenhar_texto("Bem-vindo ao PoliTiles", FONTE_PEQUENA, CINZA, (LARGURA_TELA//2, ALTURA_TELA*3//20))
    desenhar_texto("Nesse jogo, seu objetivo é simples:", FONTE_PEQUENA, CINZA, (LARGURA_TELA//2, ALTURA_TELA*4//20))
    desenhar_texto("Aperte os botões assim que os círculos", FONTE_MUITO_PEQUENA, CINZA, (LARGURA_TELA//2, ALTURA_TELA*5//20))
    desenhar_texto("estiverem sobre a linha vermelha para pontuar.", FONTE_MUITO_PEQUENA, CINZA, (LARGURA_TELA//2, ALTURA_TELA*6//20))
    desenhar_texto("Como jogar?", FONTE_PEQUENA, CINZA, (LARGURA_TELA//2, ALTURA_TELA*7//20 + 5))
    desenhar_texto("1. Observe as 4 colunas (cada uma ligada a um botão)", FONTE_MUITO_PEQUENA, CINZA, (LARGURA_TELA//2, ALTURA_TELA*8//20))
    desenhar_texto("2. Aguarde: círculos coloridos vão cair do topo", FONTE_MUITO_PEQUENA, CINZA, (LARGURA_TELA//2, ALTURA_TELA*9//20))
    desenhar_texto("3. Quando uma nota estiver sobre a linha vermelha,", FONTE_MUITO_PEQUENA, CINZA, (LARGURA_TELA//2, ALTURA_TELA*10//20))
    desenhar_texto("Pressione o botão correspondente", FONTE_MUITO_PEQUENA, CINZA, (LARGURA_TELA//2, ALTURA_TELA*11//20))
    desenhar_texto("Fim de Jogo:", FONTE_PEQUENA, CINZA, (LARGURA_TELA//2, ALTURA_TELA*12//20 + 5))
    desenhar_texto("Derrota: O jogo acaba se você perder todas as vidas", FONTE_MUITO_PEQUENA, CINZA, (LARGURA_TELA//2, ALTURA_TELA*13//20))
    desenhar_texto("Vitória: O jogo acaba se a música chegar ao fim", FONTE_MUITO_PEQUENA, CINZA, (LARGURA_TELA//2, ALTURA_TELA*14//20))
    desenhar_texto("OBS: Acertar nota: + Precisão --> + pontos", FONTE_MUITO_PEQUENA, CINZA, (LARGURA_TELA//2, ALTURA_TELA*15//20))
    desenhar_texto("OBS: Errar ou deixar a nota passar = -1 vida.", FONTE_MUITO_PEQUENA, CINZA, (LARGURA_TELA//2, ALTURA_TELA*16//20))
    desenhar_texto("Pressione o botão preto para sair", FONTE_PEQUENA, CINZA, (LARGURA_TELA//2, ALTURA_TELA*18//20))
    pygame.display.flip()
    esperar_tecla(BOT_PRETO)
    return


def configuracoes():
    global MUSICA_FUNDO_VOLUME
    global EFEITOS_SONOROS_VOLUME
    global NOTA_VOLUME
    global STATUS_LEDS
    global MAX_ERROS
    global arduino

    selecao = 0

    while True:
        TELA.fill(BEGE)
        desenhar_texto("Configurações", FONTE_GRANDE, MARROM, (LARGURA_TELA//2, 60))
        desenhar_direcionais()

        opcoes = [f"Música de fundo: {int(MUSICA_FUNDO_VOLUME*100)}%", f"Efeitos sonoros de menu: {int(EFEITOS_SONOROS_VOLUME*100)}%", f"Volume das notas: {int(NOTA_VOLUME*100)}%", f"LEDS: {'Ligados' if STATUS_LEDS else 'Desligados'}", f"Erros permitidos: {MAX_ERROS}", "Limpar Recordes", "Adicionar Músicas", "Remover Músicas", "Voltar"]
        N_opcoes = len(opcoes)
        
        for i, texto in enumerate(opcoes):
            cor = BRANCO if i == selecao else CINZA
            desenhar_texto(texto, FONTE, cor, (LARGURA_TELA//2, ALTURA_TELA//5 + i * 38))

        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == USEREVENT_BOTAO:
                if evento.botao == BOT_AMARELO:
                    selecao = (selecao - 1) % N_opcoes      
                elif evento.botao == BOT_AZUL:
                    selecao = (selecao + 1) % N_opcoes
                elif evento.botao == BOT_VERMELHO:
                    match selecao:
                        case 0:
                            MUSICA_FUNDO_VOLUME = max(0.0, MUSICA_FUNDO_VOLUME - 0.05)
                            pygame.mixer.music.set_volume(MUSICA_FUNDO_VOLUME)
                        case 1:
                            EFEITOS_SONOROS_VOLUME = max(0.0, EFEITOS_SONOROS_VOLUME - 0.05)
                            for s in SONS:
                                s.set_volume(EFEITOS_SONOROS_VOLUME)
                        case 2:
                            NOTA_VOLUME = max(0.0, NOTA_VOLUME - 0.05)
                        case 3:
                            STATUS_LEDS = not STATUS_LEDS
                            if STATUS_LEDS == True:
                                arduino.write("ON\n".encode())
                            if STATUS_LEDS == False:
                                arduino.write("OFF\n".encode())
                        case 4:
                            MAX_ERROS = max(MAX_ERROS - 1, 1)
                elif evento.botao == BOT_VERDE:
                    match selecao:
                        case 0:
                            MUSICA_FUNDO_VOLUME = min(1.0, MUSICA_FUNDO_VOLUME + 0.05)
                            pygame.mixer.music.set_volume(MUSICA_FUNDO_VOLUME)
                        case 1:
                            EFEITOS_SONOROS_VOLUME = max(0.0, EFEITOS_SONOROS_VOLUME + 0.05)
                            for s in SONS:
                                s.set_volume(EFEITOS_SONOROS_VOLUME)
                        case 2:
                            NOTA_VOLUME = min(1.0, NOTA_VOLUME + 0.05)
                        case 3:
                            STATUS_LEDS = not STATUS_LEDS
                            if STATUS_LEDS == True:
                                arduino.write("ON\n".encode())
                            if STATUS_LEDS == False:
                                arduino.write("OFF\n".encode())
                        case 4:
                            MAX_ERROS+=1
                elif evento.botao == BOT_PRETO:
                    if selecao == 3:
                        STATUS_LEDS = not STATUS_LEDS
                        if STATUS_LEDS == True:
                            arduino.write("ON\n".encode())
                        if STATUS_LEDS == False:
                            arduino.write("OFF\n".encode())
                    if selecao == 5:
                        operacao_sucedida = db_functions.resetar_recordes()
                        if operacao_sucedida == True:
                            desenhar_texto("Recordes limpos", FONTE, VERMELHO, (LARGURA_TELA//2, 460))
                        if operacao_sucedida == False:
                            desenhar_texto("A operação falhou!", FONTE, VERMELHO, (LARGURA_TELA//2, 460))                            
                        pygame.display.flip()
                        pygame.time.delay(400)
                    elif selecao == 6:
                        operacao_sucedida = adicionar_musicas()
                        if operacao_sucedida == True:
                            desenhar_texto("Operação bem sucedida", FONTE, VERMELHO, (LARGURA_TELA//2, 400))
                        if operacao_sucedida == False:
                            desenhar_texto("A operação falhou!", FONTE, VERMELHO, (LARGURA_TELA//2, 400))
                        pygame.display.flip()
                        pygame.time.delay(400)
                    elif selecao == 7:
                        operacao_sucedida = remover_musicas()
                        if operacao_sucedida == True:
                            desenhar_texto("Operação bem sucedida", FONTE, VERMELHO, (LARGURA_TELA//2, 460))
                            pygame.display.flip()
                            pygame.time.delay(400)
                    elif selecao == 8:
                        return


def adicionar_musicas():
    selecao = 0
    N_opcoes = 4
    nome = ""
    path = ""
    FIM_DA_ADICAO = False
    editando = False
    campo_ativo = ""  # 'nome' ou 'path'
    texto_temp = ""

    while not FIM_DA_ADICAO:
        TELA.fill(BEGE)

        desenhar_texto("Adicionar Música", FONTE_GRANDE, MARROM, (LARGURA_TELA//2, ALTURA_TELA//10))
        
        # Renderiza o menu e os campos de texto
        cor = BRANCO if selecao == 0 else CINZA
        desenhar_texto("Insira o nome da música", FONTE_PEQUENA, CINZA, (LARGURA_TELA//2, ALTURA_TELA//5))
        pygame.draw.rect(TELA, cor, (LARGURA_TELA//6, ALTURA_TELA//5 + 20, LARGURA_TELA*2//3, 40))
        desenhar_texto(nome if selecao != 0 or not editando else texto_temp + "|", FONTE_MUITO_PEQUENA, PRETO, (LARGURA_TELA//2, ALTURA_TELA//5 + 40))

        cor = BRANCO if selecao == 1 else CINZA
        desenhar_texto("Insira o nome do arquivo (Ex: Nome.mid)", FONTE_PEQUENA, CINZA, (LARGURA_TELA//2, ALTURA_TELA*2//5 - 20))
        pygame.draw.rect(TELA, cor, (LARGURA_TELA//6, ALTURA_TELA*2//5, LARGURA_TELA*2//3, 40))
        desenhar_texto(path if selecao != 1 or not editando else texto_temp + "|", FONTE_MUITO_PEQUENA, PRETO, (LARGURA_TELA//2, ALTURA_TELA*2//5 + 20))

        cor = BRANCO if selecao == 2 else CINZA
        desenhar_texto("Salvar", FONTE_PEQUENA, cor, (LARGURA_TELA//2, ALTURA_TELA*3//5 - 45))

        cor = BRANCO if selecao == 3 else CINZA
        desenhar_texto("Sair", FONTE_PEQUENA, cor, (LARGURA_TELA//2, ALTURA_TELA*3//5 - 5))

        desenhar_texto("Atenção!", FONTE_PEQUENA, VERMELHO, (LARGURA_TELA//2, ALTURA_TELA*7//10 + 20))
        desenhar_texto("Desligue o Caps Lock.", FONTE_PEQUENA, CINZA, (LARGURA_TELA//2, ALTURA_TELA*7//10 + 20 + 25))
        desenhar_texto("Tome cuidado com o espaçamento.", FONTE_PEQUENA, CINZA, (LARGURA_TELA//2, ALTURA_TELA*7//10 + 20 + 50))
        desenhar_texto("Não utilize caracteres especiais.", FONTE_PEQUENA, CINZA, (LARGURA_TELA//2, ALTURA_TELA*7//10 + 20 + 75))
        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif evento.type == pygame.KEYDOWN:
                if editando:
                    if evento.key == pygame.K_RETURN:
                        if campo_ativo == "nome":
                            nome = texto_temp
                        elif campo_ativo == "path":
                            path = texto_temp
                        texto_temp = ""
                        editando = False
                        campo_ativo = ""
                    elif evento.key == pygame.K_BACKSPACE:
                        texto_temp = texto_temp[:-1]
                    elif evento.key == pygame.K_ESCAPE:
                        texto_temp = ""
                        editando = False
                        campo_ativo = ""
                    else:
                        texto_temp += evento.unicode
                else:
                    if evento.key == pygame.K_UP:
                        selecao = (selecao - 1) % N_opcoes
                    elif evento.key == pygame.K_DOWN:
                        selecao = (selecao + 1) % N_opcoes
                    elif evento.key == pygame.K_RETURN:
                        if selecao == 0:
                            editando = True
                            campo_ativo = "nome"
                            texto_temp = nome
                        elif selecao == 1:
                            editando = True
                            campo_ativo = "path"
                            texto_temp = path
                        elif selecao == 2:
                            # print(f"Nome: {nome}, Arquivo: {path}")
                            nome.strip()
                            path.strip()
                            if nome != "" and path != "":
                                db_functions.adicionar_musica(nome, path)
                                return True
                            return False
                        elif selecao == 3:
                            return False
            elif evento.type == USEREVENT_BOTAO:
                if editando:
                    if evento.botao == BOT_PRETO:
                        if campo_ativo == "nome":
                            nome = texto_temp
                        elif campo_ativo == "path":
                            path = texto_temp
                        texto_temp = ""
                        editando = False
                        campo_ativo = ""
                else:
                    if evento.botao == BOT_AMARELO:
                        selecao = (selecao - 1) % N_opcoes
                    elif evento.botao == BOT_AZUL:
                        selecao = (selecao + 1) % N_opcoes
                    elif evento.botao == BOT_PRETO:
                        if selecao == 0:
                            editando = True
                            campo_ativo = "nome"
                            texto_temp = nome
                        elif selecao == 1:
                            editando = True
                            campo_ativo = "path"
                            texto_temp = path
                        elif selecao == 2:
                            # print(f"Nome: {nome}, Arquivo: {path}")
                            nome.strip()
                            path.strip()
                            if nome != "" and path != "":
                                db_functions.adicionar_musica(nome, path)
                                return True
                            return False
                        elif selecao == 3:
                            return False  


def remover_musicas():
    global Numero_musica
    titulos = db_functions.obter_titulos()
    N_titulos = len(titulos)
    N_opcoes = 3
    selecao = 0
    index = 0
    retorno = False

    while True:

        TELA.fill(BEGE)
        desenhar_texto("Remover Músicas", FONTE_GRANDE, MARROM, (LARGURA_TELA//2, ALTURA_TELA//3))
        desenhar_direcionais()

        cor = BRANCO if selecao == 0 else CINZA
        if N_titulos == 0:
            desenhar_texto("< Sem músicas >", FONTE, VERMELHO, (LARGURA_TELA//2, ALTURA_TELA//2))
        else:
            desenhar_texto("<  " + titulos[index] + "  >", FONTE, cor, (LARGURA_TELA//2, ALTURA_TELA//2))
        cor = BRANCO if selecao == 1 else CINZA
        desenhar_texto("Remover", FONTE, cor, (LARGURA_TELA//2, ALTURA_TELA//2 + 40))
        cor = BRANCO if selecao == 2 else CINZA
        desenhar_texto("Sair", FONTE, cor, (LARGURA_TELA//2, ALTURA_TELA//2 + 80))

        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                match evento.key:
                    case pygame.K_LEFT if selecao == 0 and N_titulos != 0:
                        index = (index - 1) % N_titulos
                    case pygame.K_RIGHT if selecao == 0 and N_titulos != 0:
                        index = (index + 1) % N_titulos
                    case pygame.K_UP:
                        selecao = (selecao - 1) % N_opcoes
                    case pygame.K_DOWN:
                        selecao = (selecao + 1) % N_opcoes
                    case pygame.K_RETURN if selecao == 1:
                        db_functions.remover_musica(index)
                        desenhar_texto("Música Removida.", FONTE, VERMELHO, (LARGURA_TELA//2, 450))
                        titulos = db_functions.obter_titulos()
                        N_titulos = len(titulos)
                        Numero_musica = 0
                        selecao = 0
                        if N_titulos != 0:
                            index = (index - 1) % N_titulos
                        pygame.display.flip()
                        pygame.time.delay(400)
                        retorno = True
                    case pygame.K_RETURN if selecao == 2:
                        return retorno
                    case pygame.K_ESCAPE:
                        return retorno
            if evento.type == USEREVENT_BOTAO:
                if evento.botao == BOT_VERMELHO and selecao == 0 and N_titulos != 0:
                    index = (index - 1) % N_titulos
                if evento.botao == BOT_VERDE and selecao == 0 and N_titulos != 0:
                    index = (index + 1) % N_titulos
                if evento.botao == BOT_AMARELO:
                    selecao = (selecao - 1) % N_opcoes
                if evento.botao == BOT_AZUL:
                    selecao = (selecao + 1) % N_opcoes
                if evento.botao == BOT_PRETO:
                    if selecao == 1:
                        db_functions.remover_musica(index)
                        desenhar_texto("Música Removida.", FONTE, VERMELHO, (LARGURA_TELA//2, 450))
                        titulos = db_functions.obter_titulos()
                        N_titulos = len(titulos)
                        selecao = 0
                        Numero_musica = 0
                        if N_titulos != 0:
                            index = (index - 1) % N_titulos
                        pygame.display.flip()
                        pygame.time.delay(400)
                        retorno = True
                    if selecao == 2:
                        return retorno


def contagem_regressiva():
    for i in range(3,0,-1):
        TELA.fill(BEGE)
        desenhar_texto(str(i), FONTE_GRANDE, MARROM, (LARGURA_TELA//2, ALTURA_TELA//3))
        pygame.display.flip()
        pygame.time.delay(1000)
    return


def tela_preparacao():
    global notasjson
    global Numero_musica

    PATH_MUSICA = db_functions.obter_arquivo_musica(Numero_musica)

    TELA.fill(BEGE)
    desenhar_texto(NOME_JOGO, FONTE_GRANDE, MARROM, (LARGURA_TELA//2, ALTURA_TELA//3))
    desenhar_texto("Para começar", FONTE, CINZA, (LARGURA_TELA//2, ALTURA_TELA//2))
    desenhar_texto("Pressione o botão preto", FONTE, CINZA, (LARGURA_TELA//2, ALTURA_TELA//2 + 40))
    pygame.display.flip()
    esperar_tecla(BOT_PRETO)
    extracao_sucedida = extract.mid_to_json(PATH_MUSICA)
    if extracao_sucedida == False:
        tela_erro()
        return False
    if extracao_sucedida == True:
        notasjson = abrir_arquivo(PATH_NOTAS_JSON)
        if notasjson == None:
            tela_erro()
            return False
        contagem_regressiva()
        return True


def tela_erro():
    TELA.fill(BEGE)
    desenhar_texto("ERRO", FONTE_GRANDE, VERMELHO, (LARGURA_TELA//2, ALTURA_TELA//4))
    desenhar_texto("Não foi possível carregar a música", FONTE, CINZA, (LARGURA_TELA//2, ALTURA_TELA//4 + 60))
    desenhar_texto("Sugestões:", FONTE, CINZA, (LARGURA_TELA//2, ALTURA_TELA//4 + 110))
    desenhar_texto("1) Escolha outra música", FONTE, CINZA, (LARGURA_TELA//2, ALTURA_TELA//4 + 140))
    desenhar_texto("2) Revise os arquivos de origem", FONTE, CINZA, (LARGURA_TELA//2, ALTURA_TELA//4 + 170))
    desenhar_texto("Para voltar ao menu", FONTE, CINZA, (LARGURA_TELA//2, ALTURA_TELA//4 + 220))
    desenhar_texto("Pressione o botão preto", FONTE, CINZA, (LARGURA_TELA//2, ALTURA_TELA//4 + 250))
    pygame.display.flip()
    esperar_tecla(BOT_PRETO)


def tela_pause():
    
    opcoes = ["Retomar Jogo", "Voltar para o Menu Principal"]
    N_opcoes = len(opcoes)
    selecao = 0
    
    while(True):

        TELA.fill(BEGE)
        desenhar_texto("Jogo pausado.", FONTE_GRANDE, MARROM, (LARGURA_TELA//2, ALTURA_TELA//3 + 40))

        for i, texto in enumerate(opcoes):
            cor = BRANCO if i == selecao else CINZA
            desenhar_texto(texto, FONTE, cor, (LARGURA_TELA//2, ALTURA_TELA/2 + i * 40))

        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == USEREVENT_BOTAO:
                if evento.botao == BOT_AMARELO:
                    selecao = (selecao - 1) % N_opcoes
                elif evento.botao == BOT_AZUL:
                    selecao = (selecao + 1) % N_opcoes
                elif evento.botao == BOT_PRETO:
                    if selecao == 0:
                        return False 
                    if selecao == 1:
                        return True


def tela_derrota():
    TELA.fill(BEGE)
    desenhar_texto("Fim de Jogo!", FONTE_GRANDE, VERMELHO, (LARGURA_TELA//2, ALTURA_TELA//3))
    desenhar_texto("Você perdeu", FONTE_GRANDE, VERMELHO, (LARGURA_TELA//2, ALTURA_TELA//3 + 70))
    desenhar_texto("Pressione o botão preto para sair", FONTE, CINZA, (LARGURA_TELA//2, ALTURA_TELA//2 + 40))
    pygame.display.flip()
    esperar_tecla(BOT_PRETO)


def tela_vitoria(pontos : int):
    global Numero_musica
    TELA.fill(BEGE)
    if db_functions.obter_recorde_musica(Numero_musica) <= pontos:
        db_functions.atualizar_recorde(Numero_musica, pontos)
        desenhar_texto("Parabéns!", FONTE_GRANDE, VERMELHO, (LARGURA_TELA//2, ALTURA_TELA//3 - 40))
        desenhar_texto("Você venceu!", FONTE_GRANDE, VERMELHO, (LARGURA_TELA//2, ALTURA_TELA//3))
        desenhar_texto("Novo Recorde!", FONTE_GRANDE, VERMELHO, (LARGURA_TELA//2, ALTURA_TELA//3 + 40))
    else:
        desenhar_texto("Parabéns!", FONTE_GRANDE, VERMELHO, (LARGURA_TELA//2, ALTURA_TELA//3))
        desenhar_texto("Você venceu!", FONTE_GRANDE, VERMELHO, (LARGURA_TELA//2, ALTURA_TELA//3 + 40))
    
    desenhar_texto(f"Pontos: {pontos}", FONTE, CINZA, (LARGURA_TELA//2, ALTURA_TELA//2))
    desenhar_texto("Pressione o botão preto para sair", FONTE, CINZA, (LARGURA_TELA//2, ALTURA_TELA//2 + 40))
    pygame.display.flip()
    esperar_tecla(BOT_PRETO)


# Função operacional do jogo
def jogar():
    global notasjson

    preparativos_finalizados = tela_preparacao()
    if preparativos_finalizados == False:
        return

    notas_index = 0
    notas = []
    pontos = 0
    erros = 0
    inicio_musica = pygame.time.get_ticks()
    tempo_pausado = 0
    intervalo_inicial = 400
    intervalo_final = 200

    while True:
        TELA.fill(BEGE)
        agora = pygame.time.get_ticks()

        # Linhas verticais
        for i in range(1, N_COLUNAS):
            pygame.draw.line(TELA, CINZA, (i*LARGURA_COLUNA, 0), (i*LARGURA_COLUNA, ALTURA_TELA), 2)

        # Linha de acerto
        pygame.draw.rect(TELA, VERMELHO, (0, ALTURA_LINHA_ACERTO, LARGURA_TELA, 5))

        # Botão de pausa
        pygame.draw.rect(TELA, CINZA, (LARGURA_TELA-60, 13, 50, 30))
        desenhar_texto("||", FONTE, BRANCO, (LARGURA_TELA-35, 25))
        desenhar_texto("BOTÃO", FONTE_MUITO_PEQUENA, BRANCO, (LARGURA_TELA-35, 55))
        desenhar_texto("PRETO", FONTE_MUITO_PEQUENA, BRANCO, (LARGURA_TELA-35, 70))

        for evento in pygame.event.get():
            if agora - inicio_musica - tempo_pausado < intervalo_inicial:
                break
            if evento.type == pygame.QUIT: # não eh pra acontecer, mas deixa por precaucao <3
                pygame.quit()
                arduino.close()
                sys.exit()
            elif evento.type == USEREVENT_BOTAO:
                if evento.botao == BOT_PRETO: # Jogo pausado
                    acumulador = pygame.time.get_ticks()
                    SAIR = tela_pause() # Retorna True se o jogador escolher voltar para o menu
                    if SAIR:
                        return
                    contagem_regressiva()
                    tempo_pausado += pygame.time.get_ticks() - acumulador   
                if evento.botao in BOTOES:
                    idx = BOTOES.index(evento.botao)
                    colisao = False
                    for nota in notas:
                        if nota.coluna == idx and nota.colidiu():
                            colisao = True
                            tocar_nota(nota.index)
                            notas.remove(nota)
                            pontos += nota.calcular_pontos()
                            break
                    if colisao == False:
                        mostrar_erro(idx)
                        erros += 1
                        if erros >= MAX_ERROS:
                            tela_derrota(   )
                            return        

        
        # Atualiza notas na tela
        for nota in notas[:]:
            nota.atualizar()
            nota.desenhar(TELA)
            if nota.y > ALTURA_TELA:
                mostrar_erro(nota.coluna)
                notas.remove(nota)
                erros += 1
                if erros >= MAX_ERROS:
                    tela_derrota()
                    return

        # Atualiza notas em som
        atualizar_notas()

        # Gera nova nota
        if notas_index == 0: 
            if agora - inicio_musica - tempo_pausado >= intervalo_inicial:
                notas.append(Nota(notas_index))
                inicio_musica = agora
                notas_index+=1
        elif notas_index < len(notasjson) and agora - inicio_musica - tempo_pausado >= int(notasjson[notas_index][0]["inicio"]*1000):    
            notas.append(Nota(notas_index))
            notas_index+=1
        

        # Carrega a tela de vitória
        if notas_index >= len(notasjson):
            intervalo_final -= 1
            if intervalo_final == 0:
                tela_vitoria(pontos)
                return

        # Pontuação e erros em tempo real
        desenhar_texto(f"Pontos: {pontos}", FONTE, BRANCO, (90, 20))
        desenhar_texto(f"Erros: {erros}/{MAX_ERROS}", FONTE, VERMELHO, (90, 50))

        pygame.display.flip()
        clock.tick(FPS)


#####################
#    FIM TELAS      #
#####################















###################
#      MAIN      #
###################

menu_principal()


arduino.write("ON\n".encode())
LER = False
arduino.close()
pygame.quit()
sys.exit()
