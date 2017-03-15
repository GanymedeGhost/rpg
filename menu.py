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
        self.targetCursorImage = pygame.image.load("spr/menu/cursor-target.png")

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
        self.portraitAnchor = [(15, 21), (15, 61), (15, 101)]
        self.itemIndexAnchor = (152, 7)
        self.itemAnchor = [(48, 20), (48, 29), (48, 38), (48, 45), (48, 54), (48, 63), (48, 70), (48, 81), (48, 92)]
        self.itemDescAnchor = (44, 104)
        self.meterIconOffset = (-26, -1)

        self.commandCursorPosOffset = (-7, 0)
        self.commandCursor = 0

        self.selectCursor = 0
        self.selectCursorOffset = 0

        self.skillCursorPosOffset = (-7, 0)
        self.skillCursor = 0
        self.skillCursorOffset = 0

        self.itemCursorPosOffset = (-7, 0)
        self.itemCursor = 0
        self.itemCursorOffset = 0

        self.targetCursorPosOffset = (4, -8)
        self.targetCursor = 0

        self.cursorIndex = 0
        self.selectedThing = None

        self.currentHero = None
        self.currentSkill = None
        self.currentItem = None

    def get_target(self, targetAll = False):
        self.MC.change_state(g.MenuState.TARGET_ITEM)

    def process_get_command(self):
        self.commandCursor = self.cursorIndex
        selection = self.process_input(0, 6)
        if (selection > -1):
            if selection == 0:
                self.MC.change_state(g.MenuState.ITEM)

    def process_get_item(self):
        self.itemCursor = self.cursorIndex + self.itemCursorOffset
        selection = self.process_input(0, 8)
        if (selection > -1):
            if g.INVENTORY[selection][0].usableField:
                self.currentItem = g.INVENTORY[selection][0]
                self.get_target()

    def process_get_target(self):
        self.targetCursor = self.cursorIndex
        selection = self.process_input(0, 2)
        if (selection > -1):
            self.selectedThing = None

    def render_target_cursor(self):
        self.MC.controller.VIEW_SURF.blit(self.targetCursorImage, utility.add_tuple(self.portraitAnchor[self.cursorIndex], self.targetCursorPosOffset))

    def render_status_window(self):
        self.MC.controller.VIEW_SURF.blit(self.statusPanel, (0, 0))
        index = 0
        for hero in g.PARTY_LIST:
            offset = self.statusAnchor[index]
            self.MC.controller.VIEW_SURF.blit(hero.icon, self.portraitAnchor[index])
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
        self.MC.controller.TEXT_MANAGER.draw_text_ralign(str(1 + self.itemCursor + self.itemCursorOffset) + "/" + str( g.INVENTORY_MAX_SLOTS), self.itemIndexAnchor, g.WHITE)

        #draw item list
        index = 0
        for item in range(self.itemCursorOffset, self.itemCursorOffset + 7):
            if g.INVENTORY[item][0].name != "":
                self.MC.controller.TEXT_MANAGER.draw_text_ralign(str(g.INVENTORY[item][1])+ "x", utility.add_tuple(self.itemAnchor[index], (22, 0)), g.WHITE)
                self.MC.controller.TEXT_MANAGER.draw_text(g.INVENTORY[item][0].name, utility.add_tuple(self.itemAnchor[index], (24, 0)), g.WHITE)
            index += 1

        self.MC.controller.VIEW_SURF.blit(self.cursorImage, utility.add_tuple(self.itemAnchor[self.itemCursor], self.itemCursorPosOffset))

        #draw current item description
        curItem = g.INVENTORY[self.itemCursor + self.itemCursorOffset][0]
        if curItem.desc != "":
            parsedStr = self.MC.controller.TEXT_MANAGER.parse_string(curItem.desc, 120)

            curOffset = (0, 0)
            lineOffset = (0, 8)

            index = 0
            for line in range(0, len(parsedStr)):
                self.MC.controller.TEXT_MANAGER.draw_text(parsedStr[index], utility.add_tuple(self.itemDescAnchor, curOffset), g.WHITE)
                curOffset = utility.add_tuple(curOffset, lineOffset)
                index += 1

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
        self.MC.controller.TEXT_MANAGER.draw_text_ralign(g.PLAY_SEC_STR, utility.add_tuple(self.infoAnchor, (48, 27)), g.WHITE)
        self.MC.controller.TEXT_MANAGER.draw_text_ralign(":", utility.add_tuple(self.infoAnchor, (35, 27)), g.WHITE)
        self.MC.controller.TEXT_MANAGER.draw_text_ralign(g.PLAY_MIN_STR, utility.add_tuple(self.infoAnchor, (33, 27)), g.WHITE)
        self.MC.controller.TEXT_MANAGER.draw_text_ralign(":", utility.add_tuple(self.infoAnchor, (20, 27)), g.WHITE)
        self.MC.controller.TEXT_MANAGER.draw_text_ralign(g.PLAY_HR_STR, utility.add_tuple(self.infoAnchor, (18, 27)), g.WHITE)

    def restore_cursor(self):
        if (self.MC.menuState == g.MenuState.MENU):
            self.cursorIndex = self.commandCursor
        if (self.MC.menuState == g.MenuState.ITEM):
            self.cursorIndex = self.itemCursor

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
                if self.MC.menuState == g.MenuState.ITEM:
                    self.itemCursorOffset -= cMax
        elif self.MC.controller.KEYS[g.KEY_RIGHT]:
            if g.CURSOR_TIMER < 0:
                g.CURSOR_TIMER = g.CURSOR_DELAY
                if self.MC.menuState == g.MenuState.ITEM:
                    self.itemCursorOffset += cMax
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
                    self.restore_cursor()
                else:
                    self.MC.change_state(g.MenuState.EXIT)

        #limit/wrap the cursor
        if self.MC.menuState == g.MenuState.SKILL:
            if self.cursorIndex >= len(self.MC.currentHero.skills):
                self.cursorIndex = 0
            elif self.cursorIndex < 0:
                self.cursorIndex = len(self.MC.currentHero.skills) - 1

            if self.skillCursorOffset > len(self.MC.currentHero.skills) - 5:
                self.skillCursorOffset = 0
            elif self.skillCursorOffset < 0:
                self.skillCursorOffset = len(self.MC.currentHero.skills) - 5

            if self.cursorIndex > 4:
                if self.skillCursorOffset < len(self.MC.currentHero.skills) - 5:
                    self.skillCursorOffset += 1
                    self.cursorIndex -= 1
            elif self.cursorIndex < 0:
                if self.skillCursorOffset > 0:
                    self.skillCursorOffset -= 1
                    self.cursorIndex += 1

        if self.MC.menuState == g.MenuState.ITEM and self.cursorIndex > 8:
            if self.itemCursorOffset < g.INVENTORY_MAX_SLOTS - 9:
                self.itemCursorOffset += 1
                self.cursorIndex -= 1

        if self.MC.menuState == g.MenuState.ITEM and self.cursorIndex < 0:
            if self.itemCursorOffset > 0:
                self.itemCursorOffset -= 1
                self.cursorIndex += 1

        if self.itemCursorOffset > g.INVENTORY_MAX_SLOTS - 9:
            self.itemCursorOffset = 0

        if self.itemCursorOffset < 0:
            self.itemCursorOffset = g.INVENTORY_MAX_SLOTS - 9

        if self.cursorIndex > cMax:
            self.cursorIndex = cMin
            if self.MC.menuState == g.MenuState.ITEM:
                self.itemCursorOffset = 0
            elif self.MC.menuState == g.MenuState.SKILL:
                self.skillCursorOffset = 0
        elif self.cursorIndex < cMin:
            self.cursorIndex = cMax
            if self.MC.menuState == g.MenuState.ITEM:
                self.itemCursorOffset = g.INVENTORY_MAX_SLOTS - 9
            elif self.MC.menuState == g.MenuState.SKILL:
                self.skillCursorOffset = len(self.MC.currentHero.skills) - 9

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
        elif self.MC.menuState == g.MenuState.TARGET_ITEM:
            self.render_target_cursor()
            self.render_item_window()
            self.process_get_target()

