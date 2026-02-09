import pygame


#we used oop principles in order to seperate our code
class Game:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((1920, 1080), pygame.RESIZABLE) # makes it so that you can resize the screen
    
        self.clock = pygame.time.Clock() # allows me to set it to 60 fps later
        pygame.display.set_caption("Geo Dash")

        #loading bg
        self.bg = pygame.image.load("images/stereomadness_bg.jpeg").convert()
        self.current_bg = pygame.transform.smoothscale(self.bg, self.screen.get_size()) # allows me to resize the screen easily

        #
        self.player = Player() #initialize the player class
        self.player_group = pygame.sprite.GroupSingle() #it allows gor changing the sprite instead of duplicating it each time
        self.player_group.add(self.player) #adds the sprite to the group
        self.obstacle_group = pygame.sprite.Group() #same thing as the player
        self.obstacle_timer = pygame.USEREVENT + 1
        pygame.time.set_timer(self.obstacle_timer, 1500) # how long it takes for each obstacle to fly in
        
        # pattern that we used: Spike, Spike, Block, Block, Block
        #bbasically its a loop so that the spikes will fly in and then the blocks in an loop
        self.spawn_pattern = [0, 0, 1, 1, 1] 
        self.pattern_index = 0 #starts at 0

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False #if game is closed, stop running
                elif event.type == pygame.VIDEORESIZE: # if you resize the screen, then change the bacground to fit it
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    self.current_bg = pygame.transform.smoothscale(self.bg, (event.w, event.h))
                
                elif event.type == self.obstacle_timer: # if the obstacle timer is finished, teh obstacle starts to fly in
                    obstacle_type = self.spawn_pattern[self.pattern_index]
                    
                    if obstacle_type == 0:
                        obs = Obstacle1(2000, 700) # if its a spike it spawns in on this coordinate
                    else:
                        obs = Block(2000, 700) # if its a cube it spawns in on this coordinate
                    
                    self.obstacle_group.add(obs) #adds the obstacle to the group of obstacles
                    self.pattern_index = (self.pattern_index + 1) % len(self.spawn_pattern)

            # Update funcs
            self.obstacle_group.update() 
            self.player_group.update()

            # using collide_mask for precision
            collisions = pygame.sprite.spritecollide(self.player, self.obstacle_group, False, pygame.sprite.collide_mask)
            
            if collisions:
                for obstacle in collisions:
                    # Spike == dead
                    if obstacle.type == 'spike':
                        self.reset_game()
                    
                    #block = check physics
                    elif obstacle.type == 'block':
                        # PLATFORM LOGIC FIX:
                        # If player is falling (gravity > 0) and the player's feet are higher than the middle of the bloc, We assume that is a landing, not a crash.
                        if self.player.gravity > 0 and self.player.rect.bottom < obstacle.rect.centery:
                            # Land on top
                            self.player.rect.bottom = obstacle.rect.top # we didnt know how to do this, so we made it so that it just teleports to the top
                            self.player.gravity = 0
                        else:
                            # Hit side/bottom == Dead
                            self.reset_game()

            # draw on teh screen
            self.screen.blit(self.current_bg, (0, 0)) 
            self.player_group.draw(self.screen)
            self.obstacle_group.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(60) #seet fps to 60

        pygame.quit()

    def reset_game(self):
        self.obstacle_group.empty() 
        self.player.rect.center = (600, 740)  #player spawn cords
        self.player.gravity = 0 #physics for the game
        self.pattern_index = 0 #reset


def get_trimmed_image(surface):
    # i tried to remove transparent edges from an image so the hitbox fits perfectly
    rect = surface.get_bounding_rect() 
    return surface.subsurface(rect).copy() 

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("images/cube1.png").convert_alpha() #image cube1
        self.image = pygame.transform.scale(self.image, (90, 90)) #size of object
        self.rect = self.image.get_rect()
        self.rect.center = (600, 740) #where the object spawns in
        
        # We still need a mask for collision to work with the blocks
        self.mask = pygame.mask.from_surface(self.image)
        
        self.gravity = 0
        self.jump_strength = -22 # negative in pygame is positive
        self.floor_y = 785 

    def player_input(self):
        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pressed()
        
        if (keys[pygame.K_SPACE] or mouse[0]): # if its space or mouse click, jump
            if self.rect.bottom >= self.floor_y or self.gravity == 0: #make sure they arent already jumping
                self.gravity = self.jump_strength

    def apply_gravity(self):
        self.gravity += 1  #its gotta come down
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
        super().__init__() #initialize this with the game superclass
        raw_image = pygame.image.load("images/block.png").convert_alpha()
        
        scaled_image = pygame.transform.scale(raw_image, (120, 120)) 
        #had to make the block bigger cause it looked awkwardly small
        
        self.image = get_trimmed_image(scaled_image)
        
        self.rect = self.image.get_rect()
        self.rect.x = x_pos
        self.rect.y = y_pos
        self.type = "block"
        
        # mask for precision
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.x -= 10
        if self.rect.right < 0:
            self.kill() # after it goes past the screen, it is removed too reduce lag

if __name__ == "__main__":
    game = Game()
    game.run()