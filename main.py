import pygame
import pygame.locals

import my_globals as g
import database as db
import world
import battle
import menu
import inventory
import animarium
import utility

class Control(object):
    def __init__(self):
        ##THIS SHOULD REALLY START AS INIT
        self.GAME_STATE = g.GameState.MAP

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

        self.playTimeEvent = pygame.USEREVENT + 1
        pygame.time.set_timer(self.playTimeEvent, 1000)
        
        g.PARTY_LIST.append(db.Hero.dic["Luxe"])
        g.PARTY_LIST.append(db.Hero.dic["Elle"])
        g.PARTY_LIST.append(db.Hero.dic["Asa"])
        
        inventory.init()
        inventory.add_item("Potion", 2)
        inventory.add_item("Revive")
        animarium.add_animagus("Signis")
        animarium.add_animagus("Zeir")
        animarium.add_animagus("Luna")
        animarium.add_animagus("Felix")

        self.LEVEL = world.Level(self.VIEW_RECT.copy(), self)
        self.LEVEL.load_file("lvl/level.map")
        self.LEVEL.add_entity(world.Player("player", self.LEVEL, (1,0), self.SPRITE_CACHE['spr/red.png'], True))

        self.skipRender = False

    def start_battle(self, monsters, initiative = -1):
        g.MONSTER_LIST = []
        for key in monsters:
            g.MONSTER_LIST.append(db.Monster.dic[key])
        self.BATTLE = battle.BattleController(self, initiative)
        self.GAME_STATE = g.GameState.BATTLE

    def open_menu(self):
        self.MENU = menu.MenuController(self)
        self.GAME_STATE = g.GameState.MENU

    def event_loop(self):
        for event in pygame.event.get():
            self.KEYS = pygame.key.get_pressed()
            if event.type == pygame.QUIT or self.KEYS[pygame.K_ESCAPE]:
                self.CURRENT_STATE = -1
            if event.type == self.playTimeEvent:
                utility.play_time()
                pygame.time.set_timer(self.playTimeEvent, 1000)
            ###DEBUG KEYS
            if self.KEYS[pygame.K_1]:
                g.LOG_FILTER[g.LogLevel.DEBUG] = not g.LOG_FILTER[g.LogLevel.DEBUG]
                utility.log("Debug Log: " + str(g.LOG_FILTER[g.LogLevel.DEBUG]), g.LogLevel.SYSTEM)
            if self.KEYS[pygame.K_2]:
                g.LOG_FILTER[g.LogLevel.ERROR] = not g.LOG_FILTER[g.LogLevel.ERROR]
                utility.log("Error Log: " + str(g.LOG_FILTER[g.LogLevel.ERROR]), g.LogLevel.SYSTEM)
            if self.KEYS[pygame.K_3]:
                g.LOG_FILTER[g.LogLevel.FEEDBACK] = not g.LOG_FILTER[g.LogLevel.FEEDBACK]
                utility.log("Feedback Log: " + str(g.LOG_FILTER[g.LogLevel.FEEDBACK]), g.LogLevel.SYSTEM)
            if self.KEYS[pygame.K_4]:
                inventory.sort_by(g.INVENTORY_SORT_KEY)

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
        elif self.GAME_STATE == g.GameState.BATTLE:
            if self.BATTLE.BATTLE_STATE != g.BattleState.EXIT:
                self.BATTLE.update()
            else:
                g.INPUT_TIMER = g.INPUT_DELAY
                self.GAME_STATE = g.GameState.MAP
                del self.BATTLE
                self.BATTLE = None
        elif self.GAME_STATE == g.GameState.MENU:
            if self.MENU.menuState != g.MenuState.EXIT:
                self.MENU.update()
            else:
                self.GAME_STATE = g.GameState.MAP
                del self.MENU
                self.MENU = None
    
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
    Control().main_loop()
    pygame.quit()

if __name__=='__main__':
    main()
