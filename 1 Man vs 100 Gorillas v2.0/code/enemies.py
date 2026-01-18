import pygame
import random
import math
from settings import *

class Enemy(pygame.sprite.Sprite):
    def __init__(self, game, x, y, player):
        self.game = game
        self.player = player
        self._layer = ENEMY_LAYER
        self.groups = self.game.all_sprites, self.game.enemies
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x
        self.y = y
        self.width = TILESIZE
        self.height = TILESIZE

        self.x_change = 0
        self.y_change = 0
        self.facing = random.choice(['left', 'right', 'up', 'down'])
        self.animation_loop = 1

        self.image = self.game.enemy1_spritesheet.get_sprite(3, 2, self.width, self.height)
        self.image.set_colorkey(BLACK)

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        self.collision_timer = 0
        self.damage = 5
        self.score_value = 1
        self.max_health = 10
        self.health = 10
        self.dropped_loot = False

        self.path = []
        self.path_update_timer = 0
        self.path_update_interval = 500

        self.down_animations = [self.game.enemy1_spritesheet.get_sprite(6, 4, self.width, self.height),
                self.game.enemy1_spritesheet.get_sprite(70, 4, self.width, self.height),
                self.game.enemy1_spritesheet.get_sprite(136, 4, self.width, self.height)]

        self.up_animations = [self.game.enemy1_spritesheet.get_sprite(36, 68, self.width, self.height),
                self.game.enemy1_spritesheet.get_sprite(70, 68, self.width, self.height),
                self.game.enemy1_spritesheet.get_sprite(136, 68, self.width, self.height)]

        self.left_animations = [self.game.enemy1_spritesheet.get_sprite(6, 196, self.width, self.height),
                self.game.enemy1_spritesheet.get_sprite(70, 196, self.width, self.height),
                self.game.enemy1_spritesheet.get_sprite(136, 196, self.width, self.height)]       

        self.right_animations = [self.game.enemy1_spritesheet.get_sprite(6, 132, self.width, self.height),
                self.game.enemy1_spritesheet.get_sprite(70, 132, self.width, self.height),
                self.game.enemy1_spritesheet.get_sprite(136, 132, self.width, self.height)]
                
        self.idle_down = self.game.enemy1_spritesheet.get_sprite(6, 4, self.width, self.height)
        self.idle_up = self.game.enemy1_spritesheet.get_sprite(6, 68, self.width, self.height)
        self.idle_left = self.game.enemy1_spritesheet.get_sprite(6, 196, self.width, self.height)
        self.idle_right = self.game.enemy1_spritesheet.get_sprite(6, 132, self.width, self.height)

    def draw_health_bar(self, camera):
        if self.health > 0:
            bar_width = self.rect.width
            bar_height = 5
            fill = (self.health / self.max_health) * bar_width
        
            x = self.rect.x + camera.camera.x
            y = self.rect.y + camera.camera.y - bar_height - 2
        
            pygame.draw.rect(self.game.screen, RED, (x, y, bar_width, bar_height))
            pygame.draw.rect(self.game.screen, GREEN, (x, y, fill, bar_height))

    def update(self):
        self.movement()
        self.animate()

        # Store old position
        old_x = self.rect.x
        old_y = self.rect.y
        
        # Try X movement
        self.rect.x += self.x_change
        self.collide_blocks('x')
        
        # Try Y movement
        self.rect.y += self.y_change
        self.collide_blocks('y')
        
        # If completely stuck on both axes, force path recalculation
        if self.rect.x == old_x and self.rect.y == old_y and (self.x_change != 0 or self.y_change != 0):
            self.path = []  # Clear path to force recalculation
        
        # Reset changes
        self.x_change = 0
        self.y_change = 0

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
        current_time = pygame.time.get_ticks()
        
        if current_time - self.path_update_timer >= self.path_update_interval:
            self.path = self.game.pathfinding.find_path(
                (self.rect.centerx, self.rect.centery),
                (self.player.rect.centerx, self.player.rect.centery)
            )
            self.path_update_timer = current_time
        
        if len(self.path) > 1:
            target_x, target_y = self.path[1] 
            
            dx = target_x - self.rect.centerx
            dy = target_y - self.rect.centery
            distance = math.hypot(dx, dy)
            
            if distance != 0:
                dx, dy = dx / distance, dy / distance
                
                self.x_change = dx * ENEMY1_SPEED
                self.y_change = dy * ENEMY1_SPEED
                
                # Update facing direction
                if abs(dx) > abs(dy):
                    if dx < 0:
                        self.facing = 'left'
                    else:
                        self.facing = 'right'
                else:
                    if dy < 0:
                        self.facing = 'up'
                    else:
                        self.facing = 'down'
                
                if distance < TILESIZE / 2:
                    self.path.pop(0)

    def collide_blocks(self, direction):
        hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
        
        if direction == "x":
            if hits:
                if self.x_change > 0:
                    self.rect.x = hits[0].rect.left - self.rect.width
                elif self.x_change < 0:
                    self.rect.x = hits[0].rect.right
                self.x_change = 0  # Stop X movement but Y can still happen

        if direction == "y":
            if hits:
                if self.y_change > 0:
                    self.rect.y = hits[0].rect.top - self.rect.height
                elif self.y_change < 0:
                    self.rect.y = hits[0].rect.bottom
                self.y_change = 0  # Stop Y movement but X can still happen

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.die()

    def die(self):
        self.game.score += self.score_value
        self.drop_loot()
        self.kill()

    def drop_loot(self):
        from items import AmmoCrate, MedKit, MiniShield
        if not self.dropped_loot:
            self.dropped_loot = True
            roll = random.random()
            if roll < 0.15:
                AmmoCrate(self.game, self.rect.x, self.rect.y)
            elif roll < 0.25:
                MedKit(self.game, self.rect.x, self.rect.y)
            elif roll < 0.30:
                MiniShield(self.game, self.rect.x, self.rect.y)


