import pygame
from .paddle import Paddle
from .ball import Ball

pygame.mixer.init()
paddle_sound = pygame.mixer.Sound("sounds/paddle_hit.wav")
wall_sound = pygame.mixer.Sound("sounds/wall_bounce.wav")
score_sound = pygame.mixer.Sound("sounds/score.wav")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.paddle_width = 10
        self.paddle_height = 100

        self.player = Paddle(10, height // 2 - 50, self.paddle_width, self.paddle_height)
        self.ai = Paddle(width - 20, height // 2 - 50, self.paddle_width, self.paddle_height)
        self.ball = Ball(width // 2, height // 2, 7, 7, width, height,paddle_sound,wall_sound,score_sound)

        self.player_score = 0
        self.ai_score = 0
        self.font = pygame.font.SysFont("Arial", 30)
        self.winning_score = 5  # default target (best of 9 -> first to 5)

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.player.move(-10, self.height)
        if keys[pygame.K_s]:
            self.player.move(10, self.height)

    def update(self, SCREEN):
        # Move ball
        self.ball.move()

        # --- Collision check with paddles ---
        if self.ball.rect().colliderect(self.player.rect()):
            self.ball.x = self.player.x + self.player.width
            self.ball.velocity_x *= -1
        elif self.ball.rect().colliderect(self.ai.rect()):
            self.ball.x = self.ai.x - self.ball.width
            self.ball.velocity_x *= -1
        # ------------------------------------

        # --- Scoring check ---
        if self.ball.x <= 0:
            self.ai_score += 1
            self.ball.reset()
        elif self.ball.x >= self.width:
            self.player_score += 1
            self.ball.reset()
        # ---------------------

        # Move AI paddle
        self.ai.auto_track(self.ball, self.height)

        # Check for game over
        self.check_game_over(SCREEN)

    def render(self, SCREEN):
        SCREEN.fill(BLACK)

        # Draw paddles and ball
        pygame.draw.rect(SCREEN, WHITE, self.player.rect())
        pygame.draw.rect(SCREEN, WHITE, self.ai.rect())
        pygame.draw.ellipse(SCREEN, WHITE, self.ball.rect())
        pygame.draw.aaline(SCREEN, WHITE, (self.width // 2, 0), (self.width // 2, self.height))

        # Draw scores
        player_text = self.font.render(str(self.player_score), True, WHITE)
        ai_text = self.font.render(str(self.ai_score), True, WHITE)
        SCREEN.blit(player_text, (self.width // 4, 20))
        SCREEN.blit(ai_text, (self.width * 3 // 4, 20))

    def check_game_over(self, SCREEN):
        if self.player_score >= self.winning_score or self.ai_score >= self.winning_score:
            winner_text = "Player Wins!" if self.player_score >= self.winning_score else "AI Wins!"
            message = self.font.render(winner_text, True, WHITE)

            SCREEN.fill(BLACK)
            SCREEN.blit(
                message,
                (
                    self.width // 2 - message.get_width() // 2,
                    self.height // 2 - 100,
                ),
            )

            # --- Show replay options ---
            options = [
                "Press 3 for Best of 3",
                "Press 5 for Best of 5",
                "Press 7 for Best of 7",
                "Press ESC to Exit",
            ]
            for i, text in enumerate(options):
                opt_surface = self.font.render(text, True, WHITE)
                SCREEN.blit(opt_surface, (self.width // 2 - opt_surface.get_width() // 2,
                                          self.height // 2 + i * 40))
            # ----------------------------

            pygame.display.flip()

            self.handle_replay(SCREEN)

    def handle_replay(self, SCREEN):
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        quit()
                    elif event.key == pygame.K_3:
                        self.winning_score = 2  # Best of 3 → first to 2
                        waiting = False
                    elif event.key == pygame.K_5:
                        self.winning_score = 3  # Best of 5 → first to 3
                        waiting = False
                    elif event.key == pygame.K_7:
                        self.winning_score = 4  # Best of 7 → first to 4
                        waiting = False

            pygame.time.wait(100)

        # Reset game state
        self.player_score = 0
        self.ai_score = 0
        self.ball.reset()
        SCREEN.fill(BLACK)
        pygame.display.flip()
