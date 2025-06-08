import pygame
import pygame.midi
import json
import sys
import extract
import db_functions
from constants import PATH_MUSICA, PATH_IMAGEM_FUNDO_PRINCIPAL, PATH_MUSICA_FUNDO, PATH_NOTAS_JSON
from constants import NOME_JOGO, MAX_ERROS, FPS
from constants import VERDE, AZUL, AMARELO, VERMELHO, PRETO, CINZA, BRANCO, MARROM, BEGE
from constants import FONTE_MUITO_PEQUENA, FONTE_PEQUENA, FONTE, FONTE_GRANDE
from constants import ALTURA_TELA, LARGURA_TELA, ALTURA_LINHA_ACERTO, LARGURA_COLUNA, N_COLUNAS
from constants import NOTA_VOLUME, EFEITOS_SONOROS_VOLUME, MUSICA_FUNDO_VOLUME, SONS




############################
# Init pygame e Constantes #
############################

# Carrega as notas musicais
extract.mid_to_json(PATH_MUSICA)
with open(PATH_NOTAS_JSON, "r") as f:
    notasjson = json.load(f)

# Inicialização pygame
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

# Teclas
TECLAS = [pygame.K_q, pygame.K_w, pygame.K_e, pygame.K_r]

# Identificador da musica
Numero_musica = 0

###################
#  FIM INIT + CTE #
###################












########################
#  FUNCOES E CLASSES   #
########################

# Função que emite o som da nota 
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


# Função que gerencia as durações das notas
def atualizar_notas():
    agora = pygame.time.get_ticks()
    for nota in notas_ativas[:]:  # copia da lista para remover com segurança
        if agora >= nota["desligar_em"]:
            player.note_off(nota["nota"], nota["velocidade"])
            notas_ativas.remove(nota)


# Classe Nota
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


def mostrar_erro(TELA, coluna):
    for i in range(1000):
        pygame.draw.rect(TELA, VERMELHO, (coluna*LARGURA_COLUNA, 0, LARGURA_COLUNA, 600))


def desenhar_texto(TELA, texto, fonte, cor, centro):
    render = fonte.render(texto, True, cor)
    rect = render.get_rect(center=centro)
    TELA.blit(render, rect)