class Enemy2(Enemy):
    def __init__(self, game, x, y, player):
        super().__init__(game, x, y, player)
        
        sprite = self.game.enemy2_spritesheet.get_sprite(1, 1, self.width, self.height)
        self.image = self.scale(sprite)
        
        self.damage = 10
        self.score_value = 2
        self.max_health = 20
        self.health = 20

        self.down_animations = [self.scale(self.game.enemy2_spritesheet.get_sprite(6, 4, self.width, self.height)),
                self.scale(self.game.enemy2_spritesheet.get_sprite(70, 4, self.width, self.height)),
                self.scale(self.game.enemy2_spritesheet.get_sprite(136, 4, self.width, self.height))]

        self.up_animations = [self.scale(self.game.enemy2_spritesheet.get_sprite(3, 68, self.width, self.height)),
                self.scale(self.game.enemy2_spritesheet.get_sprite(70, 68, self.width, self.height)),
                self.scale(self.game.enemy2_spritesheet.get_sprite(136, 68, self.width, self.height))]

        self.left_animations = [self.scale(self.game.enemy2_spritesheet.get_sprite(3, 196, self.width, self.height)),
                self.scale(self.game.enemy2_spritesheet.get_sprite(70, 196, self.width, self.height)),
                self.scale(self.game.enemy2_spritesheet.get_sprite(136, 196, self.width, self.height))]       

        self.right_animations = [self.scale(self.game.enemy2_spritesheet.get_sprite(3, 132, self.width, self.height)),
                self.scale(self.game.enemy2_spritesheet.get_sprite(70, 132, self.width, self.height)),
                self.scale(self.game.enemy2_spritesheet.get_sprite(136, 132, self.width, self.height))]
                
        self.idle_down = self.scale(self.game.enemy2_spritesheet.get_sprite(6, 4, self.width, self.height))
        self.idle_up = self.scale(self.game.enemy2_spritesheet.get_sprite(6, 68, self.width, self.height))
        self.idle_left = self.scale(self.game.enemy2_spritesheet.get_sprite(6, 196, self.width, self.height))
        self.idle_right = self.scale(self.game.enemy2_spritesheet.get_sprite(6, 132, self.width, self.height))

    def movement(self):
        current_time = pygame.time.get_ticks()
        
        if current_time - self.path_update_timer >= self.path_update_interval:
            self.path = self.game.pathfinding.find_path(
                (self.rect.centerx, self.rect.centery),
                (self.player.rect.centerx, self.player.rect.centery)
            )
            self.path_update_timer = current_time
        
        if len(self.path) > 1:
            target_x, target_y = self.path[1] 
            
            dx = target_x - self.rect.centerx
            dy = target_y - self.rect.centery
            distance = math.hypot(dx, dy)
            
            if distance != 0:
                dx, dy = dx / distance, dy / distance
                
                self.x_change = dx * ENEMY2_SPEED
                self.y_change = dy * ENEMY2_SPEED
                
                if abs(dx) > abs(dy):
                    if dx < 0:
                        self.facing = 'left'
                    else:
                        self.facing = 'right'
                else:
                    if dy < 0:
                        self.facing = 'up'
                    else:
                        self.facing = 'down'
                
                if distance < TILESIZE / 2:
                    self.path.pop(0)

    def draw_health_bar(self, camera):
        if self.health > 0:
            bar_width = self.rect.width
            bar_height = 5
            fill = (self.health / self.max_health) * bar_width
        
            x = self.rect.x + camera.camera.x
            y = self.rect.y + camera.camera.y - bar_height - 2
        
            pygame.draw.rect(self.game.screen, RED, (x, y, bar_width, bar_height))
            pygame.draw.rect(self.game.screen, GREEN, (x, y, fill, bar_height))

    def scale(self, sprite):
        sprite.set_colorkey(BLACK)
        return pygame.transform.scale(sprite, (int(self.width * 1.15), int(self.height * 1.15)))


