import pygame

class Game:
    def __init__(self):
        pygame.init()

        # --- Window Setup ---
        self.screen = pygame.display.set_mode((1920, 1080), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("Geo Dash")

        # --- Background Setup ---
        self.bg = pygame.image.load("images/stereomadness_bg.jpeg").convert()
        self.current_bg = pygame.transform.smoothscale(self.bg, self.screen.get_size())

        # --- Player Setup ---
        self.player = Player()
        self.player_group = pygame.sprite.GroupSingle()
        self.player_group.add(self.player)

        # --- Obstacle Setup ---
        self.obstacle_group = pygame.sprite.Group()
        self.obstacle_timer = pygame.USEREVENT + 1
        pygame.time.set_timer(self.obstacle_timer, 1500) 
        
        # Pattern: Spike, Spike, Block, Block, Block
        self.spawn_pattern = [0, 0, 1, 1, 1] 
        self.pattern_index = 0

    def run(self):
        running = True
        while running:
            # --- 1. Event Handling ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    self.current_bg = pygame.transform.smoothscale(self.bg, (event.w, event.h))
                
                elif event.type == self.obstacle_timer:
                    obstacle_type = self.spawn_pattern[self.pattern_index]
                    
                    if obstacle_type == 0:
                        obs = Obstacle1(2000, 700)
                    else:
                        obs = Block(2000, 700) 
                    
                    self.obstacle_group.add(obs)
                    self.pattern_index = (self.pattern_index + 1) % len(self.spawn_pattern)

            # --- 2. Update Positions ---
            self.obstacle_group.update() 
            self.player_group.update()

            # --- 3. Collision Logic ---
            # using collide_mask for precision
            collisions = pygame.sprite.spritecollide(self.player, self.obstacle_group, False, pygame.sprite.collide_mask)
            
            if collisions:
                for obstacle in collisions:
                    # CASE A: Spike -> Dead
                    if obstacle.type == 'spike':
                        self.reset_game()
                    
                    # CASE B: Block -> Check physics
                    elif obstacle.type == 'block':
                        # PLATFORM LOGIC FIX:
                        # If player is falling (gravity > 0) 
                        # AND the player's feet are higher than the MIDDLE of the block (centery)
                        # We assume this is a landing, not a crash.
                        if self.player.gravity > 0 and self.player.rect.bottom < obstacle.rect.centery:
                            # Land on top
                            self.player.rect.bottom = obstacle.rect.top
                            self.player.gravity = 0
                        else:
                            # Hit side/bottom -> Dead
                            self.reset_game()

            # --- 4. Draw ---
            self.screen.blit(self.current_bg, (0, 0))
            self.player_group.draw(self.screen)
            self.obstacle_group.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

    def reset_game(self):
        self.obstacle_group.empty() 
        self.player.rect.center = (600, 740) 
        self.player.gravity = 0
        self.pattern_index = 0

# --- HELPER FUNCTION (Only used for blocks now) ---
def get_trimmed_image(surface):
    """Removes transparent edges from an image so the hitbox fits perfectly."""
    rect = surface.get_bounding_rect() 
    return surface.subsurface(rect).copy() 

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # NORMAL LOADING (No trimming)
        self.image = pygame.image.load("images/cube1.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (90, 90))
        self.rect = self.image.get_rect()
        self.rect.center = (600, 740)
        
        # We still need a mask for collision to work with the blocks
        self.mask = pygame.mask.from_surface(self.image)
        
        self.gravity = 0
        self.jump_strength = -22 
        self.floor_y = 785 

    def player_input(self):
        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pressed()
        
        if (keys[pygame.K_SPACE] or mouse[0]):
            if self.rect.bottom >= self.floor_y or self.gravity == 0:
                self.gravity = self.jump_strength

    def apply_gravity(self):
        self.gravity += 1 
        self.rect.y += self.gravity
        
        if self.rect.bottom >= self.floor_y:
            self.rect.bottom = self.floor_y
            self.gravity = 0 

    def update(self):
        self.player_input()
        self.apply_gravity()

class Obstacle1(pygame.sprite.Sprite):
    def __init__(self, x_pos, y_pos):
        super().__init__()
        # NORMAL LOADING (No trimming)
        self.image = pygame.image.load("images/spike.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (100, 100))
        self.rect = self.image.get_rect()
        self.rect.x = x_pos
        self.rect.y = y_pos
        self.type = "spike"
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.x -= 10
        if self.rect.right < 0:
            self.kill()

class Block(pygame.sprite.Sprite):
    def __init__(self, x_pos, y_pos):
        super().__init__()
        raw_image = pygame.image.load("images/block.png").convert_alpha()
        
        # 1. Scale Bigger (as you requested)
        scaled_image = pygame.transform.scale(raw_image, (120, 120))
        
        # 2. Trim ONLY the Block (as requested)
        self.image = get_trimmed_image(scaled_image)
        
        self.rect = self.image.get_rect()
        self.rect.x = x_pos
        self.rect.y = y_pos
        self.type = "block"
        
        # 3. Mask for precision
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.x -= 10
        if self.rect.right < 0:
            self.kill()

if __name__ == "__main__":
    game = Game()
    game.run()