import sys
import random
from PIL import Image
from pytmx.util_pygame import load_pygame
from settings import *
from sprites import Spritesheet, Button, Block, Decoration, Barrier
from player import Player
from enemies import Enemy, Enemy2, Enemy3, Enemy4, BossEnemy
from attacks import Attack, Bullet
from items import AmmoCrate, MedKit, MiniShield
from level import TiledMap, Camera
from pathfinding_helper import PathfindingManager

def load_gif_frames(gif_path, size=(1280, 720)):
        gif_image = Image.open(gif_path)
        frames = []
        try:
                while True:
                        frame = gif_image.copy().convert("RGB")  # Ensure RGB for Pygame compatibility
                        frame = frame.resize(size)
                        frame_surface = pygame.image.fromstring(frame.tobytes(), frame.size, frame.mode)
                        frames.append(frame_surface)
                        gif_image.seek(gif_image.tell() + 1)
        except EOFError:
                pass
        return frames

def play_intro_gif(screen, frames, clock, fps=20):
        for frame in frames:
                screen.blit(frame, (0, 0))
                pygame.display.update()
                clock.tick(fps)

gif_frames = load_gif_frames('../ui/introbackground.gif')

class Game:
        def __init__(self):
                self.monitor_size = [pygame.display.Info().current_w, pygame.display.Info().current_h]
                pygame.init()
                self.screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT), pygame.RESIZABLE)
                self.clock = pygame.time.Clock()
                self.running = True
                self.font = pygame.font.Font('../text/TTOctosquaresXBoldIt.ttf', 72)
                self.tracker_font = pygame.font.Font('../text/TTOctosquaresXBoldIt.ttf', 32)
                self.life_font = pygame.font.Font('../text/TTOctosquaresXBoldIt.ttf', 20)

                self.character_spritesheet = Spritesheet('../player/character.png')
                self.terrian_spritesheet = Spritesheet('../images/map/terrain.png')
                self.enemy1_spritesheet = Spritesheet('../enemy/enemy1.png')
                self.enemy2_spritesheet = Spritesheet('../enemy/enemy2.png')
                self.enemy3_spritesheet = Spritesheet('../enemy/enemy3.png')
                self.enemy4_spritesheet = Spritesheet('../enemy/enemy4.png')
                self.attack_spritesheet = Spritesheet('../player/attack.png')
                self.bullet_spritesheet = Spritesheet('../player/shot.png')
                self.ammo_spritesheet = Spritesheet('../images/consumeables/crate.png')
                self.medkit_spritesheet = Spritesheet('../images/consumeables/medkit.png')
                self.minishield_spritesheet = Spritesheet('../images/consumeables/minishield.png')
                self.boss_spritesheet = Spritesheet('../enemy/boss.png')
                self.intro_backgroud = pygame.image.load('../ui/introbackground.png')
                self.go_background = pygame.image.load('../ui/gameover.png')
                self.wg_background = pygame.image.load('../ui/win.png')

                pygame.display.set_caption("1 Man vs 100 Gorillas")

                self.fullscreen = False
                self.score = 0
                self.highscore = 0
                self.highscore = self.load_highscore()
                self.boss_level_started = False
                self.boss_defeated = False
                self.best_time = None

                self.enemy_spawn_points = []

                self.enemy_spawn_timer = pygame.time.get_ticks()
                self.enemy_spawn_interval = 1000

                self.enemy_types = [Enemy]
                self.spawn_weights = [1.0]
                self.all_enemy_types = [Enemy, Enemy2, Enemy3, Enemy4]
                self.all_enemy_weights = [0.5, 0.25, 0.15, 0.1]


                self.crate_pickup_sound = pygame.mixer.Sound("../audio/crate.wav")
                self.crate_pickup_sound.set_volume(1.0)

                self.death_sound = pygame.mixer.Sound("../audio/death.wav")
                self.death_sound.set_volume(1.0)

                self.bossspawn_sound = pygame.mixer.Sound("../audio/bossspawn.wav")
                self.bossspawn_sound.set_volume(1.0)

                self.bossdeath_sound = pygame.mixer.Sound("../audio/bossdeath.wav")
                self.bossdeath_sound.set_volume(1.0)

                self.bullet_sound = pygame.mixer.Sound("../audio/bullet.wav")
                self.bullet_sound.set_volume(1.0)

                self.melee_sound = pygame.mixer.Sound("../audio/melee.wav")
                self.melee_sound.set_volume(1.0)

                self.settings_icon = pygame.image.load('../ui/settings_icon.png').convert_alpha()
                self.settings_icon = pygame.transform.scale(self.settings_icon, (50, 50))

                self.show_msg = False
                self.msg_timer = 0

        def load_highscore(self):
                try:
                        with open("highscore.txt", "r") as f:
                                return int(f.read())
                except (FileNotFoundError, ValueError):
                        return 0


        def create_tilemap(self):
                #load map
                self.map = TiledMap('../data/maps/world.tmx')
                self.map_img = self.map.make_map()
                self.map_rect = self.map_img.get_rect()

                #create camera
                self.camera = Camera(self.map.width, self.map.height)

                self.enemy_spawn_points = [
                        (800, 600), (1200, 800), (1600, 1000), (2000, 1200),
                        (1000, 1400), (1400, 1600), (1800, 1800), (2200, 2000),
                        (1000, 1200), (1400, 1400), (1800, 1600),
                ]

                self.boss_barrier = None
    
                collisions_layer = self.map.tmx_data.get_layer_by_name('Collisions')
                if collisions_layer:
                        for obj in collisions_layer:
                                if hasattr(obj, 'name') and obj.name == 'barrier':
                                        self.boss_barrier = Barrier(self, obj.x, obj.y, obj.width, obj.height)
                                else:
                                        Block(self, obj.x, obj.y, obj.width, obj.height)

                objects_layer = self.map.tmx_data.get_layer_by_name('Objects')
                if objects_layer:
                        for obj in objects_layer:
                                tile = self.map.tmx_data.get_tile_image_by_gid(obj.gid)
                                if tile:
                                        Decoration(self, obj.x, obj.y, tile)
    
                entities_layer = self.map.tmx_data.get_layer_by_name('Entities')
                if entities_layer:
                        for obj in entities_layer:
                                if obj.name == 'Player':
                                        self.player = Player(self, obj.x, obj.y)

                self.pathfinding = PathfindingManager(self)

                initial_spawns = random.sample(self.enemy_spawn_points, min(5, len(self.enemy_spawn_points)))
                for x, y in initial_spawns:
                        Enemy(self, x, y, self.player)



        def new(self):
                self.playing = True
                self.start_time = pygame.time.get_ticks()
                self.timer_running = True
                pygame.mixer.init()
                pygame.mixer.music.load('../audio/maingame.mp3')
                pygame.mixer.music.set_volume(0.2)
                pygame.mixer.music.play(-1)

                self.all_sprites = pygame.sprite.LayeredUpdates()
                self.blocks = pygame.sprite.LayeredUpdates()
                self.enemies = pygame.sprite.LayeredUpdates()
                self.attacks = pygame.sprite.LayeredUpdates()
                self.items = pygame.sprite.LayeredUpdates()
                self.bullet_group = pygame.sprite.Group()

                self.create_tilemap()

                self.score = 0
                self.best_time = None

                self.enemy_types = [Enemy]
                self.spawn_weights = [1.0]
                self.all_enemy_types = [Enemy, Enemy2, Enemy3, Enemy4]
                self.all_enemy_weights = [0.5, 0.25, 0.15, 0.1]

                self.boss_level_started = False
                self.boss_defeated = False
                self.stop_spawning = False

        def events(self):
                for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()

                        if event.type == pygame.VIDEORESIZE:
                            if not self.fullscreen:
                                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

                        if event.type == pygame.KEYDOWN:
                            if event.key == CONTROLS["resize"]:
                                self.fullscreen = not self.fullscreen
                                if self.fullscreen:
                                    self.screen = pygame.display.set_mode((self.monitor_size), pygame.FULLSCREEN)
                                else:
                                    self.screen = pygame.display.set_mode((screen.get_width(), screen.get_height()), pygame.RESIZABLE)


                        if event.type == pygame.KEYDOWN:
                                if event.key == CONTROLS["melee"]:
                                        self.trigger_melee()
                                if event.key == CONTROLS["shoot"] and self.player.ammo > 0:
                                        self.trigger_shoot()

                        if event.type == pygame.MOUSEBUTTONDOWN:
                                if event.button == CONTROLS["melee"]:
                                        self.trigger_melee()
                                if event.button == CONTROLS["shoot"] and self.player.ammo > 0:
                                        self.trigger_shoot()

        def trigger_shoot(self):
                direction = self.player.facing
    
                if direction == "up":
                        self.bullet_sound.play()
                        bullet_x = self.player.rect.centerx
                        bullet_y = self.player.rect.top + self.player.rect.height // 3
                elif direction == "down":
                        self.bullet_sound.play()
                        bullet_x = self.player.rect.centerx
                        bullet_y = self.player.rect.bottom - self.player.rect.height // 3
                elif direction == "left":
                        self.bullet_sound.play()
                        bullet_x = self.player.rect.left
                        bullet_y = self.player.rect.centery
                elif direction == "right":
                        self.bullet_sound.play()
                        bullet_x = self.player.rect.right
                        bullet_y = self.player.rect.centery
    
                bullet = Bullet(self, bullet_x, bullet_y, direction)
                self.bullet_group.add(bullet)
                self.all_sprites.add(bullet)
                self.player.ammo -= 1

        def trigger_melee(self):
                self.melee_sound.play()
    
                if self.player.facing == 'up':
                        Attack(self, self.player.rect.x, self.player.rect.y - TILESIZE)
                elif self.player.facing == 'down':
                        Attack(self, self.player.rect.x, self.player.rect.y + TILESIZE)
                elif self.player.facing == 'left':
                        Attack(self, self.player.rect.x - TILESIZE, self.player.rect.y)
                elif self.player.facing == 'right':
                        Attack(self, self.player.rect.x + TILESIZE, self.player.rect.y)


        def update(self):
                self.all_sprites.update()
                self.camera.update(self.player)

                if not self.boss_level_started:
                        if self.score >= 25 and len(self.enemy_types) == 1:
                                self.enemy_types = self.all_enemy_types[:2]
                                self.spawn_weights = self.all_enemy_weights[:2]

                        if self.score >= 50 and len(self.enemy_types) == 2:
                                self.enemy_types = self.all_enemy_types[:3]
                                self.spawn_weights = self.all_enemy_weights[:3]

                        if self.score >= 75 and len(self.enemy_types) == 3:
                                self.enemy_types = self.all_enemy_types[:]
                                self.spawn_weights = self.all_enemy_weights[:]

                        if not hasattr(self, 'stop_spawning') or not self.stop_spawning:
                                self.spawn_enemies()

                if self.score >= 150 and self.boss_barrier:
                        self.show_msg = True
                        self.msg_timer = pygame.time.get_ticks() + 3000
                        print("Boss Room has now opened!!")
                        self.boss_barrier.remove_barrier()
                        self.boss_barrier = None

                        for enemy in list(self.enemies):
                                enemy.kill()

                        self.stop_spawning = True
    
                boss_trigger_rect = pygame.Rect(3300, 1600, 500, 500) 

    
                if self.score >= 150 and not self.boss_level_started:
                        if boss_trigger_rect.colliderect(self.player.rect):
                                pygame.mixer.music.stop()
                                self.boss_level_started = True
                                self.play_cutscene()
                                self.load_boss_level()

                if self.score > self.highscore:
                       self.highscore = self.score

                if self.timer_running:
                        current_time = pygame.time.get_ticks()
                        self.elapsed_time = (current_time - self.start_time) / 1000


        def spawn_enemies(self):
                now = pygame.time.get_ticks()

                available_spawns = [p for p in self.enemy_spawn_points
                        if not any(e.rect.topleft == p for e in self.enemies)]

                enemy_limit = 5

                if len(self.enemies) < enemy_limit and now - self.enemy_spawn_timer >= self.enemy_spawn_interval:
                        if available_spawns:
                                spawn_pos = random.choice(available_spawns)
                                enemy_class = random.choices(self.enemy_types, weights=self.spawn_weights, k=1)[0]
                                enemy_class(self, spawn_pos[0], spawn_pos[1], self.player)
                                self.enemy_spawn_timer = now

        def draw_coordinates(self):
                coord_text = self.tracker_font.render(
                        f"X: {int(self.player.rect.x)} Y: {int(self.player.rect.y)}", 
                        True, 
                        BLACK
                )
                coord_rect = coord_text.get_rect()
                coord_rect.topright = (self.screen.get_width() - 10, 50)  # 10px from right, 50px from top
                self.screen.blit(coord_text, coord_rect)


        def draw(self):
                self.screen.fill(BLACK)

                self.screen.blit(self.map_img, self.camera.apply_rect(self.map_rect))
        
                for sprite in self.all_sprites:
                        self.screen.blit(sprite.image, self.camera.apply(sprite))

                for enemy in self.enemies:
                        if isinstance(enemy, BossEnemy):
                                self.draw_boss_healthbar(enemy)
                        else:
                                enemy.draw_health_bar(self.camera)

                if self.show_msg:
                        if pygame.time.get_ticks() < self.msg_timer:
                                msg = self.tracker_font.render("Boss Room has now opened!!", True, BLACK)
                                self.screen.blit(msg, (WIN_WIDTH // 2 - 200, 100))
                        else:
                                self.show_msg = False


                self.draw_score()
                self.draw_lives()
                self.draw_ammo()
                self.draw_highscore()
                self.draw_speedruntimer()
                #self.draw_coordinates()

                self.clock.tick(FPS)
                pygame.display.update()

        def main(self):
                while self.playing:
                        self.events()
                        self.update()
                        self.draw()

        def draw_boss_healthbar(self, boss):
                bar_width = 400
                bar_height = 30
                bar_x = (WIN_WIDTH - bar_width) // 2
                bar_y = 30
                fill = (boss.health / boss.max_health) * bar_width

                pygame.draw.rect(self.screen, RED, (bar_x, bar_y, bar_width, bar_height))
                pygame.draw.rect(self.screen, GREEN, (bar_x, bar_y, fill, bar_height))
                pygame.draw.rect(self.screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)

        def play_cutscene(self):
                cutscene_frames = load_gif_frames("../ui/cutscene.gif", size=(1280, 720))
                play_intro_gif(self.screen, cutscene_frames, self.clock, fps=15)
                del cutscene_frames

        def load_boss_level(self):
                current_health = self.player.life
                current_shield = self.player.shield
                current_ammo = self.player.ammo

                for sprite in self.all_sprites:
                        sprite.kill()
                for enemy in self.enemies:
                        enemy.kill()

                self.all_sprites = pygame.sprite.LayeredUpdates()
                self.blocks = pygame.sprite.LayeredUpdates()
                self.enemies = pygame.sprite.LayeredUpdates()
                self.attacks = pygame.sprite.LayeredUpdates()
                self.items = pygame.sprite.LayeredUpdates()

                pygame.mixer.init()
                pygame.mixer.music.load('../audio/boss.mp3')
                pygame.mixer.music.set_volume(0.2)
                pygame.mixer.music.play(-1)

                self.map = TiledMap('../data/maps/boss_arena.tmx') 
                self.map_img = self.map.make_map()
                self.map_rect = self.map_img.get_rect()
                self.camera = Camera(self.map.width, self.map.height)

                collisions_layer = self.map.tmx_data.get_layer_by_name('Collisions')
                if collisions_layer:
                        for obj in collisions_layer:
                                Block(self, obj.x, obj.y, obj.width, obj.height)

                objects_layer = self.map.tmx_data.get_layer_by_name('Objects')
                if objects_layer:
                        for obj in objects_layer:
                                tile = self.map.tmx_data.get_tile_image_by_gid(obj.gid)
                                if tile:
                                        Decoration(self, obj.x, obj.y, tile)

                entities_layer = self.map.tmx_data.get_layer_by_name('Entities')
                if entities_layer:
                        for obj in entities_layer:
                                if obj.name == 'Player':
                                        self.player = Player(self, obj.x, obj.y)
                                        self.player.life = current_health
                                        self.player.shield = current_shield
                                        self.player.ammo = current_ammo

                                elif obj.name == 'Enemy':
                                        BossEnemy(self, obj.x, obj.y, self.player)
                                        self.bossspawn_sound.play()

        def game_over(self):
                self.timer_running = False
                pygame.mixer.music.stop()
                text = self.font.render('Game Over', True , WHITE)
                text_rect = text.get_rect(center=(WIN_WIDTH/2, WIN_HEIGHT/2- 450))

                pygame.mixer.init()
                pygame.mixer.music.load('../audio/lose.mp3')
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play(-1)

                restart_button = Button(450, WIN_HEIGHT - 100, 160, 50, BLACK, WHITE, 'Restart', 32)
                quit_button = Button(650, WIN_HEIGHT - 100, 160, 50, BLACK, WHITE, 'Quit', 32)
                settings_button = Button(20, 20, 40, 40, WHITE, BLACK, '', 32) 
                settings_button.image = self.settings_icon

                for sprite in self.all_sprites:
                        sprite.kill()

                while self.running:
                        for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                        pygame.quit()
                                        sys.exit()

                        mouse_pos = pygame.mouse.get_pos()
                        mouse_pressed = pygame.mouse.get_pressed()

                        if settings_button.is_pressed(mouse_pos, mouse_pressed):
                                self.show_settings_menu()

                        if restart_button.is_pressed(mouse_pos, mouse_pressed):
                                pygame.mixer.music.play(-1)
                                self.score = 0
                                self.new()
                                self.main()

                        if quit_button.is_pressed(mouse_pos, mouse_pressed):
                                pygame.quit()
                                sys.exit()

                        self.screen.blit(self.go_background, (0,0))
                        self.screen.blit(text, text_rect)
                        self.screen.blit(restart_button.image, restart_button.rect)
                        self.screen.blit(quit_button.image, quit_button.rect)
                        self.screen.blit(settings_button.image, settings_button.rect)

                        self.clock.tick(FPS)
                        pygame.display.update()

        def win_screen(self):
                self.timer_running = False
                pygame.mixer.music.stop()

                if self.best_time is None or self.elapsed_time < self.best_time:
                        self.best_time = self.elapsed_time

                pygame.mixer.init()
                pygame.mixer.music.load('../audio/victory.mp3')
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play(-1)

                best_time_text = self.font.render(f"Best Time: {self.best_time:.2f}s", True, WHITE)
                best_time_rect = best_time_text.get_rect(center=(WIN_WIDTH / 2, WIN_HEIGHT / 2 - 200))
                text = self.font.render('You Win!', True, WHITE)
                score_text = self.font.render(f'Score: {self.score}', True, WHITE)
                score_rect = score_text.get_rect(center=(WIN_WIDTH / 2, WIN_HEIGHT / 2 - 300))
                text_rect = text.get_rect(center=(WIN_WIDTH/2, WIN_HEIGHT/2 - 400))

                restart_button = Button(450, WIN_HEIGHT - 100, 160, 50, BLACK, WHITE, 'Restart', 32)
                quit_button = Button(650, WIN_HEIGHT - 100, 160, 50, BLACK, WHITE, 'Quit', 32)
                settings_button = Button(20, 20, 40, 40, WHITE, BLACK, '', 32) 
                settings_button.image = self.settings_icon

                for sprite in self.all_sprites:
                        sprite.kill()

                while True:
                        for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                        pygame.quit()
                                        sys.exit()

                        mouse_pos = pygame.mouse.get_pos()
                        mouse_pressed = pygame.mouse.get_pressed()

                        if settings_button.is_pressed(mouse_pos, mouse_pressed):
                                self.show_settings_menu()

                        if restart_button.is_pressed(mouse_pos, mouse_pressed):
                                pygame.mixer.music.play(-1)
                                self.score = 0
                                self.new()
                                self.main()

                        if quit_button.is_pressed(mouse_pos, mouse_pressed):
                                pygame.quit()
                                sys.exit()

                        if self.score > self.highscore:
                                self.highscore = self.score

                        self.screen.blit(self.wg_background, (0,0))
                        self.screen.blit(text, text_rect)
                        self.screen.blit(score_text, score_rect)
                        self.screen.blit(best_time_text, best_time_rect)
                        self.screen.blit(restart_button.image, restart_button.rect)
                        self.screen.blit(quit_button.image, quit_button.rect)
                        self.screen.blit(settings_button.image, settings_button.rect)

                        self.clock.tick(FPS)
                        pygame.display.update()

        def intro_screen(self):
                gif_frames = load_gif_frames("../ui/introbackground.gif")
                play_intro_gif(self.screen, gif_frames, self.clock)
                del gif_frames

                intro = True

                screen_width, screen_height = self.screen.get_size()

                title = self.font.render('1 Man vs 100 Gorillas', True, WHITE)
                title_rect = title.get_rect(center=(screen_width // 2, screen_height // 2 - 400))

                width = 200
                height = 50

                x = (WIN_WIDTH - width) // 2
                y = (WIN_HEIGHT - height) // 2

                play_button = Button(540, 600, 200, 50, WHITE, BLACK, 'Play', 32)

                settings_button = Button(20, 20, 40, 40, WHITE, BLACK, '', 32) 
                settings_button.image = self.settings_icon

                while intro:
                        for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                        pygame.quit()
                                        sys.exit()


                        mouse_pos = pygame.mouse.get_pos()
                        mouse_pressed = pygame.mouse.get_pressed()

                        if settings_button.is_pressed(mouse_pos, mouse_pressed):
                                self.show_settings_menu()

                        if play_button.is_pressed(mouse_pos, mouse_pressed):
                                intro = False
                                self.new()
                                self.main()



                        self.screen.blit(self.intro_backgroud, (0,0))
                        self.screen.blit(title, title_rect)
                        self.screen.blit(play_button.image, play_button.rect)
                        self.screen.blit(settings_button.image, settings_button.rect)

                        self.clock.tick(FPS)
                        pygame.display.update()

        def show_settings_menu(self):
                settings_running = True
                waiting_for_key = False
                action_to_rebind = None

                while settings_running:
                        self.screen.fill(BLACK)
                        y_pos = 100
                        mouse_pos = pygame.mouse.get_pos()
                        mouse_pressed = pygame.mouse.get_pressed()

                        for action, current_key in CONTROLS.items():
                                if current_key in [1, 2, 3]: 
                                        mouse_names = {1: "LEFT CLICK", 2: "MID CLICK", 3: "RIGHT CLICK"}
                                        key_name = mouse_names.get(current_key)
                                else:
                                        key_name = pygame.key.name(current_key).upper()
                
                                button_text = f"{action.capitalize()}: {key_name}"
                                color = YELLOW if (waiting_for_key and action_to_rebind == action) else WHITE
                
                                ctrl_button = Button(390, y_pos, 500, 50, color, BLACK, button_text, 32)
                                self.screen.blit(ctrl_button.image, ctrl_button.rect)

                                if ctrl_button.is_pressed(mouse_pos, mouse_pressed) and not waiting_for_key:
                                        waiting_for_key = True
                                        action_to_rebind = action
                
                                y_pos += 70

                        for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                        pygame.quit()
                                        sys.exit()

                                if waiting_for_key:
                                        new_input = None
                                        if event.type == pygame.KEYDOWN:
                                                new_input = event.key
                                        elif event.type == pygame.MOUSEBUTTONDOWN:
                                                new_input = event.button

                                        if new_input is not None:
                                                for other_action, other_key in CONTROLS.items():
                                                        if other_key == new_input:
                                                                CONTROLS[other_action] = CONTROLS[action_to_rebind]
                        
                                                CONTROLS[action_to_rebind] = new_input
                                                waiting_for_key = False
                                                action_to_rebind = None

                        back_button = Button(20, 640, 200, 50, WHITE, BLACK, 'Back', 32)
                        if back_button.is_pressed(mouse_pos, mouse_pressed) and not waiting_for_key:
                                settings_running = False
            
                        self.screen.blit(back_button.image, back_button.rect)
                        self.clock.tick(FPS)
                        pygame.display.update()

        def draw_score(self):

                score_text = self.tracker_font.render(f"Score: {self.score}", True, (0, 0, 0))
                text_rect = score_text.get_rect()
                text_rect.topleft = (10, 10)
                self.screen.blit(score_text, text_rect)

        def draw_lives(self):
                bar_width = 200
                health_bar_height = 20
                shield_bar_height = 10
                padding = 10 

                health_x = 10
                health_y = self.screen.get_height() - health_bar_height - padding

                pygame.draw.rect(self.screen, (80, 80, 80), (health_x, health_y, bar_width, health_bar_height))
                health_fill = int((self.player.life / self.player.max_life) * bar_width)
                pygame.draw.rect(self.screen, (0, 200, 0), (health_x, health_y, health_fill, health_bar_height))
                pygame.draw.rect(self.screen, (0, 0, 0), (health_x, health_y, bar_width, health_bar_height), 2)

                life_text = self.life_font.render(f" {self.player.life}", True, (0, 0, 0))
                text_rect = life_text.get_rect()
                text_rect.bottomleft = (health_x + 205, health_y + 22)  
                self.screen.blit(life_text, text_rect)

                shield_x = 10
                shield_y = health_y - shield_bar_height - padding  

                pygame.draw.rect(self.screen, (80, 80, 80), (shield_x, shield_y, bar_width, shield_bar_height))
                shield_fill = int((self.player.shield / self.player.max_shield) * bar_width)
                pygame.draw.rect(self.screen, (0, 0, 255), (shield_x, shield_y, shield_fill, shield_bar_height))
                pygame.draw.rect(self.screen, (0, 0, 0), (shield_x, shield_y, bar_width, shield_bar_height), 2)

                shield_text = self.life_font.render(f" {self.player.shield}", True, (0, 0, 0))
                text_rect = life_text.get_rect()
                text_rect.bottomleft = (shield_x + 205, shield_y + 15)  
                self.screen.blit(shield_text, text_rect)


        def draw_ammo(self):

                ammo_text = self.tracker_font.render(f"Ammo: {self.player.ammo}/{self.player.max_ammo}", True, (0, 0, 0))
                text_rect = ammo_text.get_rect()
                text_rect.bottomright = (self.screen.get_width() - 10, WIN_HEIGHT - 10)
                self.screen.blit(ammo_text, text_rect)

        def draw_highscore(self):

                score_text = self.tracker_font.render(f"Highscore: {self.highscore}", True, (0, 0, 0))
                text_rect = score_text.get_rect()
                text_rect.topleft = (10, 50)
                self.screen.blit(score_text, text_rect)

        def draw_speedruntimer(self):

                timer_text = self.tracker_font.render(f"Time: {self.elapsed_time:.2f}s", True, (0, 0, 0))
                timer_rect = timer_text.get_rect()
                timer_rect.topright = (self.screen.get_width() - 10, 10)
                self.screen.blit(timer_text, timer_rect)

if __name__ == '__main__':
        pygame.init()
        screen = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption("1 Man vs 100 Gorillas")
        clock = pygame.time.Clock()

        g = Game()
        g.intro_screen()
        g.new()
        while g.running:
                g.main()
                if g.running:
                        g.game_over()

        pygame.quit()
        sys.exit()