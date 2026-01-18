from settings import *
from enemies import BossEnemy
from items import AmmoCrate, MedKit, MiniShield

class Player(pygame.sprite.Sprite):
        def __init__(self, game, x, y):
                self.game = game
                self._layer = PLAYER_LAYER
                self.groups = self.game.all_sprites
                pygame.sprite.Sprite.__init__(self, self.groups)

                self.x = x 
                self.y = y
                self.width = TILESIZE
                self.height = TILESIZE

                self.x_change = 0
                self.y_change = 0

                self.max_life = 100
                self.life = self.max_life
                
                self.shield = 0
                self.max_shield = 50

                self.facing = 'down'
                self.animation_loop = 1

                sprite = self.game.character_spritesheet.get_sprite(1, 1, self.width, self.height)
                self.image = self.scale(sprite)

                self.rect = self.image.get_rect()
                self.rect.x = self.x
                self.rect.y = self.y

                self.max_ammo = 15
                self.ammo = self.max_ammo

                self.invincible = False
                self.invincible_timer = 0
                self.invincible_duration = 500

                self.down_animations = [self.scale(self.game.character_spritesheet.get_sprite(6, 4, self.width, self.height)),
                        self.scale(self.game.character_spritesheet.get_sprite(70, 4, self.width, self.height)),
                        self.scale(self.game.character_spritesheet.get_sprite(136, 4, self.width, self.height))]

                self.up_animations = [self.scale(self.game.character_spritesheet.get_sprite(3, 68, self.width, self.height)),
                        self.scale(self.game.character_spritesheet.get_sprite(70, 68, self.width, self.height)),
                        self.scale(self.game.character_spritesheet.get_sprite(136, 68, self.width, self.height))]

                self.left_animations = [self.scale(self.game.character_spritesheet.get_sprite(3, 196, self.width, self.height)),
                        self.scale(self.game.character_spritesheet.get_sprite(70, 196, self.width, self.height)),
                        self.scale(self.game.character_spritesheet.get_sprite(136, 196, self.width, self.height))]       

                self.right_animations = [self.scale(self.game.character_spritesheet.get_sprite(3, 132, self.width, self.height)),
                        self.scale(self.game.character_spritesheet.get_sprite(70, 132, self.width, self.height)),
                        self.scale(self.game.character_spritesheet.get_sprite(136, 132, self.width, self.height))]
                
                self.idle_down = self.scale(self.game.character_spritesheet.get_sprite(6, 4, self.width, self.height))
                self.idle_up = self.scale(self.game.character_spritesheet.get_sprite(6, 68, self.width, self.height))
                self.idle_left = self.scale(self.game.character_spritesheet.get_sprite(6, 196, self.width, self.height))
                self.idle_right = self.scale(self.game.character_spritesheet.get_sprite(6, 132, self.width, self.height))


        def update(self):
                self.movement()
                self.animate()

                self.collide_enemy()

                self.rect.x += self.x_change
                self.collide_blocks('x')
                self.rect.y += self.y_change
                self.collide_blocks('y')

                self.x_change = 0
                self.y_change = 0

                self.pickup_ammo()
                self.x = self.rect.x
                self.y = self.rect.y

                if self.invincible:
                    current_time = pygame.time.get_ticks()
                    if current_time - self.invincible_timer >= self.invincible_duration:
                        self.invincible = False

        def animate(self):

                if self.facing == "down":
                        if self.y_change == 0:
                                self.image = self.idle_down
                        else:
                                self.image = self.down_animations[int(self.animation_loop)]
                                self.animation_loop += 0.1
                        if self.animation_loop >= 3:
                                self.animation_loop = 1

                if self.facing == "up":
                        if self.y_change == 0:
                                self.image = self.idle_up
                        else:
                                self.image = self.up_animations[int(self.animation_loop)]
                                self.animation_loop += 0.1
                        if self.animation_loop >= 3:
                                self.animation_loop = 1

                if self.facing == "left":
                        if self.x_change == 0:
                                self.image = self.idle_left
                        else:
                                self.image = self.left_animations[int(self.animation_loop)]
                                self.animation_loop += 0.1
                        if self.animation_loop >= 3:
                                self.animation_loop = 1

                if self.facing == "right":
                        if self.x_change == 0:
                                self.image = self.idle_right
                        else:
                                self.image = self.right_animations[int(self.animation_loop)]
                                self.animation_loop += 0.1
                        if self.animation_loop >= 3:
                                self.animation_loop = 1

        def movement(self):
                keys = pygame.key.get_pressed()

                self.x_change = 0 
                self.y_change = 0 

                if keys[CONTROLS["left"]]:
                        self.x_change -= PLAYER_SPEED
                        self.facing = 'left'
                if keys[CONTROLS["right"]]:
                        self.x_change += PLAYER_SPEED
                        self.facing = 'right'
                if keys[CONTROLS["up"]]:
                        self.y_change -= PLAYER_SPEED
                        self.facing = 'up'
                if keys[CONTROLS["down"]]:
                        self.y_change += PLAYER_SPEED
                        self.facing = 'down'

                if self.x_change != 0 and self.y_change != 0:
                        self.x_change *= 0.7071 
                        self.y_change *= 0.7071

        def collide_enemy(self):
            if self.invincible:
                return
    
            hits = pygame.sprite.spritecollide(self, self.game.enemies, False)
            if hits:
                enemy = hits[0]
        
                if isinstance(enemy, BossEnemy):
                    return
        
                remaining_damage = enemy.damage
        
                if self.shield > 0:
                    if self.shield >= remaining_damage:
                        self.shield -= remaining_damage
                        remaining_damage = 0
                    else:
                        remaining_damage -= self.shield
                        self.shield = 0
        
                self.life -= remaining_damage
                enemy.kill()
        
                self.invincible = True
                self.invincible_timer = pygame.time.get_ticks()
        
                if self.life <= 0:
                    pygame.mixer.music.fadeout(1000)
                    self.game.death_sound.play()
                    pygame.time.delay(1000)
                    self.game.game_over()


        def collide_blocks(self, direction):
                if direction == "x":
                        hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
                        if hits:
                                if self.x_change > 0:
                                        self.rect.x = hits[0].rect.left - self.rect.width

                                if self.x_change < 0:
                                        self.rect.x = hits[0].rect.right

                if direction == "y":
                        hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
                        if hits:
                                if self.y_change > 0:
                                        self.rect.y = hits[0].rect.top - self.rect.height

                                if self.y_change < 0:
                                        self.rect.y = hits[0].rect.bottom

        def pickup_ammo(self):
                hits = pygame.sprite.spritecollide(self, self.game.items, True)
                for item in hits:
                        if isinstance(item, AmmoCrate):
                                self.game.crate_pickup_sound.play()
                                self.ammo = min(self.ammo + item.ammo_amount, self.max_ammo)

                        elif isinstance(item, MedKit):
                                '''self.game.medkit_pickup_sound.play()'''
                                self.life = min(self.life + item.heal_amount, self.max_life)

                        elif isinstance(item, MiniShield):
                                '''self.game.shield_pickup_sound.play()'''
                                self.shield = min(self.shield + item.shield_amount, self.max_shield)

        def scale(self, sprite):
                sprite.set_colorkey(BLACK)
                return pygame.transform.scale(sprite, (int(self.width * 1), int(self.height * 1)))