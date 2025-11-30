"""
Gerenciamento do mapa e colisões
"""
import pygame
# Removemos COR_CEU da importação
from config import TILE_SIZE


class Mapa:
    """Classe para carregar e renderizar o mapa"""
    
    def __init__(self, arquivo, assets):
        self.assets = assets
        self.dados = self._carregar_mapa(arquivo)
        self.largura_px = len(self.dados[0]) * TILE_SIZE
        self.altura_px = len(self.dados) * TILE_SIZE
        self.superficie = self._pre_renderizar()
    
    def _carregar_mapa(self, arquivo):
        """Carrega o mapa de um arquivo de texto"""
        try:
            with open(arquivo, 'r') as f:
                linhas = f.readlines()
            mapa = [linha.rstrip('\n') for linha in linhas]
            return mapa
        except FileNotFoundError:
            # Mapa padrão caso o arquivo não exista
            return [
                "                        ",
                "                        ",
                "      EGGGGGGGGGD       ",
                "                        ",
                " EGD              EGD   ",
                "                        ",
                "EGGGGGGGGGGGGGGGGGGGGGGD",
                "LLLLLLRRRRRRLLLLL<><>><>"
            ]
    
    def _pre_renderizar(self):
        """Renderiza o mapa completo antecipadamente para otimização"""
        superficie = pygame.Surface((self.largura_px, self.altura_px))
        
        # --- NOVO: Desenhar o background repetido (Tiling) ---
        # Em vez de preencher com cor sólida, desenhamos a imagem.
        bg = self.assets.background
        bg_w = bg.get_width()
        bg_h = bg.get_height()
        
        # Calcula quantas vezes a imagem cabe horizontalmente e verticalmente
        cols = (self.largura_px // bg_w) + 1
        rows = (self.altura_px // bg_h) + 1
        
        for r in range(rows):
            for c in range(cols):
                superficie.blit(bg, (c * bg_w, r * bg_h))
        # -----------------------------------------------------
        
        for linha_idx, linha in enumerate(self.dados):
            for coluna_idx, tile in enumerate(linha):
                x = coluna_idx * TILE_SIZE
                y = linha_idx * TILE_SIZE
                
                if tile == 'G':
                    superficie.blit(self.assets.tile_grama, (x, y))
                elif tile == 'T':
                    superficie.blit(self.assets.tile_terra, (x, y))
                elif tile == 'E':
                    superficie.blit(self.assets.tile_ponta_esq, (x, y))
                elif tile == 'D':
                    superficie.blit(self.assets.tile_ponta_dir, (x, y))
                elif tile == 'L':  # Terra Esquerda-Direita
                    superficie.blit(self.assets.tile_terra_esq_dir, (x, y))
                elif tile == 'R':  # Terra Direita-Esquerda
                    superficie.blit(self.assets.tile_terra_dir_esq, (x, y))
                elif tile == '<':  # Terra Lateral Esquerda
                    superficie.blit(self.assets.tile_terra_lateral_esq, (x, y))
                elif tile == '>':  # Terra Lateral Direita
                    superficie.blit(self.assets.tile_terra_lateral_dir, (x, y))
        
        return superficie.convert()
    
    def get_retangulos_colisao(self, rect):
        """Retorna lista de retângulos de colisão próximos ao rect dado"""
        retangulos = []
        
        # Calcular apenas os tiles próximos (otimização)
        start_col = max(0, int(rect.left // TILE_SIZE))
        end_col = min(len(self.dados[0]), int(rect.right // TILE_SIZE) + 1)
        start_row = max(0, int(rect.top // TILE_SIZE))
        end_row = min(len(self.dados), int(rect.bottom // TILE_SIZE) + 1)
        
        for row in range(start_row, end_row):
            for col in range(start_col, end_col):
                if row < len(self.dados) and col < len(self.dados[row]):
                    tile = self.dados[row][col]
                    # Tiles sólidos
                    if tile in ['G', 'T', 'E', 'D', 'L', 'R', '<', '>']:
                        tile_rect = pygame.Rect(
                            col * TILE_SIZE,
                            row * TILE_SIZE,
                            TILE_SIZE,
                            TILE_SIZE
                        )
                        retangulos.append(tile_rect)
        
        return retangulos