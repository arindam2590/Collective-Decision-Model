import pygame
import math


class Hurdle:
    def __init__(self, x, y, amp=1, freq=0.02):
        self.x = float(x)
        self.y = float(y)
        self.amplitude = amp
        self.frequency = freq
        self.color = (0, 0, 0)
        self.hurdle_width = 20
        self.hurdle_height = 30

    def update_hurdle_position(self, frame_count):
        # Vertical oscillation
        self.y = self.y + self.amplitude * math.sin(frame_count * self.frequency)

    def draw_hurdles(self, screen):
        pygame.draw.rect(screen, self.color, (int(self.x), int(self.y), int(self.hurdle_width), int(self.hurdle_height)))
