import pygame
from settings import *

class AmmoCrate(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = ITEM_LAYER
        self.groups = self.game.all_sprites, self.game.items
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.image = self.game.ammo_spritesheet.get_sprite(0, 0, TILESIZE, TILESIZE)
        self.image.set_colorkey(BLACK)

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.ammo_amount = 1


class MedKit(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = ITEM_LAYER
        self.groups = self.game.all_sprites, self.game.items
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.image = self.game.medkit_spritesheet.get_sprite(0, 0, TILESIZE, TILESIZE)
        self.image.set_colorkey(BLACK)

        self.image = pygame.transform.scale(self.image, (int(TILESIZE * 1.5), int(TILESIZE * 1.5)))

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.heal_amount = 15


class MiniShield(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = ITEM_LAYER
        self.groups = self.game.all_sprites, self.game.items
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.image = self.game.minishield_spritesheet.get_sprite(0, 0, TILESIZE, TILESIZE)
        self.image.set_colorkey(BLACK)

        self.image = pygame.transform.scale(self.image, (int(TILESIZE * 1.75), int(TILESIZE * 1.75)))

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.shield_amount = 25