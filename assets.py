"""
Gerenciamento de carregamento de assets (imagens, sprites)
"""
import pygame
import sys
# Adicionamos LARGURA_VIRTUAL e ALTURA_VIRTUAL nas importações
from config import SPRITE_LARGURA, SPRITE_ALTURA, FRAMES_IDLE, FRAMES_MOVE, FRAMES_JUMP, FRAMES_HURT, FRAMES_DEAD, LARGURA_VIRTUAL, ALTURA_VIRTUAL, FRAMES_MOEDA


class Assets:
    """Classe para carregar e gerenciar todos os recursos do jogo"""
    
    def __init__(self):
        self.tile_grama = None
        self.tile_terra = None
        self.tile_ponta_esq = None
        self.tile_ponta_dir = None
        self.tile_terra_esq_dir = None
        self.tile_terra_dir_esq = None
        self.tile_terra_lateral_esq = None
        self.tile_terra_lateral_dir = None
        self.dino_idle = []
        self.dino_move = []
        self.dino_jump = []
        self.dino_hurt = []
        self.dino_dead = []
        self.meteoro_sprites = []
        self.moeda_sprites = []
        self.icone_vida = None
        # Novo atributo para o background
        self.background = None
        
        self.carregar_recursos()
    
    def _criar_background_apocaliptico(self):
        """Cria um background com gradiente de pôr do sol apocalíptico"""
        bg = pygame.Surface((LARGURA_VIRTUAL, ALTURA_VIRTUAL))
        
        # Cores do pôr do sol apocalíptico (de cima para baixo)
        cores = [
            (25, 10, 35),      # Roxo escuro no topo
            (75, 20, 45),      # Roxo avermelhado
            (140, 35, 35),     # Vermelho escuro
            (180, 60, 30),     # Vermelho alaranjado
            (220, 100, 30),    # Laranja
            (255, 140, 40),    # Laranja claro
            (255, 180, 80),    # Amarelo alaranjado
            (200, 120, 60),    # Laranja mais escuro (horizonte)
        ]
        
        # Calcular altura de cada faixa
        num_faixas = len(cores) - 1
        altura_faixa = ALTURA_VIRTUAL / num_faixas
        
        for i in range(num_faixas):
            cor_inicio = cores[i]
            cor_fim = cores[i + 1]
            y_inicio = int(i * altura_faixa)
            y_fim = int((i + 1) * altura_faixa)
            
            for y in range(y_inicio, y_fim):
                # Interpolação linear entre as cores
                t = (y - y_inicio) / altura_faixa
                r = int(cor_inicio[0] + (cor_fim[0] - cor_inicio[0]) * t)
                g = int(cor_inicio[1] + (cor_fim[1] - cor_inicio[1]) * t)
                b = int(cor_inicio[2] + (cor_fim[2] - cor_inicio[2]) * t)
                pygame.draw.line(bg, (r, g, b), (0, y), (LARGURA_VIRTUAL, y))
        
        return bg
    
    def carregar_recursos(self):
        """Carrega todas as imagens do jogo"""
        try:
            try:
                bg_raw = pygame.image.load('background.png').convert()
                self.background = pygame.transform.scale(bg_raw, (LARGURA_VIRTUAL, ALTURA_VIRTUAL))
            except FileNotFoundError:
                # Se não achar o background, cria um gradiente de pôr do sol apocalíptico
                self.background = self._criar_background_apocaliptico()

            # Tiles do mapa
            self.tile_grama = pygame.image.load('assets/grass.png').convert_alpha()
            self.tile_terra = pygame.image.load('assets/terra.png').convert_alpha()
            self.tile_ponta_esq = pygame.image.load('assets/grass_ponta_esquerda.png').convert_alpha()
            self.tile_ponta_dir = pygame.image.load('assets/grass_ponta_direita.png').convert_alpha()
            self.tile_terra_esq_dir = pygame.image.load('assets/terra_esquerda_direita.png').convert_alpha()
            self.tile_terra_dir_esq = pygame.image.load('assets/terra_direita_esquerda.png').convert_alpha()
            self.tile_terra_lateral_esq = pygame.image.load('assets/terra_lateral_esquerda.png').convert_alpha()
            self.tile_terra_lateral_dir = pygame.image.load('assets/terra_lateral_direita.png').convert_alpha()
            
            # Sprite sheets do dino
            sprite_sheet_idle = pygame.image.load('assets/idle.png').convert_alpha()
            sprite_sheet_move = pygame.image.load('assets/move.png').convert_alpha()
            sprite_sheet_jump = pygame.image.load('assets/jump.png').convert_alpha()
            sprite_sheet_hurt = pygame.image.load('assets/hurt.png').convert_alpha()
            sprite_sheet_dead = pygame.image.load('assets/dead.png').convert_alpha()
            
            # Separar frames das animações
            self.dino_idle = self._extrair_frames(sprite_sheet_idle, FRAMES_IDLE)
            self.dino_move = self._extrair_frames(sprite_sheet_move, FRAMES_MOVE)
            self.dino_jump = self._extrair_frames(sprite_sheet_jump, FRAMES_JUMP)
            self.dino_hurt = self._extrair_frames(sprite_sheet_hurt, FRAMES_HURT)
            self.dino_dead = self._extrair_frames(sprite_sheet_dead, FRAMES_DEAD)
            
            # Sprite sheet do meteoro (3 frames, 10x19 cada)
            sprite_sheet_meteoro = pygame.image.load('assets/meteoro.png').convert_alpha()
            for i in range(3):
                frame = sprite_sheet_meteoro.subsurface((i * 10, 0, 10, 19))
                self.meteoro_sprites.append(frame)
            
            # Sprite sheet das moedas
            try:
                sprite_sheet_moeda = pygame.image.load('assets/moeda.png').convert_alpha()
                # Extrair frames de moeda (tamanho diferente do sprite padrão)
                self.moeda_sprites = self._extrair_frames_moeda(sprite_sheet_moeda, FRAMES_MOEDA)
            except FileNotFoundError:
                # Se não tiver moeda.png, cria sprites simples
                self.moeda_sprites = self._criar_moedas_procedurais()
            
            # Ícone de vida
            self.icone_vida = pygame.image.load('assets/vida.png').convert_alpha()
            
        except FileNotFoundError as e:
            pygame.quit()
            sys.exit()
    
    def _extrair_frames(self, sprite_sheet, num_frames):
        """Extrai frames individuais de um sprite sheet"""
        frames = []
        for i in range(num_frames):
            frame = sprite_sheet.subsurface(
                (i * SPRITE_LARGURA, 0, SPRITE_LARGURA, SPRITE_ALTURA)
            )
            frames.append(frame)
        return frames
    
    def _extrair_frames_moeda(self, sprite_sheet, num_frames):
        """Extrai frames de moeda (tamanho fixo de 16x16)"""
        frames = []
        for i in range(num_frames):
            frame = sprite_sheet.subsurface(
                (i * 16, 0, 16, 16)
            )
            frames.append(frame)
        return frames
    