def desenhar_direcionais(TELA):
    pygame.draw.rect(TELA, MARROM, (10, int(ALTURA_TELA*0.85) - 30, 175, 110)) 
    desenhar_texto(TELA, "PRETO: SELECIONAR", FONTE_MUITO_PEQUENA, PRETO, (LARGURA_TELA//10 + 44, int(ALTURA_TELA*0.83)))
    desenhar_texto(TELA, "VERMELHO: ESQUERDA", FONTE_MUITO_PEQUENA, VERMELHO, (LARGURA_TELA//10 + 52, int(ALTURA_TELA*0.83) + 20))
    desenhar_texto(TELA, "AMARELO: CIMA", FONTE_MUITO_PEQUENA, AMARELO, (LARGURA_TELA//10 + 30, int(ALTURA_TELA*0.83) + 40))
    desenhar_texto(TELA, "AZUL: BAIXO", FONTE_MUITO_PEQUENA, AZUL, (LARGURA_TELA//10 + 16, int(ALTURA_TELA*0.83) + 60))
    desenhar_texto(TELA, "VERDE: DIREITA", FONTE_MUITO_PEQUENA, VERDE, (LARGURA_TELA//10 + 27, int(ALTURA_TELA*0.83) + 80)) 


# Espera por tecla específica
def esperar_tecla(tecla):
    esperando = True
    while esperando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.KEYDOWN and evento.key == tecla:
                esperando = False


#####################
#    FIM FUNCOES    #
#####################













###################
#      TELAS      #
###################


def menu_principal():
    global Numero_musica

    pygame.mixer.music.play(-1)
    
    opcoes = ["Jogar", "Músicas", "Tutorial", "Configurações", "Sair"]
    N_opcoes = len(opcoes)
    selecao = 0

    SAIR_DO_JOGO = False

    while SAIR_DO_JOGO == False:
        
        # Desenha o fundo personalizado para essa tela
        TELA.blit(FUNDO_CARREGADO, (0, 0))

        desenhar_texto(TELA, NOME_JOGO, FONTE_GRANDE, MARROM, (LARGURA_TELA//2, ALTURA_TELA//3 - 10))
        desenhar_direcionais(TELA)
        
        for i, opcao in enumerate(opcoes):
            cor = BRANCO if i == selecao else CINZA
            desenhar_texto(TELA, opcao, FONTE, cor, (LARGURA_TELA//2, ALTURA_TELA//2 - 50 + i*40))
        
        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                SAIR_DO_JOGO = True
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_UP:
                    SONS[0].play()
                    selecao = (selecao - 1) % N_opcoes
                elif evento.key == pygame.K_DOWN:
                    SONS[2].play()
                    selecao = (selecao + 1) % N_opcoes
                elif evento.key == pygame.K_RETURN:
                    SONS[3].play()
                    match selecao:
                        case 0:
                            pygame.mixer.music.pause()
                            jogar()
                            pygame.mixer.music.unpause()
                        case 1:
                            Numero_musica = selecionar_musica(Numero_musica)
                        case 2:
                            pass # Tutorial
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

    while True:
        TELA.fill(BEGE)
        desenhar_texto(TELA, "Músicas", FONTE_GRANDE, MARROM, (LARGURA_TELA//2, ALTURA_TELA//3))
        desenhar_texto(TELA, "Pressione a tecla ENTER para sair", FONTE_PEQUENA, CINZA, (LARGURA_TELA//2, 4*ALTURA_TELA//5))

        desenhar_direcionais(TELA)

        desenhar_texto(TELA, "<  " + opcoes[index] + "  >", FONTE, BRANCO, (LARGURA_TELA//2, ALTURA_TELA//2))
        desenhar_texto(TELA, "Recorde : " + str(recordes[index]) + " pontos", FONTE, CINZA, (LARGURA_TELA//2, ALTURA_TELA//2 + 40))
        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_LEFT or evento.key == pygame.K_UP:
                    index = (index - 1) % N_opcoes
                elif evento.key == pygame.K_RIGHT or evento.key == pygame.K_DOWN:
                    index = (index + 1) % N_opcoes
                elif evento.key == pygame.K_RETURN or evento.key == pygame.K_ESCAPE:
                    return index
       

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

        opcoes = [f"Música de fundo: {int(musica_volume*100)}%", f"Efeitos sonoros de menu: {int(tecla_volume*100)}%", f"Volume das notas: {int(NOTA_VOLUME*100)}%", f"Erros permitidos: {MAX_ERROS}", "Limpar Recordes", "Voltar"]
        N_opcoes = len(opcoes)

        for i, texto in enumerate(opcoes):
            cor = BRANCO if i == selecao else CINZA
            desenhar_texto(TELA, texto, FONTE, cor, (LARGURA_TELA//2, 200 + i * 40))

        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_UP:
                    selecao = (selecao - 1) % N_opcoes
                elif evento.key == pygame.K_DOWN:
                    selecao = (selecao + 1) % N_opcoes
                elif evento.key == pygame.K_LEFT:
                    match selecao:
                        case 0:
                            MUSICA_FUNDO_VOLUME = max(0.0, MUSICA_FUNDO_VOLUME - 0.05)
                            pygame.mixer.music.set_volume(MUSICA_FUNDO_VOLUME)
                        case 1:
                            tecla_volume = max(0.0, tecla_volume - 0.05)
                            for s in SONS:
                                s.set_volume(tecla_volume)
                        case 2:
                            NOTA_VOLUME = max(0.0, NOTA_VOLUME - 0.05)
                        case 3:
                            MAX_ERROS = max(MAX_ERROS - 1, 1)
                elif evento.key == pygame.K_RIGHT:
                    match selecao:
                        case 0:
                            MUSICA_FUNDO_VOLUME = min(1.0, MUSICA_FUNDO_VOLUME + 0.05)
                            pygame.mixer.music.set_volume(MUSICA_FUNDO_VOLUME)
                        case 1:
                            tecla_volume = max(0.0, tecla_volume + 0.05)
                            for s in SONS:
                                s.set_volume(tecla_volume)
                        case 2:
                            NOTA_VOLUME = min(1.0, NOTA_VOLUME + 0.05)
                        case 3:
                            MAX_ERROS+=1
                elif evento.key == pygame.K_RETURN:
                    if selecao == 4:
                        db_functions.resetar_recordes()
                        desenhar_texto(TELA, "Recordes limpos.", FONTE, VERMELHO, (LARGURA_TELA//2, 500))
                        pygame.display.flip()
                        pygame.time.delay(400)
                    if selecao == 5:
                        return
                elif evento.key == pygame.K_ESCAPE:
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


def tela_aguardo():
    global notasjson
    global Numero_musica
    
    PATH_MUSICA = db_functions.obter_arquivo_musica(Numero_musica)

    TELA.fill(BEGE)
    desenhar_texto(TELA, "PoliTiles", FONTE_GRANDE, MARROM, (LARGURA_TELA//2, ALTURA_TELA//3))
    desenhar_texto(TELA, "Pressione ENTER para começar", FONTE, CINZA, (LARGURA_TELA//2, ALTURA_TELA//2))
    pygame.display.flip()
    esperar_tecla(pygame.K_RETURN)

    extract.mid_to_json(PATH_MUSICA)
    with open(PATH_NOTAS_JSON, "r") as f:
        notasjson = json.load(f)

    contagem_regressiva(TELA)
    return


def tela_pause():
    TELA.fill(BEGE)
    desenhar_texto(TELA, "Jogo pausado.", FONTE_GRANDE, MARROM, (LARGURA_TELA//2, ALTURA_TELA//3 + 40))
    desenhar_texto(TELA, "Pressione ESPAÇO para retomar", FONTE, CINZA, (LARGURA_TELA//2, ALTURA_TELA//2))
    pygame.display.flip()
    esperar_tecla(pygame.K_SPACE)
    contagem_regressiva(TELA)


def tela_derrota():
    TELA.fill(BEGE)
    desenhar_texto(TELA, "Fim de Jogo!", FONTE_GRANDE, VERMELHO, (LARGURA_TELA//2, ALTURA_TELA//3))
    desenhar_texto(TELA, "Você perdeu", FONTE_GRANDE, VERMELHO, (LARGURA_TELA//2, ALTURA_TELA//3 + 70))
    desenhar_texto(TELA, "Pressione ENTER para sair", FONTE, CINZA, (LARGURA_TELA//2, ALTURA_TELA//2 + 40))
    pygame.display.flip()
    esperar_tecla(pygame.K_RETURN)


def tela_vitoria(pontos : int):
    global Numero_musica
    TELA.fill(BEGE)
    if db_functions.obter_recorde_musica(Numero_musica) <= pontos:
        db_functions.atualizar_recorde(Numero_musica, pontos)
        desenhar_texto(TELA, "Parabéns!", FONTE_GRANDE, VERMELHO, (LARGURA_TELA//2, ALTURA_TELA//3 - 40))
        desenhar_texto(TELA, "Você venceu!", FONTE_GRANDE, VERMELHO, (LARGURA_TELA//2, ALTURA_TELA//3))
        desenhar_texto(TELA, "Novo Recorde!", FONTE_GRANDE, VERMELHO, (LARGURA_TELA//2, ALTURA_TELA//3 + 40))
    else:
        desenhar_texto(TELA, "Parabéns!", FONTE_GRANDE, VERMELHO, (LARGURA_TELA//2, ALTURA_TELA//3))
        desenhar_texto(TELA, "Você venceu!", FONTE_GRANDE, VERMELHO, (LARGURA_TELA//2, ALTURA_TELA//3 + 40))

    desenhar_texto(TELA, f"Pontos: {pontos}", FONTE, CINZA, (LARGURA_TELA//2, ALTURA_TELA//2))
    desenhar_texto(TELA, "Pressione ENTER para sair", FONTE, CINZA, (LARGURA_TELA//2, ALTURA_TELA//2 + 40))
    pygame.display.flip()
    esperar_tecla(pygame.K_RETURN)


# Função operacional do jogo
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
    intervalo = 700

    tela_aguardo()

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
        desenhar_texto(TELA, "Espaço", pygame.font.SysFont("Algerian", 14), BRANCO, (LARGURA_TELA-35, 55))

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE: # Jogo pausado
                        tela_pause() # Sai da função quando o jogo é despausado     
                if evento.key in TECLAS:
                    idx = TECLAS.index(evento.key)
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
                            tela_derrota()
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
                    tela_derrota()
                    return

        # Atualiza notas em som
        atualizar_notas()

        # Gera nova nota        
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


###################
#    FIM TELAS    #
###################








###################
#      MAIN      #
###################


# Início
menu_principal()

pygame.quit()
sys.exit()
