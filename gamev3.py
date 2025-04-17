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

LARGURA, ALTURA = 400, 600
ALTURA_ACERTO = ALTURA - 100
MAX_ERROS = 20
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Piano Tiles")
clock = pygame.time.Clock()
FPS = 60

# Cores
PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)
AZUL = (65, 132, 233)
BEGE = (220,220,150)
VERMELHO = (200, 50, 50)
VERDE = (0, 200, 0)
CINZA = (100, 100, 100)
AMARELO = (255, 255, 0)

# Fontes
fonte = pygame.font.SysFont("Arial", 24)
fonte_grande = pygame.font.SysFont("Arial", 36)

# Colunas e teclas
COLUNAS = 4
LARGURA_COLUNA = LARGURA // COLUNAS
TECLAS = [pygame.K_q, pygame.K_w, pygame.K_e, pygame.K_r]

# Sons
pygame.mixer.init()
notas_ativas = []
NOTA_VOLUME = 1.0

# Posso usar isso gerar um "som ao toque" para os botões no menu
# sons = [
#     pygame.mixer.Sound('piano1.wav'),
#     pygame.mixer.Sound('piano2.wav'),
#     pygame.mixer.Sound('piano3.wav'),
#     pygame.mixer.Sound('piano4.wav')
# ]

# Música de fundo
# pygame.mixer.music.load('fundo.mp3')
# pygame.mixer.music.set_volume(0.10)
# for s in sons:
#     s.set_volume(0.2)



#####################
#     FUNCOES       #
#####################

# Função que emite o som da nota 
def tocar_nota(index):
    agora = pygame.time.get_ticks()
    nota = notasjson[index]
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
        self.coluna = notasjson[index]['coluna']
        self.x = self.coluna * LARGURA_COLUNA
        self.y = - min(400,max(200*notasjson[index]['M_altura'],100))
        self.largura = LARGURA_COLUNA
        self.altura = - self.y
        self.velocidade = 5

    def atualizar(self):
        self.y += self.velocidade

    def desenhar(self, tela):
        pygame.draw.rect(tela, PRETO, (self.x, self.y, self.largura, self.altura))

    # Retorna True se a nota tiver sido acertada
    def colidiu(self):
        return self.y + self.altura >= ALTURA - 100 and self.y <= ALTURA - 100
    
    def calcular_pontos(self):
        return int(100* (ALTURA_ACERTO - self.y)/self.altura)


# Função para desenhar erros
def mostrar_erro(tela, coluna):
    for i in range(1000):
        pygame.draw.rect(tela, VERMELHO, (coluna*LARGURA_COLUNA, 0, LARGURA_COLUNA, 600))


# Função para desenhar textos centralizados
def desenhar_texto(tela, texto, fonte, cor, centro):
    render = fonte.render(texto, True, cor)
    rect = render.get_rect(center=centro)
    tela.blit(render, rect)


