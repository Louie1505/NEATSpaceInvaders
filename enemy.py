import pygame

class Enemy:
    img: pygame.image
    coords: tuple
    def __init__(self, i, c):
        self.img = i
        self.coords = c