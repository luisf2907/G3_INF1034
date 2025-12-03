"""
Sistema de meteoros que caem do céu (Com rotação correta)
"""
import pygame
import random
import math  # --- NOVO: Necessário para calcular o ângulo ---
from config import LARGURA_VIRTUAL

class Meteoro:
    """Classe que representa um meteoro individual"""
    
    def __init__(self, x, y, sprites):
        self.x = x
        self.y = y
        
        # Velocidades
        self.vel_y = random.uniform(1.5, 3.5)
        self.vel_x = random.uniform(-1.5, 1.5)
        
        self.ativo = True
        
        # Animação
        self.frame_atual = 0
        self.contador_animacao = 0
        self.velocidade_animacao = 8
        
        # Hitbox lógica (mantemos fixa para a colisão funcionar bem)
        self.largura = 10
        self.altura = 19
        
        # Calculamos o ângulo baseado na velocidade horizontal e vertical
        # Math.atan2 retorna o ângulo em radianos, convertemos para graus.
        angulo = math.degrees(math.atan2(self.vel_x, self.vel_y))
        
        self.sprites_rotacionados = []
        for sprite in sprites:
            # pygame.transform.rotate gira no sentido anti-horário
            # Como nossa imagem aponta para baixo, o ângulo calculado já funciona bem
            sprite_rot = pygame.transform.rotate(sprite, angulo)
            self.sprites_rotacionados.append(sprite_rot)
            
    def get_hitbox(self):
        """Retorna o retângulo de colisão (lógica)"""
        return pygame.Rect(self.x, self.y, self.largura, self.altura)
    
    def atualizar(self, mapa):
        if not self.ativo:
            return False
        
        # Movimento
        self.x += self.vel_x
        self.y += self.vel_y
        
        # Verificar colisão com o chão
        hitbox = self.get_hitbox()
        colisoes = mapa.get_retangulos_colisao(hitbox)
        
        if colisoes:
            self.ativo = False
            # Retorna o primeiro retângulo colidido para saber onde criar o fogo
            return colisoes[0]
            
        # Limites do mapa
        if self.y > mapa.altura_px:
            self.ativo = False
            return None
        
        # Atualizar animação
        self.contador_animacao += 1
        if self.contador_animacao >= self.velocidade_animacao:
            self.frame_atual = (self.frame_atual + 1) % 3
            self.contador_animacao = 0
            
        return None
    
    def desenhar(self, superficie, camera_x, camera_y):
        if not self.ativo:
            return
        
        tela_x = int(self.x - camera_x)
        tela_y = int(self.y - camera_y)
        
        if -50 <= tela_x <= LARGURA_VIRTUAL + 50:
            # Pegamos a imagem já rotacionada
            imagem = self.sprites_rotacionados[self.frame_atual]
            
            # Quando giramos uma imagem, o tamanho do retângulo dela muda.
            # Para que ela não fique deslocada em relação à hitbox, pegamos o centro.
            rect_imagem = imagem.get_rect()
            rect_imagem.centerx = tela_x + self.largura // 2
            rect_imagem.centery = tela_y + self.altura // 2
            
            superficie.blit(imagem, rect_imagem)


class GerenciadorMeteoros:
    """Classe que gerencia todos os meteoros do jogo"""
    
    def __init__(self, assets, largura_mapa):
        self.assets = assets
        self.largura_mapa = largura_mapa
        self.meteoros = []
        
        self.contador_spawn = 0
        self.spawn_aleatorio_min = 15 
        self.spawn_aleatorio_max = 50
        self.proximo_spawn = random.randint(self.spawn_aleatorio_min, self.spawn_aleatorio_max)
    
    def spawn_meteoro(self, camera_x):
        # Área de spawn estendida para permitir diagonais
        min_x = int(camera_x - 100)
        max_x = int(camera_x + LARGURA_VIRTUAL + 100)
        
        min_x = max(0, min_x)
        max_x = min(self.largura_mapa - 10, max_x)
        
        if max_x > min_x:
            x = random.randint(min_x, max_x)
            y = -40
            meteoro = Meteoro(x, y, self.assets.meteoro_sprites)
            self.meteoros.append(meteoro)
    
    def atualizar(self, mapa, camera_x):
        impactos = []
        for meteoro in self.meteoros:
            colisao = meteoro.atualizar(mapa)
            if colisao:
                # colisao agora é o rect do bloco atingido
                impactos.append(colisao)
        
        self.meteoros = [m for m in self.meteoros if m.ativo]
        
        self.contador_spawn += 1
        if self.contador_spawn >= self.proximo_spawn:
            self.spawn_meteoro(camera_x)
            self.contador_spawn = 0
            self.proximo_spawn = random.randint(self.spawn_aleatorio_min, self.spawn_aleatorio_max)
            
        return impactos
    
    def desenhar(self, superficie, camera_x, camera_y):
        for meteoro in self.meteoros:
            meteoro.desenhar(superficie, camera_x, camera_y)
    
    def verificar_colisao_jogador(self, jogador_rect):
        for meteoro in self.meteoros:
            if meteoro.ativo and meteoro.get_hitbox().colliderect(jogador_rect):
                return True
        return False