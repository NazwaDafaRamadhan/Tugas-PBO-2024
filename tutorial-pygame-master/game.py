import math
import pygame
import time
import warnings
from pygame.locals import *
from random import randint
from abc import ABC, abstractmethod
from PIL import Image

warnings.filterwarnings("ignore", category=UserWarning, module="PIL.PngImagePlugin")

# Inisiasi Permainan
pygame.init()
width, height = 640, 480
screen = pygame.display.set_mode((width, height))

def load_image(path):
    try:
        with Image.open(path) as img:
            img.save(path, icc_profile=None) 
    except Exception as e:
        print(f"Error processing {path}: {e}")
    
    return pygame.image.load(path)

def load_sound(path, volume=0.05):
    sound = pygame.mixer.Sound(path)
    sound.set_volume(volume)
    return sound

class GameObject(ABC):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @abstractmethod
    def draw(self, screen):
        pass

    @abstractmethod
    def update(self):
        pass

# Player class
class Player(GameObject):
    def __init__(self, x, y, image_path):
        super().__init__(x, y)
        self.image = load_image(image_path)
        self.angle = 0

    @property
    def center(self):
        return (self.x + self.image.get_width() // 2, self.y + self.image.get_height() // 2)

    def draw(self, screen):
        rotated_image = pygame.transform.rotate(self.image, 360 - self.angle * 57.29)
        new_pos = (self.x - rotated_image.get_width() // 2, self.y - rotated_image.get_height() // 2)
        screen.blit(rotated_image, new_pos)

    def update(self, keys):
        if keys["top"]:
            self.y -= 5
        if keys["bottom"]:
            self.y += 5
        if keys["left"]:
            self.x -= 5
        if keys["right"]:
            self.x += 5

    def aim(self, mouse_position):
        center_x, center_y = self.center  
        self.angle = math.atan2(mouse_position[1] - center_y, mouse_position[0] - center_x)

    def get_firing_position(self):
        center_x, center_y = self.center  
        offset_x = math.cos(self.angle) * 32
        offset_y = math.sin(self.angle) * 32
        return (center_x + offset_x, center_y + offset_y)

# Kelas Arrow
class Arrow(GameObject):
    def __init__(self, angle, x, y, image_path):
        super().__init__(x, y)
        self.angle = angle
        self.image = load_image(image_path)

    def draw(self, screen):
        rotated_arrow = pygame.transform.rotate(self.image, 360 - self.angle * 57.29)
        rotated_rect = rotated_arrow.get_rect(center=(self.x, self.y))  # Keep the rotation centered
        screen.blit(rotated_arrow, rotated_rect.topleft)

    def update(self):
        self.x += math.cos(self.angle) * 10
        self.y += math.sin(self.angle) * 10

    def off_screen(self, width, height):
        return self.x < -64 or self.x > width or self.y < -64 or self.y > height

# Kelas Enemy
class Enemy(GameObject):
    def __init__(self, x, y, image_path):
        super().__init__(x, y)
        self.image = load_image(image_path)

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def update(self):
        self.x -= 5

# Kelas Game
class Game:
    def __init__(self):
        self.running = True
        self.game_over = False
        self.keys = {"top": False, "bottom": False, "left": False, "right": False}
        self.player = Player(100, 100, "resources/images/dude.png")
        self.arrows = []
        self.enemies = []
        # self.objects = self.arrows + self.enemies
        self.enemy_timer = 100
        self.health_point = 194
        self.score = 0
        self.countdown_timer = 90000

        self.result_display_time = None

        # Memuat Asset
        self.grass = load_image("resources/images/grass.png")
        self.castle = load_image("resources/images/castle.png")
        self.arrow_img = "resources/images/bullet.png"
        self.enemy_img = "resources/images/badguy.png"
        self.healthbar = load_image("resources/images/healthbar.png")
        self.health = load_image("resources/images/health.png")
        self.gameover = load_image("resources/images/gameover.png")
        self.youwin = load_image("resources/images/youwin.png")
        self.hit_sound = load_sound("resources/audio/explode.wav")
        self.enemy_hit_sound = load_sound("resources/audio/enemy.wav")
        self.shoot_sound = load_sound("resources/audio/shoot.wav")
        
        pygame.mixer.music.load("resources/audio/moonlight.wav")
        pygame.mixer.music.play(-1, 0.0)
        pygame.mixer.music.set_volume(0.25)

    def run(self):
        while self.running:
            if self.game_over:
                self.show_game_over_screen()
                pygame.display.flip()
                time.sleep(3)
                pygame.quit()
                exit(0)
            
            self.process_events()
            self.update_game_objects()
            self.draw_objects()
            pygame.display.flip()

    def show_game_over_screen(self):

        if self.health_point > 0 and not hasattr(self, "final_score_calculated"):
            self.score += self.health_point 
            self.final_score_calculated = True 

        if self.health_point <= 0:
            screen.blit(self.gameover, (width // 2 - self.gameover.get_width() // 2, height // 2 - self.gameover.get_height() // 2))
        else:
            screen.blit(self.youwin, (width // 2 - self.youwin.get_width() // 2, height // 2 - self.youwin.get_height() // 2))

        font = pygame.font.Font(None, 36) 
        score_text = f"Final Score: {self.score}"
        score_surface = font.render(score_text, True, (255, 255, 255))
        score_rect = score_surface.get_rect()
        score_rect.center = (width // 2, height // 2 + 40)
        screen.blit(score_surface, score_rect)

        if self.result_display_time and pygame.time.get_ticks() - self.result_display_time >= 3000:
            self.running = False

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                exit(0)
            if event.type == pygame.MOUSEBUTTONDOWN:
                firing_pos = self.player.get_firing_position()  # Get the firing position
                self.arrows.append(Arrow(self.player.angle, firing_pos[0], firing_pos[1], self.arrow_img))
                self.shoot_sound.play()
            if event.type == pygame.KEYDOWN:
                if event.key == K_w:
                    self.keys["top"] = True
                elif event.key == K_a:
                    self.keys["left"] = True
                elif event.key == K_s:
                    self.keys["bottom"] = True
                elif event.key == K_d:
                    self.keys["right"] = True
            if event.type == pygame.KEYUP:
                if event.key == K_w:
                    self.keys["top"] = False
                elif event.key == K_a:
                    self.keys["left"] = False
                elif event.key == K_s:
                    self.keys["bottom"] = False
                elif event.key == K_d:
                    self.keys["right"] = False

    def update_game_objects(self):
        self.player.update(self.keys)
        self.player.aim(pygame.mouse.get_pos())

        arrows_to_remove = []

        for i in range(len(self.arrows) - 1, -1, -1):
            arrow = self.arrows[i]
            arrow.update()
            if arrow.off_screen(width, height):
                arrows_to_remove.append(arrow)

        for arrow in arrows_to_remove:
            if arrow in self.arrows:
                self.arrows.remove(arrow)

        self.enemy_timer -= 1
        if self.enemy_timer == 0:
            self.enemies.append(Enemy(width, randint(50, height - 32), self.enemy_img))
            self.enemy_timer = randint(1, 100)

        enemies_to_remove = []
        for i in range(len(self.enemies) - 1, -1, -1):
            enemy = self.enemies[i]
            enemy.update()
            if enemy.x < -64:
                enemies_to_remove.append(enemy)
                self.health_point -= randint(5, 20)
                self.hit_sound.play()

            for arrow in self.arrows[:]:
                if pygame.Rect(enemy.x, enemy.y, 32, 32).colliderect(pygame.Rect(arrow.x, arrow.y, 16, 16)):
                    if enemy not in enemies_to_remove:
                        enemies_to_remove.append(enemy)
                    if arrow not in arrows_to_remove:
                        arrows_to_remove.append(arrow)
                    self.score += 1
                    self.enemy_hit_sound.play()

        for enemy in enemies_to_remove:
            if enemy in self.enemies:
                self.enemies.remove(enemy)
        for arrow in arrows_to_remove:
            if arrow in self.arrows:
                self.arrows.remove(arrow)

        if pygame.time.get_ticks() > self.countdown_timer:
            self.game_over = True
            self.result_display_time = pygame.time.get_ticks()

        if self.health_point <= 0:
            self.game_over = True
            self.result_display_time = pygame.time.get_ticks()

    def draw_objects(self):
        if self.game_over:
            if self.health_point > 0:
                screen.blit(self.youwin, (width // 2 - self.youwin.get_width() // 2, height // 2 - self.youwin.get_height() // 2))
            else:
                screen.blit(self.gameover, (width // 2 - self.gameover.get_width() // 2, height // 2 - self.gameover.get_height() // 2))

            if self.result_display_time and pygame.time.get_ticks() - self.result_display_time >= 3000:
                self.running = False 

        else:
            screen.fill(0)
            for x in range(int(width / self.grass.get_width()) + 1):
                for y in range(int(height / self.grass.get_height()) + 1):
                    screen.blit(self.grass, (x * 100, y * 100))

            for i in range(4):
                screen.blit(self.castle, (0, 30 + i * 105))

            self.player.draw(screen)

            # for obj in self.objects:
            #     obj.draw(screen)

            for arrow in self.arrows:
                arrow.draw(screen)

            for enemy in self.enemies:
                enemy.draw(screen)

            screen.blit(self.healthbar, (5, 5))
            for hp in range(self.health_point):
                screen.blit(self.health, (hp + 8, 8))

            font = pygame.font.Font(None, 24)
            minutes = int((self.countdown_timer - pygame.time.get_ticks()) / 60000)
            seconds = int((self.countdown_timer - pygame.time.get_ticks()) / 1000 % 60)
            time_text = "{:02}:{:02}".format(minutes, seconds)
            clock = font.render(time_text, True, (255, 255, 255))
            text_rect = clock.get_rect()
            text_rect.topright = [635, 5]
            screen.blit(clock, text_rect)

            # # Render and display the score below the timer (smaller font size)
            # score_font = pygame.font.Font(None, 40)  # Smaller font size
            # score_text = f"Score: {self.score}"  # Display score text
            # score_surface = score_font.render(score_text, True, (255, 255, 255))  # Render the score with white color
            # score_rect = score_surface.get_rect()
            # score_rect.topright = (635, 5)  # Position the score below the timer (adjust the Y position as needed)
            # screen.blit(score_surface, score_rect)

# Main entry point
game = Game()
game.run()
