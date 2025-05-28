import pygame
import pygame.midi
import serial 
import threading
import json
import sys
import extract





############################
# Init pygame e Constantes #
############################

file_musica = "Happy_Birthday.mid"

# Carrega as notas musicais
with open("notas_Happy_Birthday.json", "r") as f:
    notasjson = json.load(f)

# Inicialização
pygame.init()
pygame.midi.init()
player = pygame.midi.Output(pygame.midi.get_default_output_id())
player.set_instrument(0)

NOME_DO_JOGO =  "PoliTiles"
LARGURA_TELA, ALTURA_TELA = 460, 600
ALTURA_LINHA_ACERTO = ALTURA_TELA - 100
MAX_ERROS = 5
TELA = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
pygame.display.set_caption(NOME_DO_JOGO)
clock = pygame.time.Clock()
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
FONTE_PEQUENA = pygame.font.SysFont("Algerian", 20)
FONTE = pygame.font.SysFont("Algerian", 24)
FONTE_GRANDE = pygame.font.SysFont("Algerian", 36)

# Colunas e teclas
N_COLUNAS = 4
LARGURA_COLUNA = LARGURA_TELA // N_COLUNAS
# TECLAS = [pygame.K_q, pygame.K_w, pygame.K_e, pygame.K_r]

# Sons
pygame.mixer.init()
notas_ativas = []
NOTA_VOLUME = 0.5

# Gerar um "som ao toque" para os botões no menu
SONS = [
    pygame.mixer.Sound('piano1.wav'),
    pygame.mixer.Sound('piano2.wav'),
    pygame.mixer.Sound('piano3.wav'),
    pygame.mixer.Sound('piano4.wav')
]

# Música de fundo
pygame.mixer.music.load('moonlight-sonata-classical-piano-beethoven.mp3')
pygame.mixer.music.set_volume(0.05)
for s in SONS:
    s.set_volume(0.05)

# Botoes Arduino
BOT_VERMELHO = "VERMELHO"
BOT_AMARELO = "AMARELO"
BOT_AZUL = "AZUL"
BOT_VERDE = "VERDE"
BOT_PRETO = "PRETO"

BOTOES = [BOT_VERMELHO, BOT_AMARELO, BOT_AZUL, BOT_VERDE, BOT_PRETO]

###################
#  FIM INIT + CTE #
###################













################################
# ARDUINO E COMUNICACAO SERIAL #
################################

# Conectar à porta COM correta (verifique no Arduino IDE)
arduino = serial.Serial('COM3', 9600)
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

# Função que emite o som da nota 
def tocar_nota(index):
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


# Função que gerencia as durações das notas
def atualizar_notas():
    agora = pygame.time.get_ticks()
    for nota in notas_ativas[:]:  # copia da lista para remover com segurança
        if agora >= nota["desligar_em"]:
            player.note_off(nota["nota"], nota["velocidade"])
            notas_ativas.remove(nota)


# Classe Nota
class Nota:
    def __init__(self, index):
        self.index = index
        self.coluna = notasjson[index][0]['coluna']
        self.raio = LARGURA_COLUNA/2
        self.x = self.coluna * LARGURA_COLUNA + LARGURA_COLUNA/2 + 1
        self.y = - min(400,max(200*notasjson[index][0]['M_altura'],120))
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

    def desenhar(self, tela):
        # pygame.draw.rect(tela, PRETO, (self.x, self.y, self.largura, self.altura))
        pygame.draw.circle(tela, self.cor, (self.x,self.y), self.raio)

    # Retorna True se a nota tiver sido acertada
    def colidiu(self):
        return self.y + self.raio >= ALTURA_LINHA_ACERTO and self.y - self.raio <= ALTURA_LINHA_ACERTO
    
    def calcular_pontos(self):
        return int(100* (ALTURA_LINHA_ACERTO - (self.y - self.raio))/(2*self.raio))


# Função para desenhar erros
def mostrar_erro(tela, coluna):
    for i in range(1000):
        pygame.draw.rect(tela, VERMELHO, (coluna*LARGURA_COLUNA, 0, LARGURA_COLUNA, 600))


# Função para desenhar textos centralizados
def desenhar_texto(tela, texto, fonte, cor, centro):
    render = fonte.render(texto, True, cor)
    rect = render.get_rect(center=centro)
    tela.blit(render, rect)


