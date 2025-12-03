"""
Sistema de ovos (moedas) colecionáveis
"""
import pygame
import math
from config import TILE_SIZE, SPRITE_LARGURA, SPRITE_ALTURA

class Ovo:
    """Representa um ovo colecionável"""
    
    def __init__(self, x, y, sprites):
        self.x = x
        self.y = y
        self.x = x
        self.y = y
        
        # Redimensionar sprites para ficarem menores (16x16)
        self.tamanho_ovo = 16
        self.sprites = []
        for sprite in sprites:
            self.sprites.append(pygame.transform.scale(sprite, (self.tamanho_ovo, self.tamanho_ovo)))
            
        self.frame_atual = 0
        self.contador_animacao = 0
        self.velocidade_animacao = 10
        self.coletado = False
        
        # Hitbox um pouco menor que o tile
        self.largura = 16
        self.altura = 16
        self.offset_x = (TILE_SIZE - self.largura) // 2
        # Hitbox um pouco menor que o tile
        self.largura = 12
        self.altura = 12
        self.offset_x = (TILE_SIZE - self.largura) // 2
        self.offset_y = (TILE_SIZE - self.altura) // 2
        
        # Variáveis para flutuar
        self.flutuar_y = 0
        self.flutuar_angulo = 0
        self.flutuar_velocidade = 0.1
        self.flutuar_amplitude = 3
        
    def get_hitbox(self):
        """Retorna o retângulo de colisão"""
        return pygame.Rect(
            self.x + self.offset_x,
            self.y + self.offset_y,
            self.largura,
            self.altura
        )
        
    def atualizar(self):
        """Atualiza a animação do ovo"""
        if self.coletado:
            return
            
        self.contador_animacao += 1
        self.contador_animacao += 1
        if self.contador_animacao >= self.velocidade_animacao:
            self.frame_atual = (self.frame_atual + 1) % len(self.sprites)
            self.contador_animacao = 0
            
        # Atualizar flutuação
        self.flutuar_angulo += self.flutuar_velocidade
        self.flutuar_y = math.sin(self.flutuar_angulo) * self.flutuar_amplitude
            
    def desenhar(self, superficie, camera_x, camera_y):
        """Desenha o ovo na tela"""
        if self.coletado:
            return
            
        tela_x = int(self.x - camera_x)
        tela_y = int(self.y - camera_y)
        
        # Centralizar o sprite no tile
        offset_sprite_x = (TILE_SIZE - self.tamanho_ovo) // 2
        offset_sprite_y = (TILE_SIZE - self.tamanho_ovo) // 2
        
        superficie.blit(
            self.sprites[self.frame_atual],
            (tela_x + offset_sprite_x, tela_y + offset_sprite_y + self.flutuar_y)
        )

class GerenciadorOvos:
    """Gerencia todos os ovos do nível"""
    
    def __init__(self, assets):
        self.assets = assets
        self.ovos = []
        self.ovos_coletados = 0
        
    def adicionar_ovos(self, posicoes):
        """Cria ovos nas posições especificadas"""
        for x, y in posicoes:
            ovo = Ovo(x, y, self.assets.ovo_sprites)
            self.ovos.append(ovo)
            
    def atualizar(self, jogador_rect):
        """Atualiza ovos e verifica colisões"""
        for ovo in self.ovos:
            if not ovo.coletado:
                ovo.atualizar()
                
                # Verificar colisão com jogador
                if ovo.get_hitbox().colliderect(jogador_rect):
                    ovo.coletado = True
                    self.ovos_coletados += 1
                    # Aqui poderia tocar um som
                    
    def desenhar(self, superficie, camera_x, camera_y):
        """Desenha todos os ovos não coletados"""
        for ovo in self.ovos:
            ovo.desenhar(superficie, camera_x, camera_y)
