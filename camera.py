"""
Sistema de câmera
"""
from config import LARGURA_VIRTUAL, ALTURA_VIRTUAL


class Camera:
    """Classe que gerencia a câmera do jogo"""
    
    def __init__(self, largura_mapa, altura_mapa):
        self.x = 0
        self.y = 0
        self.largura_mapa = largura_mapa
        self.altura_mapa = altura_mapa
    
    def atualizar(self, jogador_x, jogador_y):
        """Atualiza a posição da câmera para seguir o jogador"""
        # Centralizar câmera no jogador (um pouco à frente na direção do movimento)
        self.x = int(jogador_x - LARGURA_VIRTUAL // 3)
        self.y = int(jogador_y - ALTURA_VIRTUAL // 2)
        
        # Limitar câmera aos limites do mapa
        self.x = max(0, min(self.x, self.largura_mapa - LARGURA_VIRTUAL))
        self.y = max(0, min(self.y, self.altura_mapa - ALTURA_VIRTUAL))