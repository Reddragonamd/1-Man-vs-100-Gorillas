import pygame
import random
import math
from settings import *

class Spritesheet:
    def __init__(self, file):
        self.sheet = pygame.image.load(file).convert()

    def get_sprite(self, x, y, width, height):
        sprite = pygame.Surface([width, height])
        sprite.blit(self.sheet, (0, 0), (x, y, width, height))
        sprite.set_colorkey(BLACK)
        return sprite

class Block(pygame.sprite.Sprite):
    def __init__(self, game, x, y, width=None, height=None):
        self.game = game
        self._layer = BLOCK_LAYER
        self.groups = self.game.all_sprites, self.game.blocks
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x
        self.y = y
        self.width = width if width else TILESIZE
        self.height = height if height else TILESIZE

        self.image = pygame.Surface((self.width, self.height))
        self.image.set_alpha(0)  
        
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

class Button:
    def __init__(self, x, y, width, height, fg, bg, content, fontsize):
        self.font = pygame.font.Font('../text/TTOctosquaresXBoldIt.ttf', fontsize)
        self.content = content

        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.fg = fg
        self.bg = bg

        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(self.bg)
        self.rect = self.image.get_rect()

        self.rect.x = self.x
        self.rect.y = self.y 

        self.text = self.font.render(self.content, True, self.fg)
        self.text_rect = self.text.get_rect(center=(self.width/2, self.height/2))
        self.image.blit(self.text, self.text_rect)

    def is_pressed(self, pos, pressed):
        if self.rect.collidepoint(pos):
            if pressed[0]:
                return True
            return False
        return False

class Decoration(pygame.sprite.Sprite):
    def __init__(self, game, x, y, image):
        self.game = game
        self._layer = BLOCK_LAYER 
        self.groups = self.game.all_sprites,
        pygame.sprite.Sprite.__init__(self, self.groups)
        
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y - self.rect.height

class Barrier(pygame.sprite.Sprite):
    def __init__(self, game, x, y, width, height):
        self.game = game
        self._layer = BLOCK_LAYER
        self.groups = self.game.all_sprites, self.game.blocks
        pygame.sprite.Sprite.__init__(self, self.groups)
        
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        self.image = pygame.Surface((self.width, self.height))
        self.image.set_alpha(0) 

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        
        self.active = True
    
    def remove_barrier(self):
        self.kill()