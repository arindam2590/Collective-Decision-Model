import pygame

class Agent:
    def __init__(self, x, y, rad=10):
        self.x = x
        self.y = y
        self.radius = rad
        self.color = (255, 0, 0)        
        
    def draw_agents(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