# Menu Principal
def menu_principal():
    opcoes = ["Jogar", "Níveis", "Tutorial", "Configurações"]
    selecao = 0

    while True:
        TELA.fill(CINZA)
        desenhar_texto(TELA, "Piano Tiles", fonte_grande, PRETO, (LARGURA//2, ALTURA//3))
        for i, opcao in enumerate(opcoes):
            # cor = BRANCO if i == selecao else CINZA
            cor = PRETO
            match i:
                case 0:
                    cor = VERMELHO
                case 1:
                    cor = AMARELO
                case 2:
                    cor = AZUL
                case 3:
                    cor = VERDE
            desenhar_texto(TELA, opcao, fonte, cor, (LARGURA//2, ALTURA//2 + i*40))
        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                match evento.key:
                    case pygame.K_q:
                        selecao = 0
                        jogar()
                    case pygame.K_w:
                        pass # Selecionar nível
                    case pygame.K_e:
                        pass # Tutorial
                    case pygame.K_r:
                        configuracoes()


# Tela de Configurações
def configuracoes():
    musica_volume = pygame.mixer.music.get_volume()
    global NOTA_VOLUME
    # tecla_volume = sons[0].get_volume()
    selecao = 0
    global MAX_ERROS

    while True:
        TELA.fill(BEGE)
        desenhar_texto(TELA, "Configurações", fonte_grande, BRANCO, (LARGURA//2, 80))

        opcoes = [f"Música: {int(musica_volume*100)}%", f"Notas: {int(NOTA_VOLUME*100)}%", f"Erros permitidos: {MAX_ERROS}", "Voltar"]
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
                    selecao = (selecao - 1) % 4
                elif evento.key == pygame.K_DOWN:
                    selecao = (selecao + 1) % 4
                elif evento.key == pygame.K_LEFT:
                    match selecao:
                        case 0:
                            musica_volume = max(0.0, musica_volume - 0.05)
                            # pygame.mixer.music.set_volume(musica_volume)
                        case 1:
                            NOTA_VOLUME = max(0.0, NOTA_VOLUME - 0.05)
                            # sons[0].play()
                            # for s in sons:
                            #     s.set_volume(NOTA_VOLUME)
                            # Criar som exemplo
                        case 2:
                            MAX_ERROS-=1
                elif evento.key == pygame.K_RIGHT:
                    match selecao:
                        case 0:
                            musica_volume = min(1.0, musica_volume + 0.05)
                            # pygame.mixer.music.set_volume(musica_volume)
                        case 1:
                            NOTA_VOLUME = min(1.0, NOTA_VOLUME + 0.05)
                            # sons[0].play()
                            # for s in sons:
                            #     s.set_volume(NOTA_VOLUME)
                            # criar exemplo
                        case 2:
                            MAX_ERROS+=1
                elif evento.key == pygame.K_ESCAPE:
                    return
                elif evento.key == pygame.K_RETURN and selecao == 3:
                    return


# Tela de início
def tela_inicio():
    TELA.fill(CINZA)
    desenhar_texto(TELA, "Piano Tiles", fonte_grande, PRETO, (LARGURA//2, ALTURA//3))
    desenhar_texto(TELA, "Pressione ENTER para começar", fonte, PRETO, (LARGURA//2, ALTURA//2))
    pygame.display.flip()
    esperar_tecla(pygame.K_RETURN)


# Tela de pause
def tela_pause():
    TELA.fill(CINZA)
    desenhar_texto(TELA, "Jogo pausado.", fonte_grande, BRANCO, (LARGURA//2, ALTURA//3 + 40))
    desenhar_texto(TELA, "Pressione ESPAÇO para retomar", fonte, BRANCO, (LARGURA//2, ALTURA//2))
    pygame.display.flip()
    esperar_tecla(pygame.K_SPACE)


# Tela de derrota
def tela_derrota(pontos):
    TELA.fill(CINZA)
    desenhar_texto(TELA, "Fim de Jogo!", fonte_grande, VERMELHO, (LARGURA//2, ALTURA//3))
    desenhar_texto(TELA, f"Pontos: {pontos}", fonte, BRANCO, (LARGURA//2, ALTURA//2))
    desenhar_texto(TELA, "Pressione ENTER para sair", fonte, BRANCO, (LARGURA//2, ALTURA//2 + 40))
    pygame.display.flip()
    esperar_tecla(pygame.K_RETURN)


# Tela de vitória
def tela_vitoria(pontos):
    TELA.fill(CINZA)
    desenhar_texto(TELA, "Parabéns!", fonte_grande, VERMELHO, (LARGURA//2, ALTURA//3))
    desenhar_texto(TELA, "Você venceu!", fonte_grande, VERMELHO, (LARGURA//2, ALTURA//3 + 50))
    desenhar_texto(TELA, f"Pontos: {pontos}", fonte, BRANCO, (LARGURA//2, ALTURA//2))
    desenhar_texto(TELA, "Pressione ENTER para sair", fonte, BRANCO, (LARGURA//2, ALTURA//2 + 40))
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
        TELA.fill(AZUL)
        agora = pygame.time.get_ticks()

        # Linhas verticais
        for i in range(1, COLUNAS):
            pygame.draw.line(TELA, CINZA, (i*LARGURA_COLUNA, 0), (i*LARGURA_COLUNA, ALTURA), 2)

        # Linha de acerto
        pygame.draw.rect(TELA, VERMELHO, (0, ALTURA_ACERTO, LARGURA, 5))

        # Botão de pausa
        pygame.draw.rect(TELA, CINZA, (LARGURA-60, 13, 50, 30))
        desenhar_texto(TELA, "||", fonte, BRANCO, (LARGURA-35, 25))
        desenhar_texto(TELA, "Espaço", pygame.font.SysFont("Arial", 14), BRANCO, (LARGURA-35, 55))

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
        elif notas_index < len(notasjson) and agora - inicio_musica >= int(notasjson[notas_index]["inicio"]*1000):    
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
