"""
Classe do jogador (Dino)
"""
import pygame
from config import (
    DINO_VELOCIDADE, DINO_GRAVIDADE, DINO_FORCA_PULO,
    HITBOX_OFFSET_X, HITBOX_OFFSET_Y, HITBOX_LARGURA, HITBOX_ALTURA,
    VELOCIDADE_ANIMACAO_IDLE, VELOCIDADE_ANIMACAO_MOVE, VELOCIDADE_ANIMACAO_JUMP,
    VELOCIDADE_ANIMACAO_HURT, VELOCIDADE_ANIMACAO_DEAD, DURACAO_HURT, 
    DURACAO_INVENCIBILIDADE, VIDAS_INICIAIS
)


class Jogador:
    """Classe que representa o jogador (dinossauro)"""
    
    def __init__(self, x, y, assets):
        self.assets = assets
        self.x = x
        self.y = y
        self.vel_y = 0
        self.velocidade = DINO_VELOCIDADE
        self.gravidade = DINO_GRAVIDADE
        self.forca_pulo = DINO_FORCA_PULO
        self.no_chao = False
        self.direcao = 1  # 1 = direita, -1 = esquerda
        
        # Animação
        self.frame_atual = 0
        self.contador_animacao = 0
        self.estado = "idle"
        self.estado_anterior = "idle"
        self.frame_pulo = 0
        
        # Sistema de dano
        self.levou_dano = False
        self.contador_hurt = 0
        self.invencivel = False
        self.contador_invencibilidade = 0
        self.animacao_hurt_completa = False
        
        # Sistema de vidas
        self.vidas = VIDAS_INICIAIS
        self.morto = False
        self.animacao_morte_completa = False
        
        # Sistema de moedas
        self.moedas_coletadas = 0
    
    def get_hitbox(self):
        """Retorna o retângulo de colisão do jogador"""
        return pygame.Rect(
            self.x + HITBOX_OFFSET_X,
            self.y + HITBOX_OFFSET_Y,
            HITBOX_LARGURA,
            HITBOX_ALTURA
        )
    
    def pular(self):
        """Faz o jogador pular se estiver no chão"""
        if self.no_chao and not self.levou_dano and not self.morto:
            self.vel_y = self.forca_pulo
            self.estado = "pulando"
            self.frame_pulo = 0
            self.no_chao = False
    
    def receber_dano(self):
        """Aplica dano ao jogador"""
        if not self.invencivel and not self.morto:
            self.vidas -= 1
            
            if self.vidas <= 0:
                self.morto = True
                self.vidas = 0
                self.estado = "morto"
                self.frame_atual = 0
                self.contador_animacao = 0
                self.animacao_morte_completa = False
                return
            
            self.levou_dano = True
            self.invencivel = True
            self.contador_hurt = 0
            self.contador_invencibilidade = 0
            self.estado = "hurt"
            self.frame_atual = 0
            self.contador_animacao = 0
            self.animacao_hurt_completa = False
    
    def atualizar(self, teclas, mapa):
        """Atualiza o estado do jogador (movimento, colisão, animação)"""
        # Se está morto, apenas atualiza animação de morte
        if self.morto:
            # Aplica gravidade
            self.vel_y += self.gravidade
            dy = self.vel_y
            
            self.y += dy
            hitbox = self.get_hitbox()
            colisoes = mapa.get_retangulos_colisao(hitbox)
            
            for tile_rect in colisoes:
                if tile_rect.colliderect(hitbox):
                    if dy > 0:
                        self.y = tile_rect.top - HITBOX_OFFSET_Y - HITBOX_ALTURA
                        self.vel_y = 0
                        self.no_chao = True
                    hitbox.y = self.y + HITBOX_OFFSET_Y
            
            self._atualizar_animacao()
            return
        
        # Atualizar sistema de dano
        if self.levou_dano:
            self.contador_hurt += 1
            if self.contador_hurt >= DURACAO_HURT:
                self.levou_dano = False
                self.contador_hurt = 0
                self.frame_atual = 0
        
        if self.invencivel:
            self.contador_invencibilidade += 1
            if self.contador_invencibilidade >= DURACAO_INVENCIBILIDADE:
                self.invencivel = False
                self.contador_invencibilidade = 0
        
        # Se está tomando dano, não pode se mover
        if self.levou_dano:
            # Só aplica gravidade
            self.vel_y += self.gravidade
            dy = self.vel_y
            
            self.y += dy
            hitbox = self.get_hitbox()
            colisoes = mapa.get_retangulos_colisao(hitbox)
            
            for tile_rect in colisoes:
                if tile_rect.colliderect(hitbox):
                    if dy > 0:
                        self.y = tile_rect.top - HITBOX_OFFSET_Y - HITBOX_ALTURA
                        self.vel_y = 0
                        self.no_chao = True
                    elif dy < 0:
                        self.y = tile_rect.bottom - HITBOX_OFFSET_Y
                        self.vel_y = 0
                    hitbox.y = self.y + HITBOX_OFFSET_Y
            
            self._atualizar_animacao()
            return
        
        # Movimento horizontal
        movendo = False
        dx = 0
        
        if teclas[pygame.K_LEFT]:
            dx = -self.velocidade
            self.direcao = -1
            movendo = True
        if teclas[pygame.K_RIGHT]:
            dx = self.velocidade
            self.direcao = 1
            movendo = True
        
        # Aplicar movimento horizontal e verificar colisão
        self.x += dx
        hitbox = self.get_hitbox()
        colisoes = mapa.get_retangulos_colisao(hitbox)
        
        for tile_rect in colisoes:
            if tile_rect.colliderect(hitbox):
                if dx > 0:
                    self.x = tile_rect.left - HITBOX_OFFSET_X - HITBOX_LARGURA
                elif dx < 0:
                    self.x = tile_rect.right - HITBOX_OFFSET_X
                hitbox.x = self.x + HITBOX_OFFSET_X
        
        # Aplicar gravidade
        self.vel_y += self.gravidade
        dy = self.vel_y
        
        # Verificar se ainda está no chão
        if self.no_chao and dy > 0:
            test_rect = pygame.Rect(
                self.x + HITBOX_OFFSET_X,
                self.y + HITBOX_OFFSET_Y + 1,
                HITBOX_LARGURA,
                HITBOX_ALTURA
            )
            if any(tile.colliderect(test_rect) for tile in mapa.get_retangulos_colisao(test_rect)):
                dy = 0
                self.vel_y = 0
            else:
                self.no_chao = False
        
        # Aplicar movimento vertical e verificar colisão
        self.y += dy
        hitbox = self.get_hitbox()
        colisoes = mapa.get_retangulos_colisao(hitbox)
        
        for tile_rect in colisoes:
            if tile_rect.colliderect(hitbox):
                if dy > 0:
                    self.y = tile_rect.top - HITBOX_OFFSET_Y - HITBOX_ALTURA
                    self.vel_y = 0
                    self.no_chao = True
                elif dy < 0:
                    self.y = tile_rect.bottom - HITBOX_OFFSET_Y
                    self.vel_y = 0
                hitbox.y = self.y + HITBOX_OFFSET_Y
        
        # Atualizar estado
        if not self.no_chao:
            self.estado = "pulando"
        elif movendo:
            self.estado = "movendo"
        else:
            self.estado = "idle"
        
        # Resetar animação ao mudar de estado
        if self.estado != self.estado_anterior:
            self.frame_atual = 0
            self.contador_animacao = 0
            if self.estado == "pulando":
                self.frame_pulo = 0
            self.estado_anterior = self.estado
        
        # Atualizar animação
        self._atualizar_animacao()
    
    def _atualizar_animacao(self):
        """Atualiza os frames da animação"""
        # Animação de morte
        if self.morto:
            if self.animacao_morte_completa:
                self.frame_atual = 4  # Último frame da morte
                return
            
            self.contador_animacao += 1
            if self.contador_animacao >= VELOCIDADE_ANIMACAO_DEAD:
                if self.frame_atual < 4:
                    self.frame_atual += 1
                else:
                    self.animacao_morte_completa = True
                self.contador_animacao = 0
            return
        
        # Se está em hurt e a animação já completou, mantém no último frame
        if self.levou_dano and self.animacao_hurt_completa:
            self.frame_atual = 3  # Último frame do hurt
            return
        
        self.contador_animacao += 1
        
        # Velocidade da animação depende do estado
        if self.levou_dano or self.estado == "hurt":
            vel = VELOCIDADE_ANIMACAO_HURT
        elif self.estado == "idle":
            vel = VELOCIDADE_ANIMACAO_IDLE
        elif self.estado == "movendo":
            vel = VELOCIDADE_ANIMACAO_MOVE
        else:
            vel = VELOCIDADE_ANIMACAO_JUMP
        
        if self.contador_animacao >= vel:
            if self.levou_dano or self.estado == "hurt":
                if self.frame_atual < 3:
                    self.frame_atual += 1
                else:
                    self.animacao_hurt_completa = True
            elif self.estado == "idle":
                self.frame_atual = (self.frame_atual + 1) % 3
            elif self.estado == "movendo":
                self.frame_atual = (self.frame_atual + 1) % 6
            elif self.estado == "pulando":
                # Frame do pulo depende da velocidade vertical
                if self.vel_y < -3:
                    self.frame_pulo = 0
                elif self.vel_y < 0:
                    self.frame_pulo = 1
                elif self.vel_y >= 0 and not self.no_chao:
                    self.frame_pulo = 2
                else:
                    self.frame_pulo = 3
            
            self.contador_animacao = 0
    
    def desenhar(self, superficie, camera_x, camera_y):
        """Desenha o jogador na tela"""
        # Posição na tela relativa à câmera
        tela_x = int(self.x - camera_x)
        tela_y = int(self.y - camera_y)
        
        # Selecionar sprite correto
        if self.morto:
            sprite = self.assets.dino_dead[min(self.frame_atual, 4)]
        elif self.levou_dano or self.estado == "hurt":
            sprite = self.assets.dino_hurt[min(self.frame_atual, 3)]
        elif self.estado == "idle":
            sprite = self.assets.dino_idle[min(self.frame_atual, 2)]
        elif self.estado == "movendo":
            sprite = self.assets.dino_move[min(self.frame_atual, 5)]
        elif self.estado == "pulando":
            sprite = self.assets.dino_jump[min(self.frame_pulo, 3)]
        else:
            sprite = self.assets.dino_idle[0]
        
        # Flipar sprite se estiver virado para esquerda
        if self.direcao == -1:
            sprite = pygame.transform.flip(sprite, True, False)
        
        # Efeito de piscar durante invencibilidade (não aplica se morto)
        if not self.morto and self.invencivel and (self.contador_invencibilidade // 5) % 2 == 0:
            return  # Não desenha (cria efeito de piscar)
        
        superficie.blit(sprite, (tela_x, tela_y))
    
    def adicionar_moeda(self):
        """Incrementa o contador de moedas coletadas"""
        self.moedas_coletadas += 1