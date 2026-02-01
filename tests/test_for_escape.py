import pygame
import sys

# Configuration
GRID_SIZE = 32
CELL_SIZE = 20  # Pixels per grid point
SCREEN_RES = GRID_SIZE * CELL_SIZE
FPS = 60

# Colors
COLOR_BG = (30, 30, 30)
COLOR_GRID = (50, 50, 50)
COLOR_PLAYER = (0, 255, 150)


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_RES, SCREEN_RES))
    pygame.display.set_caption("32x32 Wrap-Around Grid")
    clock = pygame.time.Clock()

    # Player starting position (grid coordinates)
    player_x = 16
    player_y = 16

    while True:
        # 1. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:  # Up
                    player_y -= 1
                elif event.key == pygame.K_s:  # Down
                    player_y += 1
                elif event.key == pygame.K_a:  # Left
                    player_x -= 1
                elif event.key == pygame.K_d:  # Right
                    player_x += 1

        # 2. Wrap-Around Logic (The Magic)
        # Using % ensures the value always stays between 0 and 31
        player_x %= GRID_SIZE
        player_y %= GRID_SIZE

        # 3. Drawing
        screen.fill(COLOR_BG)

        # Draw a subtle grid for reference
        for x in range(0, SCREEN_RES, CELL_SIZE):
            pygame.draw.line(screen, COLOR_GRID, (x, 0), (x, SCREEN_RES))
        for y in range(0, SCREEN_RES, CELL_SIZE):
            pygame.draw.line(screen, COLOR_GRID, (0, y), (SCREEN_RES, y))

        # Draw the player
        player_rect = pygame.Rect(
            player_x * CELL_SIZE,
            player_y * CELL_SIZE,
            CELL_SIZE,
            CELL_SIZE
        )
        pygame.draw.rect(screen, COLOR_PLAYER, player_rect)
        pygame.draw.circle(screen, 'red',(SCREEN_RES // 2, SCREEN_RES//2), CELL_SIZE)

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()