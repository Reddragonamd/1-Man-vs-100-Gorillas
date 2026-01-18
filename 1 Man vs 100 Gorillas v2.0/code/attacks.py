import pygame
import math
from settings import *

class Attack(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = PLAYER_LAYER
        self.groups = self.game.all_sprites, self.game.attacks
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x
        self.y = y
        self.width = TILESIZE
        self.height = TILESIZE

        self.animation_loop = 0

        self.image = self.game.attack_spritesheet.get_sprite(0, 0, self.width, self.height)

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        self.right_animations = [
            self.game.attack_spritesheet.get_sprite(0, 128, self.width, self.height),
            self.game.attack_spritesheet.get_sprite(64, 128, self.width, self.height),
            self.game.attack_spritesheet.get_sprite(128, 128, self.width, self.height),
            self.game.attack_spritesheet.get_sprite(192, 128, self.width, self.height),
            self.game.attack_spritesheet.get_sprite(256, 128, self.width, self.height)
        ]

        self.down_animations = [
            self.game.attack_spritesheet.get_sprite(0, 64, self.width, self.height),
            self.game.attack_spritesheet.get_sprite(64, 64, self.width, self.height),
            self.game.attack_spritesheet.get_sprite(128, 64, self.width, self.height),
            self.game.attack_spritesheet.get_sprite(192, 64, self.width, self.height),
            self.game.attack_spritesheet.get_sprite(256, 64, self.width, self.height)
        ]

        self.left_animations = [
            self.game.attack_spritesheet.get_sprite(0, 192, self.width, self.height),
            self.game.attack_spritesheet.get_sprite(64, 192, self.width, self.height),
            self.game.attack_spritesheet.get_sprite(128, 192, self.width, self.height),
            self.game.attack_spritesheet.get_sprite(192, 192, self.width, self.height),
            self.game.attack_spritesheet.get_sprite(256, 192, self.width, self.height)
        ]

        self.up_animations = [
            self.game.attack_spritesheet.get_sprite(0, 0, self.width, self.height),
            self.game.attack_spritesheet.get_sprite(64, 0, self.width, self.height),
            self.game.attack_spritesheet.get_sprite(128, 0, self.width, self.height),
            self.game.attack_spritesheet.get_sprite(192, 0, self.width, self.height),
            self.game.attack_spritesheet.get_sprite(256, 0, self.width, self.height)
        ]

    def update(self):
        self.animate()
        self.collide()

    def collide(self):
        hits = pygame.sprite.spritecollide(self, self.game.enemies, False)
        if hits:
            self.kill()
            for enemy in hits:
                enemy.take_damage(10)

    def animate(self):
        direction = self.game.player.facing

        if direction == "up":
            self.image = self.up_animations[math.floor(self.animation_loop)]
            self.animation_loop += 0.5
            if self.animation_loop >= 5:
                self.kill()

        if direction == "down":
            self.image = self.down_animations[math.floor(self.animation_loop)]
            self.animation_loop += 0.5
            if self.animation_loop >= 5:
                self.kill()

        if direction == "left":
            self.image = self.left_animations[math.floor(self.animation_loop)]
            self.animation_loop += 0.5
            if self.animation_loop >= 5:
                self.kill()

        if direction == "right":
            self.image = self.right_animations[math.floor(self.animation_loop)]
            self.animation_loop += 0.5
            if self.animation_loop >= 5:
                self.kill()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, game, x, y, direction):
        self.game = game
        self._layer = PLAYER_LAYER
        self.groups = self.game.all_sprites, self.game.attacks
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x
        self.y = y
        self.width = TILESIZE
        self.height = TILESIZE

        self.speed = 5
        self.animation_loop = 0
        self.direction = direction

        self.right_animations = [self.game.bullet_spritesheet.get_sprite(214, 29, self.width, self.height)]
        self.down_animations = [self.game.bullet_spritesheet.get_sprite(41, 11, self.width, self.height)]
        self.left_animations = [self.game.bullet_spritesheet.get_sprite(304, 28, self.width, self.height)]
        self.up_animations = [self.game.bullet_spritesheet.get_sprite(132, 5, self.width, self.height)]

        self.image = self.down_animations[0]
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 2000

    def update(self):
        self.movement()
        self.animate()
        self.collide()
        
        if pygame.time.get_ticks() - self.spawn_time > self.lifetime:
            self.kill()

    def collide(self):
        enemy_hits = pygame.sprite.spritecollide(self, self.game.enemies, False)
        if enemy_hits:
            self.kill()
            for enemy in enemy_hits:
                enemy.take_damage(5)

        if pygame.sprite.spritecollide(self, self.game.blocks, False):
            self.kill()

    def animate(self):
        if self.direction == "up":
            current_animations = self.up_animations
        elif self.direction == "down":
            current_animations = self.down_animations
        elif self.direction == "left":
            current_animations = self.left_animations
        else: 
            current_animations = self.right_animations

        self.image = current_animations[math.floor(self.animation_loop)]

        self.animation_loop += 0.2
        if self.animation_loop >= len(current_animations):
            self.animation_loop = 0

    def movement(self):
        if self.direction == "up":
            self.y -= self.speed
        elif self.direction == "down":
            self.y += self.speed
        elif self.direction == "left":
            self.x -= self.speed
        elif self.direction == "right":
            self.x += self.speed
        
        self.rect.x = self.x
        self.rect.y = self.y