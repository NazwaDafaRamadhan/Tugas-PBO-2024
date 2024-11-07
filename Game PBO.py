import pygame
import sys
import random
import time

# init pygame
pygame.init()

# class game object
class GameObject :
    def __init__(self, color, position):
        self.color = color
        self.position = position

    def draw(self, game_window):
        pygame.draw.rect(game_window, self.color, pygame.Rect(self.position[0], self.position[1], 10, 10))

# class snake 
class Snake(GameObject):
    def __init__(self, position):
        super().__init__(pygame.Color(0, 255, 0), position)
        self.body = [list(position), [position[0] - 10, position[1]], [position[0] - 20, position[1]]]
        self.direction = 'Right'
        self.change_to = self.direction

    def change_direction(self, direction):
        if direction == 'Up' and self.direction != 'Down':
            self.change_to = 'Up'
        elif direction == 'Down' and self.direction != 'Up':
            self.change_to = 'Down'
        if direction =='Right' and self.direction !='Left':
            self.change_to = 'Right'
        elif direction == 'Left' and self.direction != 'Right':
            self.change_to = 'Left'

    def move(self):
        self.direction = self.change_to
        
        if self.direction == 'Up':
            self.position[1] -= 10
        elif self.direction == 'Down':
            self.position[1] += 10
        elif self.direction == 'Left':
            self.position[0] -= 10
        elif self.direction == 'Right':
            self.position[0] += 10
        
        self.body.insert(0, list(self.position))

    def shrink(self):
        self.body.pop()

    def draw(self, game_window):
        for pos in self.body:
            pygame.draw.rect(game_window, self.color, pygame.Rect(pos[0], pos[1], 10, 10))

    def check_collision(self, frame_size_x, frame_size_y):
        
        # Wall Check 
        if self.position[0] < 0 or self.position[0] > frame_size_x - 10 or self.position[1] < 0 or self.position[1] >frame_size_y - 10:
            return True
        
        # Body Check
        for block in self.body[1:]:
            if self.position[0] == block[0] and self.position[1] == block[1]:
                return True
            
        return False
    
class Apple(GameObject):
    def __init__(self, frame_size_x, frame_size_y, color):
        position = [random.randrange(1, (frame_size_x // 10)) * 10, random.randrange(1, (frame_size_y // 10)) * 10]
        super().__init__(color, position)

    def respawn(self, frame_size_x, frame_size_y):
        self.position = [random.randrange(1, (frame_size_x // 10)) * 10, random.randrange(1, (frame_size_y // 10)) * 10]

class Game(GameObject):
    def __init__(self):
        self.frame_size_x = 800
        self.frame_size_y = 600
        self.clock = pygame.time.Clock()
        self.game_window = pygame.display.set_mode((self.frame_size_x, self.frame_size_y)) 
        pygame.display.set_caption('Snake Game')
        self.fps_controller = pygame.time.Clock()
        self.snake = Snake([100, 50])
        # self.apple = Apple(self.frame_size_x, self.frame_size_y)
        self.apple = [Apple(self.frame_size_x, self.frame_size_y, pygame.Color(255, 0, 0)), Apple(self.frame_size_x, self.frame_size_y, pygame.Color(0, 0, 255))]
        self.score = 0
        
    def game_over(self):
        my_font = pygame.font.SysFont('Arial', 90)
        game_over_surface = my_font.render('YOU DIED', True, pygame.Color(255, 0, 0))
        game_over_rect = game_over_surface.get_rect()
        game_over_rect.midtop = (self.frame_size_x / 2, self.frame_size_y / 4)
        self.game_window.fill(pygame.Color(0, 0, 0))
        self.game_window.blit(game_over_surface, game_over_rect)
        pygame.display.flip()
        time.sleep(3)
        pygame.quit()
        sys.exit()

    def show_score(self):
        score_font = pygame.font.SysFont('Arial', 20)
        score_surface = score_font.render('Score : ' + str(self.score), True, pygame.Color(0, 0, 0))
        score_rect = score_surface.get_rect()
        score_rect.midtop = (72, 15)
        self.game_window.blit(score_surface, score_rect)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.snake.change_direction('Up')
                    elif event.key == pygame.K_DOWN:
                        self.snake.change_direction('Down')
                    elif event.key == pygame.K_LEFT:
                        self.snake.change_direction('Left')
                    elif event.key == pygame.K_RIGHT:
                        self.snake.change_direction('Right')
                    elif event.key == pygame.K_ESCAPE:
                        pygame.event.post(pygame.event.Event(pygame.QUIT))

            self.snake.move()

            apple_eaten = False

            # if self.snake.position == self.apple.position:
            #     self.score += 1
            #     self.apple.respawn(self.frame_size_x, self.frame_size_y)
            # else:
            #     self.snake.shrink()
            
            for apple in self.apple:
                if self.snake.position == apple.position:
                    self.score += 1
                    apple.respawn(self.frame_size_x, self.frame_size_y)
                    apple_eaten = True
                
            if not apple_eaten:
                self.snake.shrink()

            self.game_window.fill(pygame.Color(255, 255, 255))

            self.snake.draw(self.game_window)
            # self.apple.draw(self.game_window)

            for apple in self.apple:
                apple.draw(self.game_window)
                
            self.show_score()

            if self.snake.check_collision(self.frame_size_x, self.frame_size_y):
                self.game_over()

            pygame.display.update()
            self.fps_controller.tick(10)

# Menjalankan Kode Program
if __name__ == "__main__":
    game = Game()
    game.run()