def desenhar_direcionais(TELA):
    arial = pygame.font.SysFont("Arial", 20)
    pygame.draw.rect(TELA, MARROM, (10, int(ALTURA_TELA*0.95) - 30, 130, 45))
    desenhar_texto(TELA, "Direcionais:", FONTE_PEQUENA, PRETO, (LARGURA_TELA//10 + 30, int(ALTURA_TELA*0.95) - 20))
    desenhar_texto(TELA, "<", arial, VERMELHO, (LARGURA_TELA//10, int(ALTURA_TELA*0.95)))
    desenhar_texto(TELA, "^", arial, AMARELO, (LARGURA_TELA//10 + 20, int(ALTURA_TELA*0.95) + 5))
    desenhar_texto(TELA, "v", arial, AZUL, (LARGURA_TELA//10 + 40, int(ALTURA_TELA*0.95)))
    desenhar_texto(TELA, ">", arial, VERDE, (LARGURA_TELA//10 + 60, int(ALTURA_TELA*0.95))) 


# Espera por botao específico
def esperar_tecla(botao):
    esperando = True
    while esperando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == USEREVENT_BOTAO and evento.botao == botao:
                esperando = False

#####################
#    FIM FUNCOES    #
#####################












###################
#      TELAS      #
###################


# Menu Principal
def menu_principal():
    global LER
    global file_musica
    pygame.mixer.music.play(-1)
    opcoes = ["Jogar", "Músicas", "Tutorial", "Configurações", "Sair"]
    N_opcoes = len(opcoes)
    selecao = 0
    musica = 0
    file_musica = "Happy_Birthday.mid"
    
    SAIR_DO_JOGO = False

    while SAIR_DO_JOGO == False:
        TELA.fill(BEGE)
        desenhar_texto(TELA, NOME_DO_JOGO, FONTE_GRANDE, MARROM, (LARGURA_TELA//2, ALTURA_TELA//3))
        desenhar_direcionais(TELA)
        
        for i, opcao in enumerate(opcoes):
            cor = BRANCO if i == selecao else CINZA
            desenhar_texto(TELA, opcao, FONTE, cor, (LARGURA_TELA//2, ALTURA_TELA//2 + i*40))

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
                            musica, file_musica = selecionar_musica(musica)
                        case 2:
                            pass # Tutorial
                        case 3:
                            pygame.mixer.music.pause()
                            configuracoes()
                            pygame.mixer.music.unpause()
                        case 4:
                            SAIR_DO_JOGO = True


def selecionar_musica(index):
    global notasjson 
    opcoes = ["Happy Birthday", "M2", "M3", "M4"]

    while True:
        TELA.fill(BEGE)
        desenhar_texto(TELA, "Músicas", FONTE_GRANDE, MARROM, (LARGURA_TELA//2, ALTURA_TELA//3))
        desenhar_texto(TELA, "Pressione o botão preto para sair", FONTE_PEQUENA, CINZA, (LARGURA_TELA//2, 4*ALTURA_TELA//5))

        desenhar_direcionais(TELA)

        desenhar_texto(TELA, "<  " + opcoes[index] + "  >", FONTE, BRANCO, (LARGURA_TELA//2, ALTURA_TELA//2))
        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == USEREVENT_BOTAO:
                if evento.botao == BOT_AMARELO:
                    index = (index - 1) % 4
                elif evento.botao == BOT_AZUL:
                    index = (index + 1) % 4
                elif evento.botao == BOT_PRETO:
                    match index:
                        case 0:
                            return index, "Happy_Birthday.mid"
                        case 1:
                            return index, "M2.mid"
                        case _:
                            print("ERROR")

                    with open("notas.json", "r") as f:
                                notasjson = json.load(f)

                    return index,""

# Tela de Configurações
def configuracoes():
    global NOTA_VOLUME
    global MAX_ERROS
    musica_volume = pygame.mixer.music.get_volume()
    tecla_volume = SONS[0].get_volume()
    selecao = 0

    while True:
        TELA.fill(BEGE)
        desenhar_texto(TELA, "Configurações", FONTE_GRANDE, MARROM, (LARGURA_TELA//2, 80))
        desenhar_direcionais(TELA)

        opcoes = [f"Música de fundo: {int(musica_volume*100)}%", f"Efeitos sonoros de menu: {int(tecla_volume*100)}%", f"Volume das notas: {int(NOTA_VOLUME*100)}%", f"Erros permitidos: {MAX_ERROS}", "Voltar"]
        for i, texto in enumerate(opcoes):
            cor = BRANCO if i == selecao else CINZA
            desenhar_texto(TELA, texto, FONTE, cor, (LARGURA_TELA//2, 200 + i * 40))

        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == USEREVENT_BOTAO:
                if evento.botao == BOT_AMARELO:
                    selecao = (selecao - 1) % 5
                elif evento.botao == BOT_AZUL:
                    selecao = (selecao + 1) % 5
                elif evento.botao == BOT_VERMELHO:
                    match selecao:
                        case 0:
                            musica_volume = max(0.0, musica_volume - 0.05)
                            pygame.mixer.music.set_volume(musica_volume)
                        case 1:
                            tecla_volume = max(0.0, tecla_volume - 0.05)
                            for s in SONS:
                                s.set_volume(tecla_volume)
                            # sons[0].play()
                        case 2:
                            NOTA_VOLUME = max(0.0, NOTA_VOLUME - 0.05)
                        case 3:
                            MAX_ERROS = max(MAX_ERROS - 1, 1)
                elif evento.botao == BOT_VERDE:
                    match selecao:
                        case 0:
                            musica_volume = min(1.0, musica_volume + 0.05)
                            pygame.mixer.music.set_volume(musica_volume)
                        case 1:
                            tecla_volume = max(0.0, tecla_volume + 0.05)
                            for s in SONS:
                                s.set_volume(tecla_volume)
                            # sons[0].play()
                        case 2:
                            NOTA_VOLUME = min(1.0, NOTA_VOLUME + 0.05)
                        case 3:
                            MAX_ERROS+=1
                elif evento.botao == BOT_PRETO:
                    return


def contagem_regressiva(TELA):
    TELA.fill(BEGE)
    desenhar_texto(TELA, "3", FONTE_GRANDE, MARROM, (LARGURA_TELA//2, ALTURA_TELA//3))
    pygame.display.flip()
    pygame.time.delay(1000)
    TELA.fill(BEGE)
    desenhar_texto(TELA, "2", FONTE_GRANDE, MARROM, (LARGURA_TELA//2, ALTURA_TELA//3))
    pygame.display.flip()
    pygame.time.delay(1000)
    TELA.fill(BEGE)
    desenhar_texto(TELA, "1", FONTE_GRANDE, MARROM, (LARGURA_TELA//2, ALTURA_TELA//3))
    pygame.display.flip()
    pygame.time.delay(1000)

# Tela de início
def tela_inicio():
    global notasjson
    global file_musica
    TELA.fill(BEGE)
    desenhar_texto(TELA, NOME_DO_JOGO, FONTE_GRANDE, MARROM, (LARGURA_TELA//2, ALTURA_TELA//3))
    desenhar_texto(TELA, "Para começar", FONTE, CINZA, (LARGURA_TELA//2, ALTURA_TELA//2))
    desenhar_texto(TELA, "Pressione o botão preto", FONTE, CINZA, (LARGURA_TELA//2, ALTURA_TELA//2 +30))
    pygame.display.flip()
    esperar_tecla(BOT_PRETO)
    extract.mid_to_json(file_musica)
    with open("notas.json", "r") as f:
        notasjson = json.load(f)
    contagem_regressiva(TELA)


# Tela de pause
def tela_pause():
    TELA.fill(BEGE)
    desenhar_texto(TELA, "Jogo pausado.", FONTE_GRANDE, MARROM, (LARGURA_TELA//2, ALTURA_TELA//3 + 40))
    desenhar_texto(TELA, "Para retomar", FONTE, CINZA, (LARGURA_TELA//2, ALTURA_TELA//2))
    desenhar_texto(TELA, "Pressione o botão preto", FONTE, CINZA, (LARGURA_TELA//2, ALTURA_TELA//2 +30))
    pygame.display.flip()
    esperar_tecla(BOT_PRETO)
    contagem_regressiva(TELA)


# Tela de derrota
def tela_derrota(pontos):
    TELA.fill(BEGE)
    desenhar_texto(TELA, "Fim de Jogo!", FONTE_GRANDE, VERMELHO, (LARGURA_TELA//2, ALTURA_TELA//3))
    desenhar_texto(TELA, f"Pontos: {pontos}", FONTE, CINZA, (LARGURA_TELA//2, ALTURA_TELA//2))
    desenhar_texto(TELA, "Pressione o botão preto para sair", FONTE, CINZA, (LARGURA_TELA//2, ALTURA_TELA//2 + 40))
    pygame.display.flip()
    esperar_tecla(BOT_PRETO)


# Tela de vitória
def tela_vitoria(pontos):
    TELA.fill(BEGE)
    desenhar_texto(TELA, "Parabéns!", FONTE_GRANDE, VERMELHO, (LARGURA_TELA//2, ALTURA_TELA//3))
    desenhar_texto(TELA, "Você venceu!", FONTE_GRANDE, VERMELHO, (LARGURA_TELA//2, ALTURA_TELA//3 + 50))
    desenhar_texto(TELA, f"Pontos: {pontos}", FONTE, CINZA, (LARGURA_TELA//2, ALTURA_TELA//2))
    desenhar_texto(TELA, "Pressione o botão preto para sair", FONTE, CINZA, (LARGURA_TELA//2, ALTURA_TELA//2 + 40))
    pygame.display.flip()
    esperar_tecla(BOT_PRETO)


# Função principal do jogo
def jogar():
    global notasjson
    notas_index = 0
    # tempo0 = pygame.time.get_ticks() # Para futuras implementações
    notas = []
    pontos = 0
    erros = 0
    fim = 200
    inicio_musica = None
    inicio_jogo = pygame.time.get_ticks()
    coluna_ultima = 0
    intervalo = 700

    tela_inicio()

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
        desenhar_texto(TELA, "||", FONTE, BRANCO, (LARGURA_TELA-35, 25))
        desenhar_texto(TELA, "BOTÃO", pygame.font.SysFont("Algerian", 14), BRANCO, (LARGURA_TELA-35, 55))
        desenhar_texto(TELA, "PRETO", pygame.font.SysFont("Algerian", 14), BRANCO, (LARGURA_TELA-35, 70))

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT: # não eh pra acontecer, mas deixa por precaucao <3
                pygame.quit()
                arduino.close()
                sys.exit()
            elif evento.type == USEREVENT_BOTAO:

                # Jogo pausado
                if evento.botao == BOT_PRETO:
                    tela_pause()  # Sai da função quando o jogo é despausado
                        
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
                        mostrar_erro(TELA, idx)
                        erros += 1
                if erros >= MAX_ERROS:
                    # pygame.mixer.music.stop()
                    tela_derrota(pontos)
                    return        

        
        # Atualiza notas na tela
        for nota in notas[:]:
            nota.atualizar()
            nota.desenhar(TELA)
            if nota.y > ALTURA_TELA:
                mostrar_erro(TELA, nota.coluna)
                notas.remove(nota)
                erros += 1
                if erros >= MAX_ERROS:
                    # pygame.mixer.music.stop()
                    tela_derrota(pontos)
                    return

        # Atualiza notas em som
        atualizar_notas()

        # Gera nova nota
        # if agora - tempo_ultima > intervalo and notas_index < len(notasjson):    
        if notas_index == 0: 
            if agora - inicio_jogo >= intervalo:
                notas.append(Nota(notas_index))
                inicio_musica = agora
                notas_index+=1
        elif notas_index < len(notasjson) and agora - inicio_musica >= int(notasjson[notas_index][0]["inicio"]*1000):    
            notas.append(Nota(notas_index))
            notas_index+=1
        

        # Carrega a tela de vitória
        if notas_index >= len(notasjson):
            fim -= 1
            if fim == 0:
                tela_vitoria(pontos)
                return

        # Pontuação e erros em tempo real
        desenhar_texto(TELA, f"Pontos: {pontos}", FONTE, BRANCO, (90, 20))
        desenhar_texto(TELA, f"Erros: {erros}/{MAX_ERROS}", FONTE, VERMELHO, (90, 50))

        pygame.display.flip()
        clock.tick(FPS)


#####################
#    FIM TELAS      #
#####################















###################
#      MAIN      #
###################

menu_principal()

LER = False
arduino.close()
pygame.quit()
sys.exit()
