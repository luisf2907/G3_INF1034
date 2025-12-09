"""
Sistema de moedas coletáveis
"""
import pygame
import math
from config import (
    VELOCIDADE_ANIMACAO_MOEDA, FRAMES_MOEDA,
    MOEDA_LARGURA, MOEDA_ALTURA, MOEDA_VELOCIDADE_FLUTUACAO,
    MOEDA_AMPLITUDE_FLUTUACAO
)


class Moeda:
    """Classe que representa uma moeda coletável"""
    
    def __init__(self, x, y, sprites_moeda):
        self.x = x
        self.y = y
        self.y_original = y  # Usado para animação de flutuação
        self.sprites = sprites_moeda
        
        # Animação
        self.frame_atual = 0
        self.contador_animacao = 0
        self.velocidade_animacao = VELOCIDADE_ANIMACAO_MOEDA
        
        # Flutuação vertical (efeito bobbing)
        self.tempo_flutuacao = 0
        
        # Estado
        self.ativo = True
        self.coletado = False
    
    def get_hitbox(self):
        """Retorna o retângulo de colisão da moeda"""
        return pygame.Rect(
            self.x - MOEDA_LARGURA // 2,
            self.y - MOEDA_ALTURA // 2,
            MOEDA_LARGURA,
            MOEDA_ALTURA
        )
    
    def atualizar(self):
        """Atualiza a animação e flutuação da moeda"""
        if not self.ativo:
            return
        
        # Animação de frame
        self.contador_animacao += 1
        if self.contador_animacao >= self.velocidade_animacao:
            self.contador_animacao = 0
            self.frame_atual = (self.frame_atual + 1) % len(self.sprites)
        
        # Efeito de flutuação vertical (sine wave)
        self.tempo_flutuacao += MOEDA_VELOCIDADE_FLUTUACAO
        self.y = self.y_original + math.sin(self.tempo_flutuacao) * MOEDA_AMPLITUDE_FLUTUACAO
    
    def desenhar(self, superficie, camera_x=0, camera_y=0):
        """Desenha a moeda na tela"""
        if not self.ativo:
            return
        
        sprite = self.sprites[self.frame_atual]
        
        # Calcular posição na tela (subtraindo offset da câmera)
        tela_x = int(self.x - MOEDA_LARGURA // 2 - camera_x)
        tela_y = int(self.y - MOEDA_ALTURA // 2 - camera_y)
        
        # Desenhar sprite
        superficie.blit(sprite, (tela_x, tela_y))
    
    def coletar(self):
        """Marca a moeda como coletada"""
        self.coletado = True
        self.ativo = False


class GerenciadorMoedas:
    """Gerenciador de moedas no mapa"""
    
    def __init__(self, assets, largura_mapa_px):
        self.assets = assets
        self.largura_mapa_px = largura_mapa_px
        self.moedas = []
        self.pontos_totais = 0
    
    def adicionar_moeda(self, x, y):
        """Adiciona uma moeda ao mapa"""
        moeda = Moeda(x, y, self.assets.moeda_sprites)
        self.moedas.append(moeda)
    
    def atualizar(self, camera_x):
        """Atualiza todas as moedas"""
        for moeda in self.moedas:
            moeda.atualizar()
    
    def verificar_colisao_jogador(self, jogador_hitbox):
        """Verifica colisão com o jogador e retorna pontos coletados"""
        pontos = 0
        for moeda in self.moedas:
            if moeda.ativo and jogador_hitbox.colliderect(moeda.get_hitbox()):
                moeda.coletar()
                pontos += 10  # Valor padrão por moeda
                self.pontos_totais += pontos
        
        return pontos
    
    def desenhar(self, superficie, camera_x, camera_y):
        """Desenha todas as moedas ativas"""
        for moeda in self.moedas:
            if moeda.ativo:
                moeda.desenhar(superficie, camera_x, camera_y)
    
    def reiniciar(self):
        """Reinicia o gerenciador de moedas"""
        self.moedas = []
        self.pontos_totais = 0
    
    def debug_info(self):
        """Exibe informações de debug do gerenciador de moedas"""
        pass
