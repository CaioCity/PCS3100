import pygame
import pygame.midi
import json
import sys


# Carrega as notas musicais
with open("notas.json", "r") as f:
    notasjson = json.load(f)

# Inicialização
pygame.init()
pygame.midi.init()
player = pygame.midi.Output(pygame.midi.get_default_output_id())
player.set_instrument(0)

LARGURA, ALTURA = 460, 600
ALTURA_ACERTO = ALTURA - 100
MAX_ERROS = 5
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("PoliTiles")
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
fonte_pequena = pygame.font.SysFont("Algerian", 20)
fonte = pygame.font.SysFont("Algerian", 24)
fonte_grande = pygame.font.SysFont("Algerian", 36)

# Colunas e teclas
COLUNAS = 4
LARGURA_COLUNA = LARGURA // COLUNAS
TECLAS = [pygame.K_q, pygame.K_w, pygame.K_e, pygame.K_r]

# Sons
pygame.mixer.init()
notas_ativas = []
NOTA_VOLUME = 0.5

# Gerar um "som ao toque" para os botões no menu
sons = [
    pygame.mixer.Sound('piano1.wav'),
    pygame.mixer.Sound('piano2.wav'),
    pygame.mixer.Sound('piano3.wav'),
    pygame.mixer.Sound('piano4.wav')
]

# Música de fundo
pygame.mixer.music.load('moonlight-sonata-classical-piano-beethoven.mp3')
pygame.mixer.music.set_volume(0.05)
for s in sons:
    s.set_volume(0.05)