class Enemy3(Enemy):
    def __init__(self, game, x, y, player):
        super().__init__(game, x, y, player)
        
        sprite = self.game.enemy3_spritesheet.get_sprite(1, 1, self.width, self.height)
        self.image = self.scale(sprite)
        
        self.damage = 15
        self.score_value = 3
        self.max_health = 30
        self.health = 30

        self.down_animations = [self.scale(self.game.enemy3_spritesheet.get_sprite(6, 4, self.width, self.height)),
                self.scale(self.game.enemy3_spritesheet.get_sprite(70, 4, self.width, self.height)),
                self.scale(self.game.enemy3_spritesheet.get_sprite(136, 4, self.width, self.height))]

        self.up_animations = [self.scale(self.game.enemy3_spritesheet.get_sprite(3, 68, self.width, self.height)),
                self.scale(self.game.enemy3_spritesheet.get_sprite(70, 68, self.width, self.height)),
                self.scale(self.game.enemy3_spritesheet.get_sprite(136, 68, self.width, self.height))]

        self.left_animations = [self.scale(self.game.enemy3_spritesheet.get_sprite(3, 196, self.width, self.height)),
                self.scale(self.game.enemy3_spritesheet.get_sprite(70, 196, self.width, self.height)),
                self.scale(self.game.enemy3_spritesheet.get_sprite(136, 196, self.width, self.height))]       

        self.right_animations = [self.scale(self.game.enemy3_spritesheet.get_sprite(3, 132, self.width, self.height)),
                self.scale(self.game.enemy3_spritesheet.get_sprite(70, 132, self.width, self.height)),
                self.scale(self.game.enemy3_spritesheet.get_sprite(136, 132, self.width, self.height))]
                
        self.idle_down = self.scale(self.game.enemy3_spritesheet.get_sprite(6, 4, self.width, self.height))
        self.idle_up = self.scale(self.game.enemy3_spritesheet.get_sprite(6, 68, self.width, self.height))
        self.idle_left = self.scale(self.game.enemy3_spritesheet.get_sprite(6, 196, self.width, self.height))
        self.idle_right = self.scale(self.game.enemy3_spritesheet.get_sprite(6, 132, self.width, self.height))

    def movement(self):
        current_time = pygame.time.get_ticks()
        
        if current_time - self.path_update_timer >= self.path_update_interval:
            self.path = self.game.pathfinding.find_path(
                (self.rect.centerx, self.rect.centery),
                (self.player.rect.centerx, self.player.rect.centery)
            )
            self.path_update_timer = current_time
        
        if len(self.path) > 1:
            target_x, target_y = self.path[1] 
            
            dx = target_x - self.rect.centerx
            dy = target_y - self.rect.centery
            distance = math.hypot(dx, dy)
            
            if distance != 0:
                dx, dy = dx / distance, dy / distance
                
                self.x_change = dx * ENEMY3_SPEED
                self.y_change = dy * ENEMY3_SPEED
                
                if abs(dx) > abs(dy):
                    if dx < 0:
                        self.facing = 'left'
                    else:
                        self.facing = 'right'
                else:
                    if dy < 0:
                        self.facing = 'up'
                    else:
                        self.facing = 'down'
                
                if distance < TILESIZE / 2:
                    self.path.pop(0)

    def draw_health_bar(self, camera):
        if self.health > 0:
            bar_width = self.rect.width
            bar_height = 5
            fill = (self.health / self.max_health) * bar_width
        
            x = self.rect.x + camera.camera.x
            y = self.rect.y + camera.camera.y - bar_height - 2
        
            pygame.draw.rect(self.game.screen, RED, (x, y, bar_width, bar_height))
            pygame.draw.rect(self.game.screen, GREEN, (x, y, fill, bar_height))

    def scale(self, sprite):
        sprite.set_colorkey(BLACK)
        return pygame.transform.scale(sprite, (int(self.width * 1.25), int(self.height * 1.25)))


