"""
Sistema de fogo gerado por meteoros
"""
import pygame
from config import TILE_SIZE

class Fogo:
    """Representa um efeito de fogo no chão"""
    
    # Estados
    ESTADO_START = 0
    ESTADO_LOOP = 1
    ESTADO_END = 2
    
    def __init__(self, x, y, assets):
        self.x = x
        self.y = y
        self.assets = assets
        
        self.estado = self.ESTADO_START
        self.frame_atual = 0
        self.contador_animacao = 0
        self.velocidade_animacao = 5
        
        self.ativo = True
        # self.tempo_loop = 0
        # self.duracao_loop = 180  # Removido, agora roda apenas uma vez
        
        # Hitbox (menor que o sprite)
        self.largura = 14
        self.altura = 20
        self.offset_x = 5
        self.offset_y = 12
        
    def get_hitbox(self):
        """Retorna o retângulo de colisão"""
        return pygame.Rect(
            self.x + self.offset_x,
            self.y + self.offset_y,
            self.largura,
            self.altura
        )
        
    def atualizar(self):
        """Atualiza a animação e estado do fogo"""
        if not self.ativo:
            return
            
        self.contador_animacao += 1
        if self.contador_animacao >= self.velocidade_animacao:
            self.contador_animacao = 0
            self.frame_atual += 1
            
            # Lógica de transição de estados
            if self.estado == self.ESTADO_START:
                if self.frame_atual >= len(self.assets.fogo_start):
                    self.estado = self.ESTADO_LOOP
                    self.frame_atual = 0
                    
            elif self.estado == self.ESTADO_LOOP:
                if self.frame_atual >= len(self.assets.fogo_loop):
                    # Assim que terminar o loop, vai para o end
                    self.estado = self.ESTADO_END
                    self.frame_atual = 0
                
                # self.tempo_loop += 1
                # if self.tempo_loop >= self.duracao_loop:
                #     self.estado = self.ESTADO_END
                #     self.frame_atual = 0
                    
            elif self.estado == self.ESTADO_END:
                if self.frame_atual >= len(self.assets.fogo_end):
                    self.ativo = False
                    
    def desenhar(self, superficie, camera_x, camera_y):
        """Desenha o fogo na tela"""
        if not self.ativo:
            return
            
        tela_x = int(self.x - camera_x)
        tela_y = int(self.y - camera_y)
        
        sprites = []
        if self.estado == self.ESTADO_START:
            sprites = self.assets.fogo_start
        elif self.estado == self.ESTADO_LOOP:
            sprites = self.assets.fogo_loop
        elif self.estado == self.ESTADO_END:
            sprites = self.assets.fogo_end
            
        if self.frame_atual < len(sprites):
            superficie.blit(sprites[self.frame_atual], (tela_x, tela_y))

class GerenciadorFogo:
    """Gerencia todos os fogos do nível"""
    
    def __init__(self, assets):
        self.assets = assets
        self.fogos = []
        
    def adicionar_fogo(self, rect_colisao):
        """Cria fogo em cima do bloco colidido"""
        # rect_colisao é o retângulo do bloco que o meteoro atingiu
        x_bloco = rect_colisao.x
        y_bloco = rect_colisao.y
        
        # Centralizar o fogo (24px) no tile (16px)
        # offset = (16 - 24) // 2 = -4
        x_final = x_bloco - 4
        
        # O fogo deve ficar em cima do bloco
        # O sprite do fogo tem 32px de altura
        # Queremos que a base do fogo (y + 32) coincida com o topo do bloco (y_bloco)
        # y_final = y_bloco - 32
        # Anteriormente estava -28, o que fazia sobrepor 4px.
        # Ajustando para -32 para ficar exatamente em cima.
        y_final = y_bloco - 32
        
        fogo = Fogo(x_final, y_final, self.assets)
        self.fogos.append(fogo)
            
    def atualizar(self, jogador_rect):
        """Atualiza fogos e verifica colisões"""
        colidiu = False
        
        for fogo in self.fogos:
            fogo.atualizar()
            
            # Verificar colisão com jogador se estiver no loop (fogo alto)
            if fogo.ativo and fogo.estado == Fogo.ESTADO_LOOP:
                if fogo.get_hitbox().colliderect(jogador_rect):
                    colidiu = True
                    
        # Remover fogos inativos
        self.fogos = [f for f in self.fogos if f.ativo]
        
        return colidiu
                    
    def desenhar(self, superficie, camera_x, camera_y):
        """Desenha todos os fogos"""
        for fogo in self.fogos:
            fogo.desenhar(superficie, camera_x, camera_y)