#####################
#     FUNCOES       #
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
        return self.y + self.raio >= ALTURA_ACERTO and self.y - self.raio <= ALTURA_ACERTO
    
    def calcular_pontos(self):
        return int(100* (ALTURA_ACERTO - (self.y - self.raio))/(2*self.raio))


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
    pygame.draw.rect(TELA, MARROM, (10, int(ALTURA*0.95) - 30, 130, 45))
    desenhar_texto(TELA, "Direcionais:", fonte_pequena, PRETO, (LARGURA//10 + 30, int(ALTURA*0.95) - 20))
    desenhar_texto(TELA, "<", arial, VERMELHO, (LARGURA//10, int(ALTURA*0.95)))
    desenhar_texto(TELA, "^", arial, AMARELO, (LARGURA//10 + 20, int(ALTURA*0.95) + 5))
    desenhar_texto(TELA, "v", arial, AZUL, (LARGURA//10 + 40, int(ALTURA*0.95)))
    desenhar_texto(TELA, ">", arial, VERDE, (LARGURA//10 + 60, int(ALTURA*0.95))) 


# Menu Principal
def menu_principal():
    pygame.mixer.music.play(-1)
    opcoes = ["Jogar", "Níveis", "Tutorial", "Configurações"]
    selecao = 0

    while True:
        TELA.fill(BEGE)
        desenhar_texto(TELA, "PoliTiles", fonte_grande, MARROM, (LARGURA//2, ALTURA//3))
        desenhar_direcionais(TELA)
        
        for i, opcao in enumerate(opcoes):
            cor = BRANCO if i == selecao else CINZA
            desenhar_texto(TELA, opcao, fonte, cor, (LARGURA//2, ALTURA//2 + i*40))
        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_UP:
                    sons[0].play()
                    selecao = (selecao - 1) % 4
                elif evento.key == pygame.K_DOWN:
                    sons[2].play()
                    selecao = (selecao + 1) % 4
                elif evento.key == pygame.K_RETURN:
                    sons[3].play()
                    match selecao:
                        case 0:
                            pygame.mixer.music.pause()
                            jogar()
                            pygame.mixer.music.unpause()
                        case 1:
                            pass # Selecionar nível
                        case 2:
                            pass # Tutorial
                        case 3:
                            pygame.mixer.music.pause()
                            configuracoes()
                            pygame.mixer.music.unpause()


# Tela de Configurações
def configuracoes():
    musica_volume = pygame.mixer.music.get_volume()
    global NOTA_VOLUME
    tecla_volume = sons[0].get_volume()
    selecao = 0
    global MAX_ERROS

    while True:
        TELA.fill(BEGE)
        desenhar_texto(TELA, "Configurações", fonte_grande, MARROM, (LARGURA//2, 80))
        desenhar_direcionais(TELA)

        opcoes = [f"Música de fundo: {int(musica_volume*100)}%", f"Efeitos sonoros de menu: {int(tecla_volume*100)}%", f"Notas: {int(NOTA_VOLUME*100)}%", f"Erros permitidos: {MAX_ERROS}", "Voltar"]
        for i, texto in enumerate(opcoes):
            cor = BRANCO if i == selecao else CINZA
            desenhar_texto(TELA, texto, fonte, cor, (LARGURA//2, 200 + i * 40))

        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_UP:
                    selecao = (selecao - 1) % 5
                elif evento.key == pygame.K_DOWN:
                    selecao = (selecao + 1) % 5
                elif evento.key == pygame.K_LEFT:
                    match selecao:
                        case 0:
                            musica_volume = max(0.0, musica_volume - 0.05)
                            pygame.mixer.music.set_volume(musica_volume)
                        case 1:
                            tecla_volume = max(0.0, tecla_volume - 0.05)
                            for s in sons:
                                s.set_volume(tecla_volume)
                            # sons[0].play()
                        case 2:
                            NOTA_VOLUME = max(0.0, NOTA_VOLUME - 0.05)
                        case 3:
                            MAX_ERROS = max(MAX_ERROS - 1, 1)
                elif evento.key == pygame.K_RIGHT:
                    match selecao:
                        case 0:
                            musica_volume = min(1.0, musica_volume + 0.05)
                            pygame.mixer.music.set_volume(musica_volume)
                        case 1:
                            tecla_volume = max(0.0, tecla_volume + 0.05)
                            for s in sons:
                                s.set_volume(tecla_volume)
                            # sons[0].play()
                        case 2:
                            NOTA_VOLUME = min(1.0, NOTA_VOLUME + 0.05)
                        case 3:
                            MAX_ERROS+=1
                elif evento.key == pygame.K_ESCAPE:
                    return
                elif evento.key == pygame.K_RETURN and selecao == 4:
                    return


def contagem_regressiva(TELA):
    TELA.fill(BEGE)
    desenhar_texto(TELA, "3", fonte_grande, MARROM, (LARGURA//2, ALTURA//3))
    pygame.display.flip()
    pygame.time.delay(1000)
    TELA.fill(BEGE)
    desenhar_texto(TELA, "2", fonte_grande, MARROM, (LARGURA//2, ALTURA//3))
    pygame.display.flip()
    pygame.time.delay(1000)
    TELA.fill(BEGE)
    desenhar_texto(TELA, "1", fonte_grande, MARROM, (LARGURA//2, ALTURA//3))
    pygame.display.flip()
    pygame.time.delay(1000)

# Tela de início
def tela_inicio():
    TELA.fill(BEGE)
    desenhar_texto(TELA, "PoliTiles", fonte_grande, MARROM, (LARGURA//2, ALTURA//3))
    desenhar_texto(TELA, "Pressione ENTER para começar", fonte, CINZA, (LARGURA//2, ALTURA//2))
    pygame.display.flip()
    esperar_tecla(pygame.K_RETURN)
    contagem_regressiva(TELA)


# Tela de pause
def tela_pause():
    TELA.fill(BEGE)
    desenhar_texto(TELA, "Jogo pausado.", fonte_grande, MARROM, (LARGURA//2, ALTURA//3 + 40))
    desenhar_texto(TELA, "Pressione ESPAÇO para retomar", fonte, CINZA, (LARGURA//2, ALTURA//2))
    pygame.display.flip()
    esperar_tecla(pygame.K_SPACE)


# Tela de derrota
def tela_derrota(pontos):
    TELA.fill(BEGE)
    desenhar_texto(TELA, "Fim de Jogo!", fonte_grande, VERMELHO, (LARGURA//2, ALTURA//3))
    desenhar_texto(TELA, f"Pontos: {pontos}", fonte, CINZA, (LARGURA//2, ALTURA//2))
    desenhar_texto(TELA, "Pressione ENTER para sair", fonte, CINZA, (LARGURA//2, ALTURA//2 + 40))
    pygame.display.flip()
    esperar_tecla(pygame.K_RETURN)


# Tela de vitória
def tela_vitoria(pontos):
    TELA.fill(BEGE)
    desenhar_texto(TELA, "Parabéns!", fonte_grande, VERMELHO, (LARGURA//2, ALTURA//3))
    desenhar_texto(TELA, "Você venceu!", fonte_grande, VERMELHO, (LARGURA//2, ALTURA//3 + 50))
    desenhar_texto(TELA, f"Pontos: {pontos}", fonte, CINZA, (LARGURA//2, ALTURA//2))
    desenhar_texto(TELA, "Pressione ENTER para sair", fonte, CINZA, (LARGURA//2, ALTURA//2 + 40))
    pygame.display.flip()
    esperar_tecla(pygame.K_RETURN)


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
    # pygame.mixer.music.play(-1)

    while True:
        TELA.fill(BEGE)
        agora = pygame.time.get_ticks()

        # Linhas verticais
        for i in range(1, COLUNAS):
            pygame.draw.line(TELA, CINZA, (i*LARGURA_COLUNA, 0), (i*LARGURA_COLUNA, ALTURA), 2)

        # Linha de acerto
        pygame.draw.rect(TELA, VERMELHO, (0, ALTURA_ACERTO, LARGURA, 5))

        # Botão de pausa
        pygame.draw.rect(TELA, CINZA, (LARGURA-60, 13, 50, 30))
        desenhar_texto(TELA, "||", fonte, BRANCO, (LARGURA-35, 25))
        desenhar_texto(TELA, "Espaço", pygame.font.SysFont("Algerian", 14), BRANCO, (LARGURA-35, 55))

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.KEYDOWN:
                # Jogo pausado
                if evento.key == pygame.K_SPACE:
                        # pygame.mixer.music.pause()
                        tela_pause()
                        # Sai da função quando o jogo é despausado
                        # pygame.mixer.music.unpause()
                        
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
                    # pygame.mixer.music.stop()
                    tela_derrota(pontos)
                    return        

        
        # Atualiza notas na tela
        for nota in notas[:]:
            nota.atualizar()
            nota.desenhar(TELA)
            if nota.y > ALTURA:
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
        desenhar_texto(TELA, f"Pontos: {pontos}", fonte, BRANCO, (90, 20))
        desenhar_texto(TELA, f"Erros: {erros}/{MAX_ERROS}", fonte, VERMELHO, (90, 50))

        pygame.display.flip()
        clock.tick(FPS)

# Início
menu_principal()
