import pygame
import pygame.locals
import my_globals as g
import inventory as inv
import database as db
import event
import utility


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

        utility.log("MENU STATE CHANGED: " + str(self.prevMenuState) + " >> " + str(self.menuState))

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
                    if self.menuState == g.MenuState.TARGET_ITEM:
                        self.queuedAction (self, self.uiCallback)
                    elif self.menuState == g.MenuState.TARGET_SKILL:
                        self.queuedAction (self, self.uiCallback)


class MenuUI(object):

    def __init__(self, MC):
        self.MC = MC

        self.statusPanel = pygame.image.load("spr/menu/status-panel.png")
        self.commandPanel = pygame.image.load("spr/menu/command-panel.png")
        self.infoPanel = pygame.image.load("spr/menu/info-panel.png")
        self.itemPanel = pygame.image.load("spr/menu/item-panel.png")
        self.skillPanel = pygame.image.load("spr/menu/skill-panel.png")
        self.itemOptionsPanel = pygame.image.load("spr/menu/item-options.png")
        self.cursorImage = pygame.image.load("spr/cursor-h.png")
        self.cursorSelImage = pygame.image.load("spr/menu/cursor-selected.png")
        self.targetCursorImage = pygame.image.load("spr/menu/cursor-target.png")
        self.cursorHeroImage =  pygame.image.load("spr/menu/cursor-hero.png")

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
        self.itemOptionsAnchor = [(90, 85), (90, 94), (90, 103), (90, 112), (90, 121)]
        self.skillAnchor = [(48, 20), (48, 29), (48, 38), (48, 45), (48, 54), (48, 63), (48, 70), (48, 81), (48, 92)]
        self.skillDescAnchor = (44, 104)
        self.skillIndexAnchor = (152, 7)
        self.skillHeroAnchor = (38, 7)
        self.meterIconOffset = (-26, -1)

        self.commandCursorPosOffset = (-7, 0)
        self.commandCursor = 0

        self.selectCursor = 0
        self.selectCursorOffset = 0

        self.skillHeroCursorPosOffset = (4, -10)
        self.skillHeroCursor = 0

        self.skillCursorPosOffset = (-7, 0)
        self.skillCursor = 0
        self.skillCursorOffset = 0

        self.itemCursorPosOffset = (-7, 0)
        self.itemCursor = 0
        self.itemCursorOffset = 0

        self.itemOptionsCursorPosOffset = (-7, 0)
        self.itemOptionsCursor = 0

        self.targetCursorPosOffset = (4, -8)
        self.targetCursor = 0

        self.cursorIndex = 0
        self.selectedThing = None

        self.currentHero = None
        self.currentSkill = None
        self.currentItem = None
        self.currentIndex = -1
        self.currentQuantity = 0
        self.queuedAction = None

    def get_target(self, validTargets):
        self.validTargets = validTargets
        self.selectedThing = None

        if len(validTargets) > self.targetCursor:
            self.cursorIndex = self.targetCursor
        else:
            self.cursorIndex = 0

        if (self.MC.menuState == g.MenuState.SKILL):
            self.MC.change_state(g.MenuState.TARGET_SKILL)
        else:
            self.MC.change_state(g.MenuState.TARGET_ITEM)

    def process_get_command(self):
        self.commandCursor = self.cursorIndex
        selection = self.process_input(0, 6)
        if (selection > -1):
            if selection == 0:
                self.MC.change_state(g.MenuState.ITEM_OPTIONS)
            elif selection == 1:
                self.MC.change_state(g.MenuState.SKILL_HERO)
                self.restore_cursor()

    def process_get_skill_hero(self):
        self.skillHeroCursor = self.cursorIndex
        selection = self.process_input(0, len(g.PARTY_LIST)-1)
        if (selection > -1):
            self.currentHero = g.PARTY_LIST[selection]
            self.MC.change_state(g.MenuState.SKILL)
            self.cursorIndex = 0

    def process_get_item_options(self):
        self.itemOptionsCursor = self.cursorIndex
        selection = self.process_input(0, 4)
        if (selection > -1):
            if selection == 0:
                self.MC.change_state(g.MenuState.ITEM)
            elif selection == 3:
                inv.consolidate()
            elif selection == 1:
                if (g.INVENTORY_SORT_KEY < len(g.INVENTORY_SORT_KEYS)):
                    g.INVENTORY_SORT_KEY = 0
                else:
                    g.INVENTORY_SORT_KEY += 1
                inv.sort_by(g.INVENTORY_SORT_KEYS[g.INVENTORY_SORT_KEY])
            elif selection == 2:
                self.MC.change_state(g.MenuState.ITEM_ORGANIZE)
                self.restore_cursor()
            elif selection == 4:
                self.MC.prev_state()
                self.restore_cursor()

    def process_get_item_organize(self):
        self.itemCursor = self.cursorIndex
        selection = self.process_input(0, 8)
        if (selection > -1):
            if self.currentIndex < 0:
                self.currentIndex = self.itemCursor + self.itemCursorOffset
                utility.log(str(self.currentIndex))
            else:
                newIndex = self.itemCursor + self.itemCursorOffset
                utility.log(str(newIndex))
                newItem = (g.INVENTORY[self.currentIndex][0], g.INVENTORY[self.currentIndex][1])
                swapItem = (g.INVENTORY[newIndex][0], g.INVENTORY[newIndex][1])
                g.INVENTORY[newIndex] = newItem
                g.INVENTORY[self.currentIndex] = swapItem
                self.currentIndex = -1

    def process_get_item(self):
        self.itemCursor = self.cursorIndex
        selection = self.process_input(0, 8)
        if (selection > -1):
            itemIndex = selection + self.itemCursorOffset
            if g.INVENTORY[itemIndex][0].usableField:
                self.currentItem = g.INVENTORY[itemIndex][0]
                self.currentItem.useAction.start(self.MC)

    def process_get_skill(self):
        self.skillCursor = self.cursorIndex
        selection = self.process_input(0, 8)
        if (selection > -1):
            skillIndex = selection + self.skillCursorOffset
            if self.currentHero.skills[skillIndex].usableField:
                if db.Skill.check_cost(self.currentHero,  self.currentHero.skills[skillIndex]):
                    self.currentSkill = self.currentHero.skills[skillIndex]
                    self.currentSkill.useAction.start(self.MC, self.currentHero)
            #if g.INVENTORY[itemIndex][0].usableField:
            #    self.currentItem = g.INVENTORY[itemIndex][0]
            #    self.currentItem.useAction.start(self.MC)

    def process_get_target(self):
        if self.validTargets:
            selection = self.process_input(0, len(self.validTargets)-1)
            if (selection > -1):
                self.selectedThing = self.validTargets[selection]
                self.targetCursor = self.cursorIndex
        else:
            self.helpLabel = ""
            self.MC.prev_state()
            self.restore_cursor()

    def render_target_cursor(self):
        self.MC.controller.VIEW_SURF.blit(self.targetCursorImage, utility.add_tuple(self.portraitAnchor[self.cursorIndex], self.targetCursorPosOffset))

    def render_skill_hero_cursor(self):
        self.MC.controller.VIEW_SURF.blit(self.cursorHeroImage, utility.add_tuple(self.portraitAnchor[self.skillHeroCursor], self.skillHeroCursorPosOffset))

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

    def render_item_options(self):

        self.MC.controller.VIEW_SURF.blit(self.itemOptionsPanel, (0,0))

        self.MC.controller.TEXT_MANAGER.draw_text("Use", self.itemOptionsAnchor[0], g.WHITE)
        self.MC.controller.TEXT_MANAGER.draw_text("Sort", self.itemOptionsAnchor[1], g.WHITE)
        self.MC.controller.TEXT_MANAGER.draw_text("Organize", self.itemOptionsAnchor[2], g.WHITE)
        self.MC.controller.TEXT_MANAGER.draw_text("Condense", self.itemOptionsAnchor[3], g.WHITE)
        self.MC.controller.TEXT_MANAGER.draw_text("Cancel", self.itemOptionsAnchor[4], g.WHITE)

        self.MC.controller.VIEW_SURF.blit(self.cursorImage, utility.add_tuple(self.itemOptionsAnchor[self.itemOptionsCursor], self.itemOptionsCursorPosOffset))

    def render_skill_window(self):
        if self.MC.menuState == g.MenuState.TARGET_SKILL:
            globalOffset = (54, 0)
            helpWidth = 60
        else:
            globalOffset = (0, 0)
            helpWidth = 108

        self.MC.controller.VIEW_SURF.blit(self.skillPanel, globalOffset)
        self.MC.controller.TEXT_MANAGER.draw_text("SP: ", utility.add_tuple(self.skillHeroAnchor, globalOffset), g.WHITE)
        self.MC.controller.TEXT_MANAGER.draw_text_ralign(str(self.currentHero.attr['sp']) + "/" + str(self.currentHero.baseMaxSP), utility.add_tuple(self.skillHeroAnchor, utility.add_tuple(globalOffset, (71, 0))), g.WHITE)
        self.MC.controller.TEXT_MANAGER.draw_text_ralign(str(1 + self.skillCursor + self.skillCursorOffset) + "/" + str(len(self.currentHero.skills)), utility.add_tuple(self.skillIndexAnchor, globalOffset), g.WHITE)

        # draw skill list
        index = 0
        for skill in range(self.skillCursorOffset, self.skillCursorOffset + 9):
            if skill < len(self.currentHero.skills):
                if self.currentHero.skills[skill].usableField:
                    color = g.WHITE
                else:
                    color = g.GRAY
                self.MC.controller.TEXT_MANAGER.draw_text(self.currentHero.skills[skill].name, utility.add_tuple(self.itemAnchor[index], globalOffset), color)
                self.MC.controller.TEXT_MANAGER.draw_text_ralign(str(self.currentHero.skills[skill].spCost), utility.add_tuple(self.itemAnchor[index], utility.add_tuple(globalOffset, (104,0))), color)
            index += 1

        self.MC.controller.VIEW_SURF.blit(self.cursorImage, utility.add_tuple(self.skillAnchor[self.skillCursor],utility.add_tuple(globalOffset, self.skillCursorPosOffset)))
        # draw current item description
        if self.skillCursor + self.skillCursorOffset < len(self.currentHero.skills):
            curSkill = self.currentHero.skills[self.skillCursor + self.skillCursorOffset]
            if curSkill.desc != "":
                parsedStr = self.MC.controller.TEXT_MANAGER.parse_string(curSkill.desc, helpWidth)

                curOffset = utility.add_tuple(globalOffset, (0, 0))
                lineOffset = (0, 8)

                index = 0
                for line in range(0, len(parsedStr)):
                    self.MC.controller.TEXT_MANAGER.draw_text(parsedStr[index],utility.add_tuple(self.skillDescAnchor, curOffset),g.WHITE)
                    curOffset = utility.add_tuple(curOffset, lineOffset)
                    index += 1

    def render_item_window(self):
        if self.MC.menuState == g.MenuState.TARGET_ITEM:
            globalOffset = (54, 0)
            helpWidth = 60
        else:
            globalOffset = (0, 0)
            helpWidth = 108

        self.MC.controller.VIEW_SURF.blit(self.itemPanel, globalOffset)
        self.MC.controller.TEXT_MANAGER.draw_text_ralign(str(1 + self.itemCursor + self.itemCursorOffset) + "/" + str( g.INVENTORY_MAX_SLOTS), utility.add_tuple(self.itemIndexAnchor, globalOffset), g.WHITE)

        #draw item list
        index = 0
        for item in range(self.itemCursorOffset, self.itemCursorOffset + 9):
            if g.INVENTORY[item][0].name != "":
                if g.INVENTORY[item][0].usableField:
                    color = g.WHITE
                else:
                    color = g.GRAY
                self.MC.controller.TEXT_MANAGER.draw_text_ralign(str(g.INVENTORY[item][1])+ "x", utility.add_tuple(self.itemAnchor[index], utility.add_tuple(globalOffset, (22, 0))), g.WHITE)
                self.MC.controller.TEXT_MANAGER.draw_text(g.INVENTORY[item][0].name, utility.add_tuple(self.itemAnchor[index], utility.add_tuple(globalOffset, (24, 0))), color)
            index += 1

        if self.MC.menuState != g.MenuState.ITEM_OPTIONS:
            selIndex = self.currentIndex - self.itemCursorOffset
            if self.MC.menuState == g.MenuState.ITEM_ORGANIZE and selIndex >= 0 and selIndex <= 8:
                self.MC.controller.VIEW_SURF.blit(self.cursorSelImage, utility.add_tuple(self.itemAnchor[selIndex], utility.add_tuple(globalOffset, self.itemCursorPosOffset)))
            self.MC.controller.VIEW_SURF.blit(self.cursorImage, utility.add_tuple(self.itemAnchor[self.itemCursor], utility.add_tuple(globalOffset, self.itemCursorPosOffset)))

        #draw current item description
        curItem = g.INVENTORY[self.itemCursor + self.itemCursorOffset][0]
        if curItem.desc != "":
            parsedStr = self.MC.controller.TEXT_MANAGER.parse_string(curItem.desc, helpWidth)

            curOffset = utility.add_tuple(globalOffset, (0, 0))
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
        if self.MC.menuState == g.MenuState.MENU:
            self.cursorIndex = self.commandCursor
        if self.MC.menuState == g.MenuState.ITEM or self.MC.menuState == g.MenuState.ITEM_ORGANIZE:
            self.cursorIndex = self.itemCursor
        if self.MC.menuState == g.MenuState.ITEM_OPTIONS:
            self.cursorIndex = self.itemOptionsCursor
        if self.MC.menuState == g.MenuState.SKILL_HERO:
            self.cursorIndex = self.skillHeroCursor
        if self.MC.menuState == g.MenuState.SKILL:
            self.cursorIndex = self.skillCursor
        self.currentIndex = -1

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
                if self.MC.menuState == g.MenuState.ITEM or self.MC.menuState == g.MenuState.ITEM_ORGANIZE:
                    self.itemCursorOffset -= cMax
                if self.MC.menuState == g.MenuState.SKILL:
                    if self.skillHeroCursor > 0:
                        self.skillHeroCursor -= 1
                    else:
                        self.skillHeroCursor = len(g.PARTY_LIST)-1
                    self.currentHero = g.PARTY_LIST[self.skillHeroCursor]
                    self.cursorIndex = 0
                    self.skillCursorOffset = 0
        elif self.MC.controller.KEYS[g.KEY_RIGHT]:
            if g.CURSOR_TIMER < 0:
                g.CURSOR_TIMER = g.CURSOR_DELAY
                if self.MC.menuState == g.MenuState.ITEM or self.MC.menuState == g.MenuState.ITEM_ORGANIZE:
                    self.itemCursorOffset += cMax
                if self.MC.menuState == g.MenuState.SKILL:
                    if self.skillHeroCursor < len(g.PARTY_LIST)-1:
                        self.skillHeroCursor += 1
                    else:
                        self.skillHeroCursor = 0
                    self.currentHero = g.PARTY_LIST[self.skillHeroCursor]
                    self.cursorIndex = 0
                    self.skillCursorOffset = 0
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
            if self.cursorIndex >= len(self.currentHero.skills):
                self.cursorIndex = 0
            elif self.cursorIndex < 0:
                self.cursorIndex = len(self.currentHero.skills) - 1

            if self.skillCursorOffset > len(self.currentHero.skills) - 5:
                self.skillCursorOffset = 0
            elif self.skillCursorOffset < 0:
                self.skillCursorOffset = len(self.currentHero.skills) - 5

            if self.cursorIndex > 4:
                if self.skillCursorOffset < len(self.currentHero.skills) - 5:
                    self.skillCursorOffset += 1
                    self.cursorIndex -= 1
            elif self.cursorIndex < 0:
                if self.skillCursorOffset > 0:
                    self.skillCursorOffset -= 1
                    self.cursorIndex += 1

        if (self.MC.menuState == g.MenuState.ITEM or self.MC.menuState == g.MenuState.ITEM_ORGANIZE) and self.cursorIndex > 8:
            if self.itemCursorOffset < g.INVENTORY_MAX_SLOTS - 9:
                self.itemCursorOffset += 1
                self.cursorIndex -= 1

        if (self.MC.menuState == g.MenuState.ITEM or self.MC.menuState == g.MenuState.ITEM_ORGANIZE) and self.cursorIndex < 0:
            if self.itemCursorOffset > 0:
                self.itemCursorOffset -= 1
                self.cursorIndex += 1

        if self.itemCursorOffset > g.INVENTORY_MAX_SLOTS - 9:
            self.itemCursorOffset = 0

        if self.itemCursorOffset < 0:
            self.itemCursorOffset = g.INVENTORY_MAX_SLOTS - 9

        if self.cursorIndex > cMax:
            self.cursorIndex = cMin
            if self.MC.menuState == g.MenuState.ITEM or self.MC.menuState == g.MenuState.ITEM_ORGANIZE:
                self.itemCursorOffset = 0
            elif self.MC.menuState == g.MenuState.SKILL:
                self.skillCursorOffset = 0
        elif self.cursorIndex < cMin:
            self.cursorIndex = cMax
            if self.MC.menuState == g.MenuState.ITEM or self.MC.menuState == g.MenuState.ITEM_ORGANIZE:
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
        elif self.MC.menuState == g.MenuState.ITEM_OPTIONS:
            self.render_item_window()
            self.render_item_options()
            self.process_get_item_options()
        elif self.MC.menuState == g.MenuState.ITEM_ORGANIZE:
            self.render_item_window()
            self.process_get_item_organize()
        elif self.MC.menuState == g.MenuState.ITEM:
            self.render_item_window()
            self.process_get_item()
        elif self.MC.menuState == g.MenuState.TARGET_ITEM:
            self.render_target_cursor()
            self.render_item_window()
            self.process_get_target()
        elif self.MC.menuState == g.MenuState.TARGET_SKILL:
            self.render_skill_hero_cursor()
            self.render_target_cursor()
            self.render_skill_window()
            self.process_get_target()
        elif self.MC.menuState == g.MenuState.SKILL_HERO:
            self.render_skill_hero_cursor()
            self.process_get_skill_hero()
        elif self.MC.menuState == g.MenuState.SKILL:
            self.render_skill_hero_cursor()
            self.render_skill_window()
            self.process_get_skill()

        if self.selectedThing != None:
            returnVal = self.selectedThing
            self.selectedThing = None
            return returnVal
        else:
            return None

