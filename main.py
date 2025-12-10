"""
Dino Runner - Jogo de plataforma
Arquivo principal
"""
import pygame
from config import (
    LARGURA, ALTURA, LARGURA_VIRTUAL, ALTURA_VIRTUAL, FPS,
    ICONE_VIDA_ESPACAMENTO, ICONE_VIDA_MARGEM_X, ICONE_VIDA_MARGEM_Y
)
from assets import Assets
from mapa import Mapa
from jogador import Jogador
from camera import Camera
from camera import Camera
from meteoro import GerenciadorMeteoros
from ovo import GerenciadorOvos
from fogo import GerenciadorFogo

class Jogo:
    """Classe principal do jogo"""
    
    def __init__(self):
        pygame.init()
        
        # Configurar tela
        self.tela = pygame.display.set_mode(
            (LARGURA, ALTURA),
            pygame.SCALED | pygame.RESIZABLE,
            vsync=1
        )
        pygame.display.set_caption("Dino Runner - Modular")
        
        # Superfície virtual para pixel art
        self.superficie_virtual = pygame.Surface((LARGURA_VIRTUAL, ALTURA_VIRTUAL))
        
        # Carregar recursos
        self.assets = Assets()
        
        # Criar mapa
        self.mapa = Mapa('mapa_15x120.txt', self.assets)
        
        # Criar jogador
        self.jogador = Jogador(50, 100, self.assets)
        
        # Criar câmera
        self.camera = Camera(self.mapa.largura_px, self.mapa.altura_px)
        
        # Criar gerenciador de meteoros
        self.gerenciador_meteoros = GerenciadorMeteoros(self.assets, self.mapa.largura_px)
        
        # Criar gerenciador de ovos
        self.gerenciador_ovos = GerenciadorOvos(self.assets)
        posicoes_ovos = self.mapa.extrair_ovos()
        self.gerenciador_ovos.adicionar_ovos(posicoes_ovos)
        
        # Criar gerenciador de fogo
        self.gerenciador_fogo = GerenciadorFogo(self.assets)
        
        # Fonte para Game Over
        self.fonte_game_over = pygame.font.Font(None, 20)
        self.fonte_hud = pygame.font.Font(None, 16)
        
        # Controles
        self.relogio = pygame.time.Clock()
        self.rodando = True
        self.game_over = False
    
    def processar_eventos(self):
        """Processa eventos do pygame"""
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.rodando = False
            
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    self.rodando = False
                if evento.key in (pygame.K_SPACE, pygame.K_UP):
                    if not self.game_over:
                        self.jogador.pular()
                if evento.key == pygame.K_LSHIFT:
                    if not self.game_over:
                        self.jogador.iniciar_dash()
                if evento.key == pygame.K_r and self.game_over:
                    self.reiniciar()
    
    def reiniciar(self):
        """Reinicia o jogo"""
        self.jogador = Jogador(50, 100, self.assets)
        self.gerenciador_meteoros = GerenciadorMeteoros(self.assets, self.mapa.largura_px)
        
        # Recarregar ovos
        self.gerenciador_ovos = GerenciadorOvos(self.assets)
        # Precisamos recarregar o mapa para recuperar os ovos originais
        self.mapa = Mapa('mapa_15x120.txt', self.assets)
        posicoes_ovos = self.mapa.extrair_ovos()
        self.gerenciador_ovos.adicionar_ovos(posicoes_ovos)
        
        self.gerenciador_fogo = GerenciadorFogo(self.assets)
        
        self.game_over = False
    
    def atualizar(self):
        """Atualiza a lógica do jogo"""
        if self.game_over:
            return
        
        teclas = pygame.key.get_pressed()
        
        # 1. Atualiza jogador
        self.jogador.atualizar(teclas, self.mapa)
        
        # 2. Atualiza câmera (focada no jogador)
        self.camera.atualizar(self.jogador.x, self.jogador.y)
        
        # 3. Atualiza meteoros
        impactos = self.gerenciador_meteoros.atualizar(self.mapa, self.camera.x)
        
        # Criar fogo onde meteoros caíram
        for rect_colisao in impactos:
            self.gerenciador_fogo.adicionar_fogo(rect_colisao)
        
        # 4. Verifica colisão com meteoros
        if self.gerenciador_meteoros.verificar_colisao_jogador(self.jogador.get_hitbox()):
            self.jogador.receber_dano()
            
        # 5. Atualiza ovos
        self.gerenciador_ovos.atualizar(self.jogador.get_hitbox())
        
        # 6. Atualiza fogo e verifica colisão
        if self.gerenciador_fogo.atualizar(self.jogador.get_hitbox()):
            self.jogador.receber_dano()
        
        # 7. Verifica Game Over (espera animação terminar)
        if self.jogador.morto and self.jogador.animacao_morte_completa:
            self.game_over = True
    
    def desenhar_hud(self):
        """Desenha a interface (vidas)"""
        x = ICONE_VIDA_MARGEM_X
        y = ICONE_VIDA_MARGEM_Y
        
        for i in range(self.jogador.vidas):
            self.superficie_virtual.blit(self.assets.icone_vida, (x, y))
            x += ICONE_VIDA_ESPACAMENTO
            
        # Desenhar contador de ovos
        # Usar o primeiro frame do ovo como ícone
        icone_ovo = self.assets.ovo_sprites[0]
        # Reduzir para 16x16
        icone_ovo = pygame.transform.scale(icone_ovo, (16, 16))
        
        texto_ovos = f"x {self.gerenciador_ovos.ovos_coletados}"
        superficie_texto = self.fonte_hud.render(texto_ovos, True, (255, 255, 255))
        
        largura_texto = superficie_texto.get_width()
        altura_texto = superficie_texto.get_height()
        
        # Ajustar posição
        x_ovo = LARGURA_VIRTUAL - 30 - largura_texto
        y_ovo = 5
        
        # Centralizar verticalmente o texto em relação ao ícone (16px)
        offset_y_texto = (16 - altura_texto) // 2
        
        self.superficie_virtual.blit(icone_ovo, (x_ovo, y_ovo)) 
        # Reduzir espaçamento para 18px (ícone tem 16px, então 2px de gap)
        self.superficie_virtual.blit(superficie_texto, (x_ovo + 18, y_ovo + offset_y_texto))
    
    def desenhar_game_over(self):
        """Desenha a tela de Game Over"""
        # Overlay semi-transparente
        overlay = pygame.Surface((LARGURA_VIRTUAL, ALTURA_VIRTUAL))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.superficie_virtual.blit(overlay, (0, 0))
        
        # Texto Game Over
        texto_go = self.fonte_game_over.render("GAME OVER", True, (255, 255, 255))
        texto_rect_go = texto_go.get_rect(center=(LARGURA_VIRTUAL // 2, ALTURA_VIRTUAL // 2 - 15))
        self.superficie_virtual.blit(texto_go, texto_rect_go)
        
        # Texto reiniciar
        texto_r = self.fonte_game_over.render("Pressione R para reiniciar", True, (255, 255, 255))
        texto_rect_r = texto_r.get_rect(center=(LARGURA_VIRTUAL // 2, ALTURA_VIRTUAL // 2 + 5))
        self.superficie_virtual.blit(texto_r, texto_rect_r)
    
    def desenhar(self):
        """Desenha todos os elementos do jogo"""
        # Desenhar mapa na superfície virtual
        self.superficie_virtual.blit(
            self.mapa.superficie,
            (0, 0),
            (self.camera.x, self.camera.y, LARGURA_VIRTUAL, ALTURA_VIRTUAL)
        )
        
        # Desenhar meteoros
        self.gerenciador_meteoros.desenhar(
            self.superficie_virtual,
            self.camera.x,
            self.camera.y
        )
        
        # Desenhar ovos
        self.gerenciador_ovos.desenhar(
            self.superficie_virtual,
            self.camera.x,
            self.camera.y
        )
        
        # Desenhar fogo
        self.gerenciador_fogo.desenhar(
            self.superficie_virtual,
            self.camera.x,
            self.camera.y
        )
        
        # Desenhar jogador
        self.jogador.desenhar(
            self.superficie_virtual,
            self.camera.x,
            self.camera.y
        )
        
        # Desenhar HUD
        self.desenhar_hud()
        
        # Desenhar Game Over se necessário
        if self.game_over:
            self.desenhar_game_over()
        
        # Escalar e desenhar na tela real
        superficie_zoom = pygame.transform.scale(
            self.superficie_virtual,
            (LARGURA, ALTURA)
        )
        self.tela.blit(superficie_zoom, (0, 0))
        
        pygame.display.flip()
    
    def executar(self):
        """Loop principal do jogo"""
        while self.rodando:
            self.processar_eventos()
            self.atualizar()
            self.desenhar()
            self.relogio.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__":
    jogo = Jogo()
    jogo.executar()