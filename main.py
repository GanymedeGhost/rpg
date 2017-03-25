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
        self.gameState = g.GameState.MAP

        self.viewSurf = pygame.Surface((g.VIEW_WIDTH, g.VIEW_HEIGHT))
        self.viewRect = self.viewSurf.get_rect()
        self.screen = pygame.display.set_mode((g.WIN_WIDTH, g.WIN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.loopState = None
        self.spriteCache = utility.TileCache(g.TILE_SIZE)

        self.eventKeys = pygame.key.get_pressed()

        self.TM = utility.TextManager(self.viewSurf)

        self.BC = None
        self.MC = None

        self.playTimeEvent = pygame.USEREVENT + 1
        pygame.time.set_timer(self.playTimeEvent, 1000)
        
        g.partyList.append(db.Hero.dic["Luxe"])
        g.partyList.append(db.Hero.dic["Elle"])
        g.partyList.append(db.Hero.dic["Asa"])
        
        inventory.init()
        inventory.add_item("Potion", 2)
        inventory.add_item("Revive")
        animarium.add_animagus("Signis")
        animarium.add_animagus("Zeir")
        animarium.add_animagus("Luna")
        animarium.add_animagus("Felix")

        self.curLevel = world.Level(self.viewRect.copy(), self)
        self.curLevel.load_file("lvl/level.map")
        self.curLevel.add_entity(world.Player("player", self.curLevel, (1, 0), self.spriteCache['spr/red.png'], True))

        self.skipRender = False

    def start_battle(self, monsters, initiative = -1):
        g.monsterList = []
        for key in monsters:
            g.monsterList.append(db.Monster.dic[key])
        self.BC = battle.BattleController(self, initiative)
        self.gameState = g.GameState.BATTLE

    def open_menu(self):
        self.MC = menu.MenuController(self)
        self.gameState = g.GameState.MENU

    def event_loop(self):
        for event in pygame.event.get():
            self.eventKeys = pygame.key.get_pressed()
            if event.type == pygame.QUIT or self.eventKeys[pygame.K_ESCAPE]:
                self.loopState = -1
            if event.type == self.playTimeEvent:
                utility.play_time()
                pygame.time.set_timer(self.playTimeEvent, 1000)
            ###DEBUG KEYS
            if self.eventKeys[pygame.K_1]:
                g.logFilter[g.LogLevel.DEBUG] = not g.logFilter[g.LogLevel.DEBUG]
                utility.log("Debug Log: " + str(g.logFilter[g.LogLevel.DEBUG]), g.LogLevel.SYSTEM)
            if self.eventKeys[pygame.K_2]:
                g.logFilter[g.LogLevel.ERROR] = not g.logFilter[g.LogLevel.ERROR]
                utility.log("Error Log: " + str(g.logFilter[g.LogLevel.ERROR]), g.LogLevel.SYSTEM)
            if self.eventKeys[pygame.K_3]:
                g.logFilter[g.LogLevel.FEEDBACK] = not g.logFilter[g.LogLevel.FEEDBACK]
                utility.log("Feedback Log: " + str(g.logFilter[g.LogLevel.FEEDBACK]), g.LogLevel.SYSTEM)
            if self.eventKeys[pygame.K_4]:
                inventory.sort_by(g.INVENTORY_SORT_KEY)

    def display_fps(self):
        caption = "{} - FPS: {:.2f}".format(g.CAPTION, self.clock.get_fps())
        pygame.display.set_caption(caption)

    def update(self):
        if self.gameState == g.GameState.MAP:
                if not self.TM.isTyping:
                    self.curLevel.update(self.clock.get_time(), self.eventKeys)
                    self.curLevel.draw(self.viewSurf)
                else:
                    self.TM.type_text(self.eventKeys)
        elif self.gameState == g.GameState.BATTLE:
            if self.BC.battleState != g.BattleState.EXIT:
                self.BC.update()
            else:
                g.inputTimer = g.INPUT_DELAY
                self.gameState = g.GameState.MAP
                del self.BC
                self.BC = None
        elif self.gameState == g.GameState.MENU:
            if self.MC.menuState != g.MenuState.EXIT:
                self.MC.update()
            else:
                self.gameState = g.GameState.MAP
                del self.MC
                self.MC = None
    
        if not self.skipRender:
                self.window_render()
        else:
                self.skipRender = False

    def window_render(self):
        pygame.transform.scale(self.viewSurf, (g.WIN_WIDTH, g.WIN_HEIGHT), self.screen)
        pygame.display.flip()

    def main_loop(self):
        while self.loopState != -1:
            self.event_loop()
            self.update()
            pygame.display.update()
            self.clock.tick(30)
            self.display_fps()

def main():
    Control().main_loop()
    pygame.quit()

if __name__=='__main__':
    main()
