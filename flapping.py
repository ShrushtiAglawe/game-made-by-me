# flappy.py
# Simple Flappy Bird clone using pygame. No external images required.

import pygame
import sys
import random

# -------- Configuration --------
WIDTH, HEIGHT = 400, 600
FPS = 60
GRAVITY = 0.45
FLAP_STRENGTH = -8.5
PIPE_SPEED = 3
PIPE_GAP = 150
PIPE_WIDTH = 70
PIPE_INTERVAL = 1500  # milliseconds between pipes
BIRD_RADIUS = 15

# Colors
WHITE = (255, 255, 255)
BG_COLOR = (135, 206, 235)  # sky
BIRD_COLOR = (255, 200, 0)  # yellow
PIPE_COLOR = (34, 139, 34)  # green
GROUND_COLOR = (200, 180, 120)
TEXT_COLOR = (20, 20, 20)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird - Simple Clone")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

# -------- Game objects and helpers --------
class Bird:
    def __init__(self):
        self.x = WIDTH // 4
        self.y = HEIGHT // 2
        self.vel = 0.0
        self.radius = BIRD_RADIUS
        self.alive = True

    def flap(self):
        self.vel = FLAP_STRENGTH

    def update(self):
        self.vel += GRAVITY
        self.y += self.vel

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius,
                           self.radius * 2, self.radius * 2)

    def draw(self, surf):
        pygame.draw.circle(surf, BIRD_COLOR, (int(self.x), int(self.y)), self.radius)
        # small wing (visual)
        pygame.draw.polygon(surf, (255,170,0), [(self.x, self.y), (self.x - 15, self.y + 5), (self.x - 6, self.y + 13)])

class Pipe:
    def __init__(self, x):
        self.x = x
        center = random.randint(PIPE_GAP//2 + 40, HEIGHT - 120 - PIPE_GAP//2)
        self.top = center - PIPE_GAP//2
        self.bottom = center + PIPE_GAP//2
        self.passed = False

    def update(self):
        self.x -= PIPE_SPEED

    def offscreen(self):
        return self.x + PIPE_WIDTH < 0

    def collides_with(self, bird_rect):
        # top rect
        top_rect = pygame.Rect(self.x, 0, PIPE_WIDTH, self.top)
        bottom_rect = pygame.Rect(self.x, self.bottom, PIPE_WIDTH, HEIGHT - self.bottom)
        return bird_rect.colliderect(top_rect) or bird_rect.colliderect(bottom_rect)

    def draw(self, surf):
        pygame.draw.rect(surf, PIPE_COLOR, (self.x, 0, PIPE_WIDTH, self.top))
        pygame.draw.rect(surf, PIPE_COLOR, (self.x, self.bottom, PIPE_WIDTH, HEIGHT - self.bottom))
        # pipe cap (a little decoration)
        pygame.draw.rect(surf, (20,100,20), (self.x-3, self.top-8, PIPE_WIDTH+6, 8))
        pygame.draw.rect(surf, (20,100,20), (self.x-3, self.bottom, PIPE_WIDTH+6, 8))

# -------- Game functions --------
def draw_background(surf):
    surf.fill(BG_COLOR)
    # ground
    pygame.draw.rect(surf, GROUND_COLOR, (0, HEIGHT - 40, WIDTH, 40))

def draw_text_center(surf, text, y):
    img = font.render(text, True, TEXT_COLOR)
    rect = img.get_rect(center=(WIDTH//2, y))
    surf.blit(img, rect)

def main():
    bird = Bird()
    pipes = []
    score = 0
    last_pipe_time = pygame.time.get_ticks()
    running = True
    game_over = False

    while running:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_over:
                    bird.flap()
                if event.key == pygame.K_SPACE and game_over:
                    # restart
                    bird = Bird()
                    pipes = []
                    score = 0
                    last_pipe_time = pygame.time.get_ticks()
                    game_over = False
                if event.key == pygame.K_ESCAPE:
                    running = False
                    break
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not game_over:
                    bird.flap()
                else:
                    # restart on mouse click
                    bird = Bird()
                    pipes = []
                    score = 0
                    last_pipe_time = pygame.time.get_ticks()
                    game_over = False

        if not running:
            break

        # spawn pipes
        now = pygame.time.get_ticks()
        if not game_over and now - last_pipe_time > PIPE_INTERVAL:
            pipes.append(Pipe(WIDTH + 10))
            last_pipe_time = now

        if not game_over:
            bird.update()

            # update pipes
            for p in pipes:
                p.update()

            # remove offscreen pipes
            pipes = [p for p in pipes if not p.offscreen()]

            # collision detection
            bird_rect = bird.get_rect()
            if bird.y + bird.radius >= HEIGHT - 40:
                game_over = True
                bird.alive = False
            if bird.y - bird.radius <= 0:
                bird.y = bird.radius
                bird.vel = 0

            for p in pipes:
                if p.collides_with(bird_rect):
                    game_over = True
                    bird.alive = False
                # scoring: when bird passes pipe
                if not p.passed and p.x + PIPE_WIDTH < bird.x:
                    p.passed = True
                    score += 1

        # draw
        draw_background(screen)
        for p in pipes:
            p.draw(screen)
        bird.draw(screen)
        draw_text_center(screen, f"Score: {score}", 30)

        if game_over:
            draw_text_center(screen, "Game Over", HEIGHT//2 - 20)
            draw_text_center(screen, "Press SPACE or click to restart", HEIGHT//2 + 20)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
