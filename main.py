import pygame
import pygame.locals
import utility
import world

CAPTION = "ugghhh"

TILE_SIZE = 16

VIEW_WIDTH = TILE_SIZE * 10 #160
VIEW_HEIGHT = TILE_SIZE * 9 #144
VIEW_SCALE = 4
WIN_WIDTH = VIEW_WIDTH * VIEW_SCALE
WIN_HEIGHT = VIEW_HEIGHT * VIEW_SCALE

KEY_CONFIRM = pygame.K_z
KEY_CANCEL = pygame.K_x
KEY_MENU = pygame.K_c

class Control(object):
    def __init__(self):
        self.VIEW_SURF = pygame.Surface((VIEW_WIDTH, VIEW_HEIGHT))
        self.VIEW_RECT = self.VIEW_SURF.get_rect()
        self.SCREEN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        self.CLOCK = pygame.time.Clock()
        self.CURRENT_STATE = None
        self.SPRITE_CACHE = utility.TileCache(TILE_SIZE)

        self.KEYS = pygame.key.get_pressed()

        self.TEXT_MANAGER = utility.TextManager(self.VIEW_SURF)
        
        self.LEVEL = world.Level(self.VIEW_RECT.copy(), self)
        self.LEVEL.load_file("lvl/level.map")
        self.LEVEL.add_entity(world.Player("player", self.LEVEL, (1,0), self.SPRITE_CACHE['spr/red.png'], True))
        #self.PLAYER = world.Player("player", self.LEVEL, (1,0), self.SPRITE_CACHE['spr/red.png'], True)
        #self.LEVEL.add_entity(world.Actor("test", (4,0), self.SPRITE_CACHE['spr/red.png'], False))

    def event_loop(self):
        for event in pygame.event.get():
            self.KEYS = pygame.key.get_pressed()
            if event.type == pygame.QUIT or self.KEYS[pygame.K_ESCAPE]:
                self.CURRENT_STATE = -1
            #elif self.KEYS[KEY_CONFIRM]:
            #    if not self.TEXT_MANAGER.isTyping:
            #        self.TEXT_MANAGER.create_text_box("VINNY: 'Hey man, how are you?' &n That sounds pretty sweet!")

    def display_fps(self):
        caption = "{} - FPS: {:.2f}".format(CAPTION, self.CLOCK.get_fps())
        pygame.display.set_caption(caption)

    def update(self):
        if not self.TEXT_MANAGER.isTyping:
            self.LEVEL.update(self.CLOCK.get_time(), self.KEYS)
            self.LEVEL.draw(self.VIEW_SURF)
        else:
            self.TEXT_MANAGER.type_text(self.KEYS)
        
        pygame.transform.scale(self.VIEW_SURF, (WIN_WIDTH, WIN_HEIGHT), self.SCREEN)
        pygame.display.flip()
            

    def main_loop(self):
        while self.CURRENT_STATE != -1: 
            self.event_loop()
            self.update()
            pygame.display.update()
            self.CLOCK.tick(30)
            self.display_fps()

def main():
    pygame.init()
    Control().main_loop()
    pygame.quit()

if __name__=='__main__':
    main()