class Enemy4(Enemy):
    def __init__(self, game, x, y, player):
        super().__init__(game, x, y, player)
        
        sprite = self.game.enemy4_spritesheet.get_sprite(1, 1, self.width, self.height)
        self.image = self.scale(sprite)
        
        self.damage = 20
        self.score_value = 5
        self.max_health = 40
        self.health = 40

        self.down_animations = [self.scale(self.game.enemy4_spritesheet.get_sprite(6, 4, self.width, self.height)),
                self.scale(self.game.enemy4_spritesheet.get_sprite(70, 4, self.width, self.height)),
                self.scale(self.game.enemy4_spritesheet.get_sprite(136, 4, self.width, self.height))]

        self.up_animations = [self.scale(self.game.enemy4_spritesheet.get_sprite(3, 68, self.width, self.height)),
                self.scale(self.game.enemy4_spritesheet.get_sprite(70, 68, self.width, self.height)),
                self.scale(self.game.enemy4_spritesheet.get_sprite(136, 68, self.width, self.height))]

        self.left_animations = [self.scale(self.game.enemy4_spritesheet.get_sprite(3, 196, self.width, self.height)),
                self.scale(self.game.enemy4_spritesheet.get_sprite(70, 196, self.width, self.height)),
                self.scale(self.game.enemy4_spritesheet.get_sprite(136, 196, self.width, self.height))]       

        self.right_animations = [self.scale(self.game.enemy4_spritesheet.get_sprite(3, 132, self.width, self.height)),
                self.scale(self.game.enemy4_spritesheet.get_sprite(70, 132, self.width, self.height)),
                self.scale(self.game.enemy4_spritesheet.get_sprite(136, 132, self.width, self.height))]
                
        self.idle_down = self.scale(self.game.enemy4_spritesheet.get_sprite(6, 4, self.width, self.height))
        self.idle_up = self.scale(self.game.enemy4_spritesheet.get_sprite(6, 68, self.width, self.height))
        self.idle_left = self.scale(self.game.enemy4_spritesheet.get_sprite(6, 196, self.width, self.height))
        self.idle_right = self.scale(self.game.enemy4_spritesheet.get_sprite(6, 132, self.width, self.height))

    def movement(self):
        current_time = pygame.time.get_ticks()
        
        if current_time - self.path_update_timer >= self.path_update_interval:
            self.path = self.game.pathfinding.find_path(
                (self.rect.centerx, self.rect.centery),
                (self.player.rect.centerx, self.player.rect.centery)
            )
            self.path_update_timer = current_time
        
        if len(self.path) > 1:
            target_x, target_y = self.path[1] 
            
            dx = target_x - self.rect.centerx
            dy = target_y - self.rect.centery
            distance = math.hypot(dx, dy)
            
            if distance != 0:
                dx, dy = dx / distance, dy / distance
                
                self.x_change = dx * ENEMY4_SPEED
                self.y_change = dy * ENEMY4_SPEED
                
                if abs(dx) > abs(dy):
                    if dx < 0:
                        self.facing = 'left'
                    else:
                        self.facing = 'right'
                else:
                    if dy < 0:
                        self.facing = 'up'
                    else:
                        self.facing = 'down'
                
                if distance < TILESIZE / 2:
                    self.path.pop(0)

    def draw_health_bar(self, camera):
        if self.health > 0:
            bar_width = self.rect.width
            bar_height = 5
            fill = (self.health / self.max_health) * bar_width
        
            x = self.rect.x + camera.camera.x
            y = self.rect.y + camera.camera.y - bar_height - 2
        
            pygame.draw.rect(self.game.screen, RED, (x, y, bar_width, bar_height))
            pygame.draw.rect(self.game.screen, GREEN, (x, y, fill, bar_height))

    def scale(self, sprite):
        sprite.set_colorkey(BLACK)
        return pygame.transform.scale(sprite, (int(self.width * 1.5), int(self.height * 1.5)))


