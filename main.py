import pygame
import pygame.locals
import my_globals as g
import world
import battle
import utility

class Control(object):
    def __init__(self):
        self.GAME_STATE = g.GameState.MAP ##THIS SHOULD REALLY START AS INIT
        
        self.VIEW_SURF = pygame.Surface((g.VIEW_WIDTH, g.VIEW_HEIGHT))
        self.VIEW_RECT = self.VIEW_SURF.get_rect()
        self.SCREEN = pygame.display.set_mode((g.WIN_WIDTH, g.WIN_HEIGHT))
        self.CLOCK = pygame.time.Clock()
        self.CURRENT_STATE = None
        self.SPRITE_CACHE = utility.TileCache(g.TILE_SIZE)

        self.KEYS = pygame.key.get_pressed()

        self.TEXT_MANAGER = utility.TextManager(self.VIEW_SURF)

        self.BATTLE = None
        self.MENU = None
        
        self.LEVEL = world.Level(self.VIEW_RECT.copy(), self)
        self.LEVEL.load_file("lvl/level.map")
        self.LEVEL.add_entity(world.Player("player", self.LEVEL, (1,0), self.SPRITE_CACHE['spr/red.png'], True))

        self.skipRender = False
    
    def event_loop(self):
        for event in pygame.event.get():
            self.KEYS = pygame.key.get_pressed()
            if event.type == pygame.QUIT or self.KEYS[pygame.K_ESCAPE]:
                self.CURRENT_STATE = -1

    def display_fps(self):
        caption = "{} - FPS: {:.2f}".format(g.CAPTION, self.CLOCK.get_fps())
        pygame.display.set_caption(caption)

    def update(self):
        if self.GAME_STATE == g.GameState.MAP:
            if not self.TEXT_MANAGER.isTyping:
                self.LEVEL.update(self.CLOCK.get_time(), self.KEYS)
                self.LEVEL.draw(self.VIEW_SURF)
            else:
                self.TEXT_MANAGER.type_text(self.KEYS)
        elif (self.GAME_STATE == g.GameState.BATTLE):
            if (self.BATTLE.BATTLE_STATE != battle.BattleState.WIN and
                self.BATTLE.BATTLE_STATE != battle.BattleState.LOSE):
                self.BATTLE.update()
            else:
                self.GAME_STATE = g.GameState.MAP
                del self.BATTLE
        
        if not self.skipRender:
            self.window_render()
        else:
            self.skipRender = False

    def window_render(self):
        pygame.transform.scale(self.VIEW_SURF, (g.WIN_WIDTH, g.WIN_HEIGHT), self.SCREEN)
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
