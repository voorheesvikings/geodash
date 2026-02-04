import pygame

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1920, 1080), pygame.RESIZABLE)
clock = pygame.time.Clock()
pygame.display.set_caption("Geo Dash")
running = True

# Load the full-size background once
bg = pygame.image.load("images/stereomadness_bg.jpeg").convert()

# Prepare a scaled background for the current window size
current_bg = pygame.transform.smoothscale(bg, screen.get_size())

while running:
    # handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            # recreate the display surface at the new size and update the scaled background
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            current_bg = pygame.transform.smoothscale(bg, (event.w, event.h))

    # draw the (already-scaled) background to fill the window each frame
    screen.blit(current_bg, (0, 0))

    # RENDER YOUR GAME HERE

    # update the display
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()