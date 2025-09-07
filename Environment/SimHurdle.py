import pygame
import math

class Hurdle:
    def __init__(self, x, y, amp=1, freq = 0.02):
        self.x = x
        self.y = y
        self.amplitude = amp
        self.frequency = freq
        self.color = (0, 0, 0)
        self.hurdle_width = 20
        self.hurdle_height = 30      
        
    def update_hurdle_position(self, frame_count):
        hurdle_y = self.y
        # Move Vertically
        hurdle_y += self.amplitude * math.sin(frame_count * self.frequency) 
        self.y = hurdle_y
        
    def draw_hurdles(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.hurdle_width, self.hurdle_height))
