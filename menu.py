import pygame
import pygame.locals
import my_globals as g
import database as db
import inventory as inv
import event
import utility
import field_command as cmd

class MenuController (object):
    def __init__(self, controller):
        self.controller = controller
        self.menuState = g.MenuState.MENU
        self.prevMenuState = [self.menuState]

        self.UI = MenuUI(self)

        self.currentHero = None

        self.queuedAction = None
        self.uiCallback = None
        self.eventQueue = event.EventQueue()

    def change_state(self, state):
        if self.menuState != self.prevMenuState:
            self.prevMenuState.append(self.menuState)
        self.menuState = state

        utility.log("BATTLE STATE CHANGED: " + str(self.prevMenuState) + " >> " + str(self.menuState))

    def prev_state(self):
        index = len(self.prevMenuState) - 1
        self.menuState = self.prevMenuState[index]
        del self.prevMenuState[index]

    def update(self):
        eventCallback = self.eventQueue.run()

        if eventCallback < 0:
            if self.menuState != g.MenuState.EXIT:
                self.uiCallback = self.UI.update()
                if self.uiCallback != None:
                    self.uiCallback.start(self.currentHero)

class MenuUI(object):
    def __init__(self, MC):
        self.MC = MC

        self.statusPanel = pygame.image.load("spr/menu/status-panel.png")
        self.commandPanel = pygame.image.load("spr/menu/command-panel.png")
        self.infoPanel = pygame.image.load("spr/menu/info-panel.png")
        self.itemPanel = pygame.image.load("spr/menu/item-panel.png")
        self.cursorImage = pygame.image.load("spr/cursor-h.png")

        self.iconBlood = pygame.image.load("spr/battle/icon-blood.png")
        self.iconMoon = pygame.image.load("spr/battle/icon-moon.png")
        self.iconNotes = {}
        self.iconNotes[g.DamageType.LIGHT] = pygame.image.load("spr/battle/icon-note-wht.png")
        self.iconNotes[g.DamageType.DARK] = pygame.image.load("spr/battle/icon-note-blk.png")
        self.iconNotes[g.DamageType.FIRE] = pygame.image.load("spr/battle/icon-note-red.png")
        self.iconNotes[g.DamageType.ICE] = pygame.image.load("spr/battle/icon-note-blu.png")
        self.iconNotes[g.DamageType.ELEC] = pygame.image.load("spr/battle/icon-note-ylw.png")
        self.iconNotes[g.DamageType.WIND] = pygame.image.load("spr/battle/icon-note-grn.png")

        self.infoAnchor = (106, 91)
        self.commandAnchor = [(110, 12), (110, 21), (110, 30), (110, 39), (110, 48), (110, 57), (110, 66)]
        self.statusAnchor = [(94, 15), (94, 55), (94, 95)]
        self.statusAnchorOffset = (0, 9)
        self.itemAnchor = [(65, 24), (65, 32), (65, 40), (65, 48), (65, 56), (65, 64), (65, 72), (65, 80)]
        self.meterIconOffset = (-26, -1)

        self.commandCursorPosOffset = (-7, 0)
        self.commandCursor = 0

        self.selectCursor = 0
        self.selectCursorOffset = 0

        self.targetCursor = 0

        self.cursorIndex = 0
        self.selectedThing = None

    def process_get_command(self):
        self.commandCursor = self.cursorIndex
        selection = self.process_input(0, 6)
        if (selection > -1):
            if selection == 0:
                self.MC.change_state(g.MenuState.ITEM)

    def process_get_item(self):
        self.selectCursor = self.cursorIndex
        selection = self.process_input(0, 7)
        if (selection > -1):
            self.selectedThing = None

    def render_status_window(self):
        self.MC.controller.VIEW_SURF.blit(self.statusPanel, (0, 0))
        index = 0
        for hero in g.PARTY_LIST:
            offset = self.statusAnchor[index]
            self.MC.controller.VIEW_SURF.blit(hero.icon, utility.add_tuple(offset, (-79, 6)))
            self.MC.controller.TEXT_MANAGER.draw_text_ralign(str(hero.attr['name']), offset, g.WHITE)
            offset = utility.add_tuple(offset, self.statusAnchorOffset)
            self.MC.controller.TEXT_MANAGER.draw_text_ralign(str(hero.baseMaxHP), offset, g.WHITE)
            self.MC.controller.TEXT_MANAGER.draw_text_ralign("/", utility.add_tuple(offset, (-27, 0)), g.WHITE)
            self.MC.controller.TEXT_MANAGER.draw_text_ralign(str(hero.attr['hp']), utility.add_tuple(offset, (-31, 0)), g.WHITE)
            offset = utility.add_tuple(offset, self.statusAnchorOffset)
            self.MC.controller.TEXT_MANAGER.draw_text_ralign(str(hero.baseMaxSP), offset, g.WHITE)
            self.MC.controller.TEXT_MANAGER.draw_text_ralign("/", utility.add_tuple(offset, (-27, 0)), g.WHITE)
            self.MC.controller.TEXT_MANAGER.draw_text_ralign(str(hero.attr['sp']), utility.add_tuple(offset, (-31, 0)), g.WHITE)
            offset = utility.add_tuple(offset, self.statusAnchorOffset)
            self.render_meter(hero.skillType, offset)
            index += 1

    def render_item_window(self):
        self.MC.controller.VIEW_SURF.blit(self.itemPanel, (0, 0))

    def render_meter(self, skillType, pos):
        pos = utility.add_tuple(pos, self.meterIconOffset)
        offset = (5, 0)
        if skillType == g.SkillType.BLOOD:
            iconImg = self.iconBlood
        elif skillType == g.SkillType.MOON:
            iconImg = self.iconMoon
        if skillType != g.SkillType.MUSIC:
            for i in range (0, g.METER[skillType]):
                self.MC.controller.VIEW_SURF.blit(iconImg, pos)
                pos = utility.add_tuple(pos, offset)
        else:
            for i in g.METER[skillType]:
                self.MC.controller.VIEW_SURF.blit(self.iconNotes[i], utility.add_tuple(pos, (0,1)))
                pos = utility.add_tuple(pos, offset)

    def render_command_window(self):
        self.MC.controller.VIEW_SURF.blit(self.commandPanel, (0, 0))
        self.MC.controller.VIEW_SURF.blit(self.cursorImage, utility.add_tuple(self.commandAnchor[self.commandCursor], self.commandCursorPosOffset))
        self.MC.controller.TEXT_MANAGER.draw_text("Items", self.commandAnchor[0], g.WHITE)
        self.MC.controller.TEXT_MANAGER.draw_text("Skills", self.commandAnchor[1], g.WHITE)
        self.MC.controller.TEXT_MANAGER.draw_text("Equip", self.commandAnchor[2], g.WHITE)
        self.MC.controller.TEXT_MANAGER.draw_text("Anima", self.commandAnchor[3], g.WHITE)
        self.MC.controller.TEXT_MANAGER.draw_text("Status", self.commandAnchor[4], g.WHITE)
        self.MC.controller.TEXT_MANAGER.draw_text("Config", self.commandAnchor[5], g.WHITE)
        self.MC.controller.TEXT_MANAGER.draw_text("Quit", self.commandAnchor[6], g.WHITE)

    def render_info_window(self):
        self.MC.controller.VIEW_SURF.blit(self.infoPanel, (0, 0))
        self.MC.controller.TEXT_MANAGER.draw_text("GP", self.infoAnchor, g.WHITE)
        self.MC.controller.TEXT_MANAGER.draw_text_ralign(str(g.GP), utility.add_tuple(self.infoAnchor, (48, 9)), g.WHITE)
        self.MC.controller.TEXT_MANAGER.draw_text("Time", utility.add_tuple(self.infoAnchor, (0, 18)), g.WHITE)
        strHr, strMin, strSec = utility.play_time()
        self.MC.controller.TEXT_MANAGER.draw_text_ralign(strSec, utility.add_tuple(self.infoAnchor, (48, 27)), g.WHITE)
        self.MC.controller.TEXT_MANAGER.draw_text_ralign(":", utility.add_tuple(self.infoAnchor, (35, 27)), g.WHITE)
        self.MC.controller.TEXT_MANAGER.draw_text_ralign(strMin, utility.add_tuple(self.infoAnchor, (33, 27)), g.WHITE)
        self.MC.controller.TEXT_MANAGER.draw_text_ralign(":", utility.add_tuple(self.infoAnchor, (20, 27)), g.WHITE)
        self.MC.controller.TEXT_MANAGER.draw_text_ralign(strHr, utility.add_tuple(self.infoAnchor, (18, 27)), g.WHITE)



    def process_input(self, cMin, cMax):
        dt = self.MC.controller.CLOCK.get_time()
        if (g.CURSOR_TIMER >= 0):
            g.CURSOR_TIMER -= dt
        if (g.CONFIRM_TIMER >= 0):
            g.CONFIRM_TIMER -= dt

        if self.MC.controller.KEYS[g.KEY_DOWN]:
            if g.CURSOR_TIMER < 0:
                g.CURSOR_TIMER = g.CURSOR_DELAY
                self.cursorIndex += 1
        elif self.MC.controller.KEYS[g.KEY_UP]:
            if g.CURSOR_TIMER < 0:
                g.CURSOR_TIMER = g.CURSOR_DELAY
                self.cursorIndex -= 1
        elif self.MC.controller.KEYS[g.KEY_LEFT]:
            if g.CURSOR_TIMER < 0:
                g.CURSOR_TIMER = g.CURSOR_DELAY
                if self.MC.menuState == g.MenuState.ITEM or self.MC.menuState == g.MenuState.SKILL:
                    self.selectCursorOffset -= cMax
        elif self.MC.controller.KEYS[g.KEY_RIGHT]:
            if g.CURSOR_TIMER < 0:
                g.CURSOR_TIMER = g.CURSOR_DELAY
                if self.MC.menuState == g.MenuState.ITEM or self.MC.menuState == g.MenuState.SKILL:
                    self.selectCursorOffset += cMax
        elif self.MC.controller.KEYS[g.KEY_CONFIRM]:
            if g.CONFIRM_TIMER < 0:
                g.CONFIRM_TIMER = g.CONFIRM_DELAY
                self.helpLabel = ""
                return self.cursorIndex
        elif self.MC.controller.KEYS[g.KEY_CANCEL]:
            if g.CONFIRM_TIMER < 0:
                g.CONFIRM_TIMER = g.CONFIRM_DELAY
                if self.MC.menuState != g.MenuState.MENU:
                    self.MC.prev_state()
                    #self.restore_cursor()
                else:
                    self.MC.change_state(g.MenuState.EXIT)

        #limit/wrap the cursor
        if self.cursorIndex > cMax:
            self.cursorIndex = cMin
        elif self.cursorIndex < cMin:
            self.cursorIndex = cMax

        return -1


    def update(self):
        self.MC.controller.VIEW_SURF.fill(g.BLACK)
        self.render_status_window()
        self.render_command_window()
        self.render_info_window()

        if self.MC.menuState == g.MenuState.MENU:
            self.process_get_command()
        elif self.MC.menuState == g.MenuState.ITEM:
            self.render_item_window()
            self.process_get_item()