class BossEnemy(pygame.sprite.Sprite):
        def __init__(self, game, x, y, player):
                self.game = game
                self.player = player
                self._layer = ENEMY_LAYER
                self.groups = self.game.all_sprites, self.game.enemies
                pygame.sprite.Sprite.__init__(self, self.groups)

                self.x = x
                self.y = y
                self.width = TILESIZE
                self.height = TILESIZE

                self.x_change = 0
                self.y_change = 0

                self.facing = random.choice(['left', 'right', 'up', 'down'])
                self.animation_loop = 1

                sprite = self.game.boss_spritesheet.get_sprite(1, 1, self.width, self.height)
                self.image = self.scale(sprite)

                self.rect = self.image.get_rect()
                self.rect.x = self.x
                self.rect.y = self.y

                self.collision_timer = 0

                # Changed from instant kill to 25 damage per hit
                self.damage = 50
                self.score_value = 10
                self.max_health = 200
                self.health = 200

                # Attack cooldown system
                self.attack_cooldown = 1000  # 1 second between attacks in milliseconds
                self.last_attack_time = 0
                
                # Stun system
                self.stunned = False
                self.stun_duration = 500  # 1 second stun after attacking
                self.stun_end_time = 0

                self.down_animations = [self.scale(self.game.boss_spritesheet.get_sprite(6, 4, self.width, self.height)),
                        self.scale(self.game.boss_spritesheet.get_sprite(70, 4, self.width, self.height)),
                        self.scale(self.game.boss_spritesheet.get_sprite(136, 4, self.width, self.height))]

                self.up_animations = [self.scale(self.game.boss_spritesheet.get_sprite(3, 68, self.width, self.height)),
                        self.scale(self.game.boss_spritesheet.get_sprite(70, 68, self.width, self.height)),
                        self.scale(self.game.boss_spritesheet.get_sprite(136, 68, self.width, self.height))]

                self.left_animations = [self.scale(self.game.boss_spritesheet.get_sprite(3, 196, self.width, self.height)),
                        self.scale(self.game.boss_spritesheet.get_sprite(70, 196, self.width, self.height)),
                        self.scale(self.game.boss_spritesheet.get_sprite(136, 196, self.width, self.height))]       

                self.right_animations = [self.scale(self.game.boss_spritesheet.get_sprite(3, 132, self.width, self.height)),
                        self.scale(self.game.boss_spritesheet.get_sprite(70, 132, self.width, self.height)),
                        self.scale(self.game.boss_spritesheet.get_sprite(136, 132, self.width, self.height))]
                
                self.idle_down = self.scale(self.game.boss_spritesheet.get_sprite(6, 4, self.width, self.height))
                self.idle_up = self.scale(self.game.boss_spritesheet.get_sprite(6, 68, self.width, self.height))
                self.idle_left = self.scale(self.game.boss_spritesheet.get_sprite(6, 196, self.width, self.height))
                self.idle_right = self.scale(self.game.boss_spritesheet.get_sprite(6, 132, self.width, self.height))


        def update(self):
                # Check if stun has expired
                current_time = pygame.time.get_ticks()
                if self.stunned and current_time >= self.stun_end_time:
                        self.stunned = False
                
                # Only move if not stunned
                if not self.stunned:
                        self.movement()
                
                self.animate()
                self.attack_player()  # New method to handle attacks

                self.rect.x += self.x_change
                self.collide_blocks('x')

                self.rect.y += self.y_change
                self.collide_blocks('y')

                self.x_change = 0
                self.y_change = 0

        def attack_player(self):
                """Check if boss can attack the player"""
                current_time = pygame.time.get_ticks()
                
                # Check if enough time has passed since last attack
                if current_time - self.last_attack_time < self.attack_cooldown:
                        return
                
                # Check if player is close enough to attack
                if self.rect.colliderect(self.player.rect):
                        # Only attack if player is not invincible
                        if not self.player.invincible:
                                # Calculate damage after shield absorption
                                remaining_damage = self.damage

                                if self.player.shield > 0:
                                        if self.player.shield >= remaining_damage:
                                                # Shield absorbs all damage
                                                self.player.shield -= remaining_damage
                                                remaining_damage = 0
                                        else:
                                                # Shield absorbs partial damage
                                                remaining_damage -= self.player.shield
                                                self.player.shield = 0

                                # Apply remaining damage to health
                                self.player.life -= remaining_damage

                                # Set player invincibility frames
                                self.player.invincible = True
                                self.player.invincible_timer = pygame.time.get_ticks()

                                # Update last attack time
                                self.last_attack_time = current_time
                                
                                # Stun the boss after attacking
                                self.stunned = True
                                self.stun_end_time = current_time + self.stun_duration

                                # Check if player died
                                if self.player.life <= 0:
                                        pygame.mixer.music.fadeout(1000)
                                        self.game.death_sound.play()
                                        pygame.time.delay(1000)
                                        self.game.game_over()

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
                player_x = self.player.rect.x
                player_y = self.player.rect.y

                dx = player_x - self.rect.x
                dy = player_y - self.rect.y

                distance = math.hypot(dx, dy)

                if distance != 0:
                        dx += random.uniform(-5, 5)
                        dy += random.uniform(-5, 5)

                        dx, dy = dx / math.hypot(dx, dy), dy / math.hypot(dx, dy)

                        self.x_change = dx * ENEMY2_SPEED
                        self.y_change = dy * ENEMY2_SPEED

                if abs(dx) > abs(dy):
                        if dx < 0:
                                self.facing = 'left'
                        else:
                                self.facing = 'right'
                else:
                        if dy < 0:
                                self.facing = 'up'
                        else:
                                self.facing = 'down'

        def collide_blocks(self, direction):
                if direction == "x":
                        hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
                        if hits:
                                if self.x_change > 0:
                                        self.rect.x = hits[0].rect.left - self.rect.width
                                elif self.x_change < 0:
                                        self.rect.x = hits[0].rect.right
                                self.x_change = 0

                if direction == "y":
                        hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
                        if hits:
                                if self.y_change > 0:
                                        self.rect.y = hits[0].rect.top - self.rect.height
                                elif self.y_change < 0:
                                        self.rect.y = hits[0].rect.bottom
                                self.y_change = 0

                if hits:
                        self.collision_timer += 1
                        if self.collision_timer > 30:
                                self.x_change = -self.x_change
                                self.y_change = -self.y_change
                                self.collision_timer = 0
                        else:
                                self.collision_timer = 0

        def take_damage(self, amount):
                self.health -= amount
                if self.health <= 0:
                    self.game.score += self.score_value
                    pygame.mixer.music.fadeout(1000)
                    self.game.bossdeath_sound.play()
                    pygame.time.delay(1000)
                    self.game.win_screen()
                    self.kill()

        def scale(self, sprite):
                sprite.set_colorkey(BLACK)
                return pygame.transform.scale(sprite, (int(self.width * 2.5), int(self.height * 2.5)))