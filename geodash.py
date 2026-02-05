import pygame

# pygame setup

running = True

class Game:
    def __init__(self):
        pygame.init()


        self.screen = pygame.display.set_mode((1920, 1080), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.bg = pygame.image.load("images/stereomadness_bg.jpeg").convert()
        current_bg = pygame.transform.smoothscale(self.bg, self.screen.get_size())
        pygame.display.set_caption("Geo Dash")

    def run(self):
        running = True
        while running:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    current_bg = pygame.transform.smoothscale(self.bg, (event.w, event.h))

            self.screen.blit(current_bg, (0, 0))
            self.clock.tick(60)
            pygame.display.flip()

        pygame.quit()

