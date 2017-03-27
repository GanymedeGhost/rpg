import pygame
import pygame.locals
import math
import my_globals as g
import inventory as inv
import animarium as anmr
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

        self.currentHero = None
        self.currentItem = None
        self.currentSkill = None
        self.currentEquipSlot = None
        self.currentTarget = None

    def change_state(self, state):
        if self.menuState != self.prevMenuState:
            self.prevMenuState.append(self.menuState)
        self.menuState = state

        self.UI.on_state_change()

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
                    if self.menuState == g.MenuState.MENU:
                        self.change_state(self.uiCallback)
                    elif self.menuState == g.MenuState.TARGET_ITEM:
                        self.queuedAction (self, self.uiCallback)
                    elif self.menuState == g.MenuState.TARGET_SKILL:
                        self.queuedAction (self, self.uiCallback)

    def clean_up(self):
        self.UI.clean_up()
        del self.UI


class MenuUI(object):

    def __init__(self, MC):
        self.MC = MC

        self.mainPanel = pygame.image.load("spr/menu/main.png")
        self.statusPanel = pygame.image.load("spr/menu/status-panel.png")
        self.commandPanel = pygame.image.load("spr/menu/command-panel.png")
        self.infoPanel = pygame.image.load("spr/menu/info-panel.png")
        self.itemPanel = pygame.image.load("spr/menu/item-panel.png")
        self.skillPanel = pygame.image.load("spr/menu/skill-panel.png")
        self.equipPanel = pygame.image.load("spr/menu/equip-panel.png")
        self.itemOptionsPanel = pygame.image.load("spr/menu/item-options.png")
        self.cursorImage = pygame.image.load("spr/cursor-h.png")
        self.cursorSelImage = pygame.image.load("spr/menu/cursor-selected.png")
        self.targetCursorImage = pygame.image.load("spr/menu/cursor-target.png")
        self.cursorHeroImage =  pygame.image.load("spr/menu/cursor-hero.png")
        self.statsPanel = pygame.image.load("spr/menu/stats-panel.png")
        self.animagiPanel = pygame.image.load("spr/menu/animagi-panel.png")
        self.resPanel = pygame.image.load("spr/menu/res-panel.png")

        self.iconBlood = pygame.image.load("spr/battle/icon-blood.png")
        self.iconMoon = pygame.image.load("spr/battle/icon-moon.png")
        self.iconNotes = {}
        self.iconNotes[g.DamageType.LIGHT] = pygame.image.load("spr/battle/icon-note-wht.png")
        self.iconNotes[g.DamageType.DARK] = pygame.image.load("spr/battle/icon-note-blk.png")
        self.iconNotes[g.DamageType.FIRE] = pygame.image.load("spr/battle/icon-note-red.png")
        self.iconNotes[g.DamageType.COLD] = pygame.image.load("spr/battle/icon-note-blu.png")
        self.iconNotes[g.DamageType.ELEC] = pygame.image.load("spr/battle/icon-note-ylw.png")
        self.iconNotes[g.DamageType.WIND] = pygame.image.load("spr/battle/icon-note-grn.png")

        self.infoAnchor = (237, 182)
        self.mainAnchor = [(10, 30), (10, 98), (10, 166)]
        self.portraitAnchor = [(15, 21), (15, 61), (15, 101)]
        self.itemIndexAnchor = (152, 7)
        self.itemAnchor = [(48, 20), (48, 29), (48, 38), (48, 47), (48, 56), (48, 65), (48, 74), (48, 83), (48, 92)]
        self.itemDescAnchor = (44, 104)
        self.itemOptionsAnchor = [(90, 85), (90, 94), (90, 103), (90, 112), (90, 121)]
        self.skillAnchor = [(48, 20), (48, 29), (48, 38), (48, 47), (48, 56), (48, 65), (48, 74), (48, 83), (48, 92)]
        self.skillDescAnchor = (44, 104)
        self.skillIndexAnchor = (152, 7)
        self.skillHeroAnchor = (38, 7)
        self.equipSlotAnchor = [(74, 19), (74, 29), (74, 39)]
        self.equipListAnchor = [(48, 19), (48, 29), (48, 39)]
        self.equipSelAnchor = (45, 52)
        self.equipCurAnchor = (45, 94)
        self.equipIndexAnchor = (152, 7)
        self.meterIconOffset = (-26, -1)
        self.statusPageAnchor = (136, 11)
        self.resAnchor = [(104, 21), (104, 31), (104, 41), (104, 51), (104, 61), (104, 71), (104, 81), (104, 91), (104, 101), (154, 21), (154, 31), (154, 41), (154, 51), (154, 61), (154, 71), (154, 81)]
        self.statsAnchor = [(45, 21), (152, 31), (152, 41), (94, 73), (94, 83), (94, 93), (94, 103), (94, 113), (94, 123), (152, 73), (152, 83), (152, 93), (152, 103), (152, 113), (152, 123)]
        self.statsOffset = (-24, 0)
        self.animagiHeroAnchor = (44, 20)
        self.animagiListAnchor = [(48, 20), (48, 30), (48, 40), (48, 50), (48, 60)]
        self.animagiPageAnchor = (100, 72)
        self.animagiStatsAnchor = [(44, 114), (44, 124)]
        self.animagiGrowthAnchor = [(68, 80), (68, 90), (68, 100), (124, 80), (124, 90), (124, 100)]
        self.animagiSkillAnchor = [(48, 80), (48, 90), (48, 100)]

        self.resOffset = (-25, 0)

        self.hCursorPosOffset = (-8, 5)

        self.commandCursorPosOffset = (-7, 0)
        self.commandCursor = 0
        self.commandCursorPrev = 0

        self.skillHeroCursorPosOffset = (4, -10)
        self.skillHeroCursor = 0

        self.skillCursorPosOffset = (-7, 0)
        self.skillCursor = 0
        self.skillCursorOffset = 0
        self.skillCursorPrev = 0
        self.skillCursorOffsetPrev = 0

        self.itemCursorPosOffset = (-7, 0)
        self.itemCursor = 0
        self.itemCursorOffset = 0
        self.itemCursorPrev = 0
        self.itemCursorOffsetPrev = 0

        self.itemOptionsCursorPosOffset = (-7, 0)
        self.itemOptionsCursor = 0
        self.itemOptionsCursorPrev = 0

        self.equipCursorPosOffset = (-33, 0)
        self.equipListCursorPosOffset = (-7, 0)
        self.equipHeroCursor = 0
        self.equipCursor = 0
        self.equipListCursor = 0
        self.equipListCursorOffset = 0
        self.equipCursorPrev = 0
        self.equipListCursorPrev = 0
        self.equipListCursorOffsetPrev = 0

        self.animagiCursorPosOffset = (-7, 0)
        self.animagiHeroCursor = 0
        self.animagiCursor = 0
        self.animagiCursorOffset = 0
        self.animagiConfirmCursor = 0
        self.animagiCursorPrev = 0
        self.animagiCursorOffsetPrev = 0

        self.targetCursorPosOffset = (4, -8)
        self.targetCursor = 0


        self.cursorIndex = 0
        self.selectedThing = None

        self.equipInfoPage = 0
        self.equipInfoPages = 3

        self.statusHeroCursor = 0
        self.statusPage = 0
        self.statusPages = 2

        self.animagiPage = 0
        self.animagiPages = 2

        self.currentHero = None
        self.currentSkill = None
        self.currentItem = None
        self.currentEquipSlot = None
        self.currentEquipList = []
        self.currentIndex = -1
        self.currentQuantity = 0
        self.queuedAction = None

        self.commandTableLength = 5
        self.commandTable = self.init_command_table()

        self.itemOptionsTableLength = 4
        self.itemOptionsTable = self.init_item_options_table()

        self.itemTableLength = 9
        self.itemTable = self.init_item_table()

        self.skillTableLength = 9
        self.skillTable = self.init_skill_table()

        self.equipSlotTableLength = 3
        self.equipSlotTable = self.init_equip_slot_table()

        self.equipListTableLength = 3
        self.equipListTable = self.init_equip_list_table()

        self.equipCurStatsTableLength = 3
        self.equipCurStatsTable = self.init_equip_cur_stats_table()

        self.equipSelStatsTableLength = 3
        self.equipSelStatsTable = self.init_equip_sel_stats_table()

        self.equipCurResTableLength = 3
        self.equipCurResTable = self.init_equip_cur_res_table()

        self.equipSelResTableLength = 3
        self.equipSelResTable = self.init_equip_sel_res_table()

        self.animagiTableLength = 5
        self.animagiTable = self.init_animagi_table()

        self.animagiGrowthTableLength = 3
        self.animagiGrowthTable = self.init_animagi_growth_table()

        self.animagiSkillsTableLength = 3
        self.animagiSkillsTable = self.init_animagi_skills_table()

        self.animagiExpTableLength = 2
        self.animagiExpTable = None

        self.statsTableLength = 6
        self.statsTable = self.init_stats_table()

        self.resTableLength = 9
        self.resTable = self.init_res_table()

    def clean_up(self):
        del self.commandTable
        del self.itemOptionsTable
        del self.itemTable
        del self.skillTable
        del self.equipSlotTable
        del self.equipListTable
        del self.equipCurStatsTable
        del self.equipSelStatsTable
        del self.equipCurResTable
        del self.equipSelResTable
        del self.animagiTable
        del self.animagiGrowthTable
        del self.animagiSkillsTable
        del self.statsTable
        del self.resTable

    def on_state_change(self):
        self.restore_cursor()

    def init_command_table(self):
        topLeft = (241, 7)
        widths = [80]
        heights = [11, 11, 11, 11, 11, 11]
        strings = [["Items"], ["Skills"], ["Equip"], ["Animagi"], ["Status"], ["Exit"]]
        aligns = ["left"]
        return Table(self.MC, topLeft, widths, heights, strings, aligns, [])

    def init_item_options_table(self):
        topLeft = (241, 7)
        widths = [80]
        heights = [11, 11, 11, 11, 11]
        strings = [["Use"], ["Sort"], ["Arrange"], ["Condense"], ["Back"],]
        aligns = ["left"]
        return Table(self.MC, topLeft, widths, heights, strings, aligns, [])

    def init_item_table(self):
        topLeft = (48, 20)
        widths = [22, 90]
        heights = [11, 11, 11, 11, 11, 11, 11, 11, 11]
        strings = [["",""],["",""],["",""],["",""],["",""],["",""],["",""],["",""],["",""]]
        aligns = ["right", "left"]
        colors = [[g.GRAY, g.WHITE], [g.GRAY, g.WHITE], [g.GRAY, g.WHITE], [g.GRAY, g.WHITE], [g.GRAY, g.WHITE], [g.GRAY, g.WHITE], [g.GRAY, g.WHITE], [g.GRAY, g.WHITE], [g.GRAY, g.WHITE]]
        return Table(self.MC, topLeft, widths, heights, strings, aligns, colors)

    def update_item_table(self):
        strings = self.itemTable.strings
        for i in range(0, self.itemTableLength):
            ii = i + self.itemCursorOffset
            if g.INVENTORY[ii][0].name != "":
                prefix = g.INVENTORY[ii][0].icon
                if prefix != "":
                    prefix += " "
                strings[i][0] = str(g.INVENTORY[ii][1]) + "x"
                strings[i][1] = prefix + g.INVENTORY[ii][0].name
            else:
                strings[i][0] = ""
                strings[i][1] = ""

    def init_skill_table(self):
        topLeft = (48, 20)
        widths = [8, 74, 24]
        heights = [11, 11, 11, 11, 11, 11, 11, 11, 11]
        strings = [["","",""],["","",""],["","",""],["","",""],["","",""],["","",""],["","",""],["","",""],["","",""]]
        aligns = ["right", "left", "right"]
        return Table(self.MC, topLeft, widths, heights, strings, aligns, [])

    def update_skill_table(self):
        strings = self.skillTable.strings
        colors = self.skillTable.colors
        for i in range(0, self.skillTableLength):
            ii = i + self.skillCursorOffset
            if (ii < len(self.currentHero.skills)):
                strings[i][0] = self.currentHero.skills[ii].icon

                if self.currentHero.skills[ii].usableField:
                    colors[i][1] = g.WHITE
                else:
                    colors[i][1] = g.GRAY
                strings[i][1] = self.currentHero.skills[ii].name

                if self.currentHero.attr["sp"] < self.currentHero.skills[ii].spCost:
                    colors[i][2] = g.RED
                else:
                    colors[i][2] = g.WHITE

                strings[i][2] = str(self.currentHero.skills[ii].spCost)
            else:
                strings[i][0] = ""
                strings[i][1] = ""
                strings[i][2] = ""

    def init_equip_slot_table(self):
        topLeft = (48, 19)
        widths = [26, 80]
        heights = [11, 11, 11]
        strings = [["Wpn:", ""], ["Acc:", ""], ["Acc:", ""]]
        aligns = ["right", "left"]
        colors = [[g.WHITE, g.GRAY], [g.WHITE, g.GRAY], [g.WHITE, g.GRAY]]
        return Table(self.MC, topLeft, widths, heights, strings, aligns, colors)

    def update_equip_slot_table(self):
        strings = self.equipSlotTable.strings
        i = 0
        for slot in self.currentHero.equip:
            prefix = self.currentHero.equip[slot].icon
            if prefix != "":
                prefix += " "
            strings[i][1] = prefix + self.currentHero.equip[slot].name
            i += 1

    def init_equip_list_table(self):
        topLeft = (48, 19)
        widths = [110]
        heights = [11, 11, 11]
        strings = [[""], [""], [""]]
        aligns = ["left"]
        return Table(self.MC, topLeft, widths, heights, strings, aligns, [])

    def update_equip_list_table(self):
        strings = self.equipListTable.strings
        for i in range(0, self.equipListTableLength):
            ii = i + self.equipListCursorOffset
            if (ii < len(self.currentEquipList)):
                prefix = self.currentEquipList[ii].icon
                if prefix != "":
                    prefix += " "
                strings[i][0] = prefix + self.currentEquipList[ii].name
            else:
                strings[i][0] = ""

    def init_equip_cur_stats_table(self):
        topLeft = (48, 104)
        widths = [24, 16, 24, 16]
        heights = [11, 11, 11]
        strings = [["", "", "", ""], ["", "", "", ""], ["", "", "", ""]]
        aligns = ["right","right","right","right"]
        colors = [[g.GRAY, g.GRAY, g.GRAY, g.GRAY], [g.GRAY, g.GRAY, g.GRAY, g.GRAY], [g.GRAY, g.GRAY, g.GRAY, g.GRAY]]
        return Table(self.MC, topLeft, widths, heights, strings, aligns, colors)

    def update_equip_cur_stats(self):
        self.equipCurStatsTable.strings = [["", "", "", ""], ["", "", "", ""], ["", "", "", ""]]
        strings = self.equipCurStatsTable.strings
        colors = self.equipCurStatsTable.colors

        labelInd = [[0,0], [0,2], [1,0], [1,2], [2,0], [2,2]]
        valInd = [[0,1], [0,3], [1,1], [1,3], [2,1], [2,3]]

        curEquip = self.currentHero.equip[self.currentEquipSlot]

        labels = []
        vals = []
        for stat in curEquip.attr:
            labels.append(g.ATTR_NAME[stat])
            vals.append(curEquip.attr[stat])

        for i in range (0, len(labels)):
            strings[labelInd[i][0]][labelInd[i][1]] = labels[i]
            strings[valInd[i][0]][valInd[i][1]] = str(vals[i])
            if vals[i] > 0:
                colors[valInd[i][0]][valInd[i][1]] = g.GREEN
            else:
                colors[valInd[i][0]][valInd[i][1]] = g.RED

    def init_equip_cur_res_table(self):
        topLeft = (48, 104)
        widths = [32, 18, 35, 18]
        heights = [11, 11, 11]
        strings = [["", "", "", ""], ["", "", "", ""], ["", "", "", ""]]
        aligns = ["right","right","right","right"]
        colors = [[g.GRAY, g.GRAY, g.GRAY, g.GRAY], [g.GRAY, g.GRAY, g.GRAY, g.GRAY], [g.GRAY, g.GRAY, g.GRAY, g.GRAY]]
        return Table(self.MC, topLeft, widths, heights, strings, aligns, colors)

    def update_equip_cur_res(self):
        self.equipCurResTable.strings = [["", "", "", ""], ["", "", "", ""], ["", "", "", ""]]
        strings = self.equipCurResTable.strings
        colors = self.equipCurResTable.colors

        labelInd = [[0,0], [0,2], [1,0], [1,2], [2,0], [2,2]]
        valInd = [[0,1], [0,3], [1,1], [1,3], [2,1], [2,3]]

        curEquip = self.currentHero.equip[self.currentEquipSlot]

        labels = []
        vals = []
        for res in curEquip.resD:
            labels.append(g.DamageType.NAME[res])
            vals.append(math.trunc(curEquip.resD[res]*100))
        for res in curEquip.resS:
            labels.append(g.BattlerStatus.NAME[res])
            vals.append(math.trunc(curEquip.resS[res]*100))

        for i in range (0, len(labels)):
            strings[labelInd[i][0]][labelInd[i][1]] = labels[i]
            strings[valInd[i][0]][valInd[i][1]] = str(vals[i])
            if vals[i] > 0:
                colors[valInd[i][0]][valInd[i][1]] = g.GREEN
            else:
                colors[valInd[i][0]][valInd[i][1]] = g.RED

    def init_equip_sel_stats_table(self):
        topLeft = (48, 62)
        widths = [24, 16, 24, 16]
        heights = [11, 11, 11]
        strings = [["", "", "", ""], ["", "", "", ""], ["", "", "", ""]]
        aligns = ["right","right","right","right"]
        colors = [[g.GRAY, g.GRAY, g.GRAY, g.GRAY], [g.GRAY, g.GRAY, g.GRAY, g.GRAY], [g.GRAY, g.GRAY, g.GRAY, g.GRAY]]
        return Table(self.MC, topLeft, widths, heights, strings, aligns, colors)

    def update_equip_sel_stats(self):
        self.equipSelStatsTable.strings = [["", "", "", ""], ["", "", "", ""], ["", "", "", ""]]
        strings = self.equipSelStatsTable.strings
        colors = self.equipSelStatsTable.colors

        labelInd = [[0,0], [0,2], [1,0], [1,2], [2,0], [2,2]]
        valInd = [[0,1], [0,3], [1,1], [1,3], [2,1], [2,3]]

        curEquip = self.currentEquipList[self.equipListCursor + self.equipListCursorOffset]

        labels = []
        vals = []
        for stat in curEquip.attr:
            labels.append(g.ATTR_NAME[stat])
            vals.append(curEquip.attr[stat])

        for i in range (0, len(labels)):
            strings[labelInd[i][0]][labelInd[i][1]] = labels[i]
            strings[valInd[i][0]][valInd[i][1]] = str(vals[i])
            if vals[i] > 0:
                colors[valInd[i][0]][valInd[i][1]] = g.GREEN
            else:
                colors[valInd[i][0]][valInd[i][1]] = g.RED

    def init_equip_sel_res_table(self):
        topLeft = (48, 62)
        widths = [32, 18, 35, 18]
        heights = [11, 11, 11]
        strings = [["", "", "", ""], ["", "", "", ""], ["", "", "", ""]]
        aligns = ["right","right","right","right"]
        colors = [[g.GRAY, g.GRAY, g.GRAY, g.GRAY], [g.GRAY, g.GRAY, g.GRAY, g.GRAY], [g.GRAY, g.GRAY, g.GRAY, g.GRAY]]
        return Table(self.MC, topLeft, widths, heights, strings, aligns, colors)

    def update_equip_sel_res(self):
        self.equipSelResTable.strings = [["", "", "", ""], ["", "", "", ""], ["", "", "", ""]]
        strings = self.equipSelResTable.strings
        colors = self.equipSelResTable.colors

        labelInd = [[0,0], [0,2], [1,0], [1,2], [2,0], [2,2]]
        valInd = [[0,1], [0,3], [1,1], [1,3], [2,1], [2,3]]

        curEquip = self.currentEquipList[self.equipListCursor + self.equipListCursorOffset]

        labels = []
        vals = []
        for res in curEquip.resD:
            labels.append(g.DamageType.NAME[res])
            vals.append(math.trunc(curEquip.resD[res]*100))
        for res in curEquip.resS:
            labels.append(g.BattlerStatus.NAME[res])
            vals.append(math.trunc(curEquip.resS[res]*100))

        for i in range (0, len(labels)):
            strings[labelInd[i][0]][labelInd[i][1]] = labels[i]
            strings[valInd[i][0]][valInd[i][1]] = str(vals[i])
            if vals[i] > 0:
                colors[valInd[i][0]][valInd[i][1]] = g.GREEN
            else:
                colors[valInd[i][0]][valInd[i][1]] = g.RED

    def init_animagi_table(self):
        topLeft = (48, 20)
        widths = [80, 24]
        heights = [11, 11, 11, 11, 11]
        strings = [["",""], ["",""], ["",""], ["",""], ["",""]]
        aligns = ["left", "right"]
        colors = [[g.WHITE, g.GRAY], [g.WHITE, g.GRAY], [g.WHITE, g.GRAY], [g.WHITE, g.GRAY], [g.WHITE, g.GRAY]]
        return Table(self.MC, topLeft, widths, heights, strings, aligns, colors)

    def update_animagi_table(self):
        strings = self.animagiTable.strings
        for i in range(0, self.animagiTableLength):
            ii = i + self.animagiCursorOffset
            if ii < len(g.ANIMAGI):
                strings[i][0] = g.ANIMAGI[ii].name
                strings[i][1] = str(g.ANIMAGI[ii].level) + "/" + str(g.ANIMAGUS_MAX_LEVEL)
            else:
                strings[i][0] = ""
                strings[i][1] = ""

    def init_animagi_growth_table(self):
        topLeft = (48, 80)
        widths = [24, 24, 24, 24]
        heights = [11, 11, 11]
        strings = [["", "", "", ""], ["", "", "", ""], ["", "", "", ""]]

        strings[0][0] = g.ATTR_NAME['str']
        strings[1][0] = g.ATTR_NAME['end']
        strings[2][0] = g.ATTR_NAME['wis']
        strings[0][2] = g.ATTR_NAME['spr']
        strings[1][2] = g.ATTR_NAME['agi']
        strings[2][2] = g.ATTR_NAME['lck']

        aligns = ["right", "right", "right", "right"]
        colors = [[g.WHITE, g.GRAY, g.WHITE, g.GRAY], [g.WHITE, g.GRAY, g.WHITE, g.GRAY], [g.WHITE, g.GRAY, g.WHITE, g.GRAY]]
        return Table(self.MC, topLeft, widths, heights, strings, aligns, colors)

    def update_animagi_growth_table(self):
        strings = self.animagiGrowthTable.strings

        selIndex = self.animagiCursor + self.animagiCursorOffset
        if selIndex < len(g.ANIMAGI):
            curAnimagus = g.ANIMAGI[selIndex]

            text = ""
            if "str" in curAnimagus.growth:
                text = str(curAnimagus.growth['str']) + "-" + str(curAnimagus.growth['str'] + curAnimagus.level)
            else:
                text = "0-" + str(curAnimagus.level)
            strings[0][1] = text

            if "end" in curAnimagus.growth:
                text = str(curAnimagus.growth['end']) + "-" + str(curAnimagus.growth['end'] + curAnimagus.level)
            else:
                text = "0-" + str(curAnimagus.level)
            strings[1][1] = text

            if "wis" in curAnimagus.growth:
                text = str(curAnimagus.growth['wis']) + "-" + str(curAnimagus.growth['wis'] + curAnimagus.level)
            else:
                text = "0-" + str(curAnimagus.level)
            strings[2][1] = text

            if "spr" in curAnimagus.growth:
                text = str(curAnimagus.growth['spr']) + "-" + str(curAnimagus.growth['spr'] + curAnimagus.level)
            else:
                text = "0-" + str(curAnimagus.level)
            strings[0][3] = text

            if "agi" in curAnimagus.growth:
                text = str(curAnimagus.growth['agi']) + "-" + str(curAnimagus.growth['agi'] + curAnimagus.level)
            else:
                text = "0-" + str(curAnimagus.level)
            strings[1][3] = text

            if "lck" in curAnimagus.growth:
                text = str(curAnimagus.growth['lck']) + "-" + str(curAnimagus.growth['lck'] + curAnimagus.level)
            else:
                text = "0-" + str(curAnimagus.level)
            strings[2][3] = text

    def init_animagi_skills_table(self):
        topLeft = (48, 80)
        widths = [8, 80]
        heights = [11, 11, 11]
        strings = [["", ""], ["", ""], ["", ""]]
        aligns = ["right", "left"]
        colors = [[g.WHITE, g.WHITE], [g.WHITE, g.WHITE], [g.WHITE, g.WHITE]]
        return Table(self.MC, topLeft, widths, heights, strings, aligns, colors)

    def update_animagi_skills_table(self):
        strings = self.animagiSkillsTable.strings
        colors = self.animagiSkillsTable.colors
        strings[0][1] = ""
        strings[0][0] = ""
        strings[1][1] = ""
        strings[1][0] = ""
        strings[2][1] = ""
        strings[2][0] = ""

        selIndex = self.animagiCursor + self.animagiCursorOffset
        if selIndex < len(g.ANIMAGI):
            curAnimagus = g.ANIMAGI[selIndex]

            i = 0
            for skill in curAnimagus.skills:
                if skill.skillType != g.SkillType.NONE:
                    strings[i][0] = skill.icon
                if skill in curAnimagus.skillsTaught:
                    color = g.GRAY
                else:
                    if skill.skillType == g.SkillType.NONE or skill.skillType == self.currentHero.skillType:
                        color = g.WHITE
                    else:
                        color = g.RED
                strings[i][1] = skill.name
                colors[i][1] = color
                i += 1

    def init_stats_table(self):
        topLeft = (38, 74)
        widths = [30, 24, 36, 24]
        heights = [11, 11, 11, 11, 11, 11]
        strings = [["", "", "", ""], ["", "", "", ""], ["", "", "", ""], ["", "", "", ""], ["", "", "", ""], ["", "", "", ""]]
        strings[0][0] = g.ATTR_NAME['str']
        strings[1][0] = g.ATTR_NAME['end']
        strings[2][0] = g.ATTR_NAME['wis']
        strings[3][0] = g.ATTR_NAME['spr']
        strings[4][0] = g.ATTR_NAME['agi']
        strings[5][0] = g.ATTR_NAME['lck']
        strings[0][2] = g.ATTR_NAME['atk']
        strings[1][2] = g.ATTR_NAME['def']
        strings[2][2] = g.ATTR_NAME['matk']
        strings[3][2] = g.ATTR_NAME['mdef']
        strings[4][2] = g.ATTR_NAME['hit']
        strings[5][2] = g.ATTR_NAME['eva']
        aligns = ["right", "right", "right", "right"]
        colors = [[g.WHITE, g.GRAY, g.WHITE, g.GRAY], [g.WHITE, g.GRAY, g.WHITE, g.GRAY], [g.WHITE, g.GRAY, g.WHITE, g.GRAY], [g.WHITE, g.GRAY, g.WHITE, g.GRAY], [g.WHITE, g.GRAY, g.WHITE, g.GRAY], [g.WHITE, g.GRAY, g.WHITE, g.GRAY]]
        return Table(self.MC, topLeft, widths, heights, strings, aligns, colors)

    def update_stats_table(self):
        strings = self.statsTable.strings
        colors = self.statsTable.colors
        strings[0][1] = str(self.currentHero.attr['str'])
        strings[1][1] = str(self.currentHero.attr['end'])
        strings[2][1] = str(self.currentHero.attr['wis'])
        strings[3][1] = str(self.currentHero.attr['spr'])

        strings[4][1] = str(self.currentHero.attr['agi'])
        colors[4][1] = self.get_stat_color(self.currentHero.totalAgi, self.currentHero.attr['agi'])

        strings[5][1] = str(self.currentHero.attr['lck'])
        colors[5][1] = self.get_stat_color(self.currentHero.totalLck, self.currentHero.attr['lck'])

        strings[0][3] = str(self.currentHero.totalAtk)
        colors [0][3] = self.get_stat_color(self.currentHero.totalAtk, self.currentHero.baseAtk)

        strings[1][3] = str(self.currentHero.totalDef)
        colors[1][3] = self.get_stat_color(self.currentHero.totalDef, self.currentHero.baseDef)

        strings[2][3] = str(self.currentHero.totalMAtk)
        colors[2][3] = self.get_stat_color(self.currentHero.totalMAtk, self.currentHero.baseMAtk)

        strings[3][3] = str(self.currentHero.totalMDef)
        colors[3][3] = self.get_stat_color(self.currentHero.totalMDef, self.currentHero.baseMDef)

        strings[4][3] = str(self.currentHero.totalHit)
        colors[4][3] = self.get_stat_color(self.currentHero.totalHit, self.currentHero.baseHit)

        strings[5][3] = str(self.currentHero.totalEva)
        colors[5][3] = self.get_stat_color(self.currentHero.totalEva, self.currentHero.baseEva)

    def init_res_table(self):
        topLeft = (30, 20)
        widths = [48, 24, 26, 24]
        heights = [11, 11, 11, 11, 11, 11, 11, 11, 11]
        strings = [["", "", "", ""], ["", "", "", ""], ["", "", "", ""], ["", "", "", ""], ["", "", "", ""], ["", "", "", ""], ["", "", "", ""], ["", "", "", ""], ["", "", "", ""]]
        strings[0][0] = g.DamageType.NAME[g.DamageType.PHYS]
        strings[1][0] = g.DamageType.NAME[g.DamageType.FIRE]
        strings[2][0] = g.DamageType.NAME[g.DamageType.COLD]
        strings[3][0] = g.DamageType.NAME[g.DamageType.ELEC]
        strings[4][0] = g.DamageType.NAME[g.DamageType.EARTH]
        strings[5][0] = g.DamageType.NAME[g.DamageType.WIND]
        strings[6][0] = g.DamageType.NAME[g.DamageType.LIGHT]
        strings[7][0] = g.DamageType.NAME[g.DamageType.DARK]
        strings[8][0] = g.DamageType.NAME[g.DamageType.CURSE]
        strings[0][2] = g.BattlerStatus.NAME[g.BattlerStatus.POISON]
        strings[1][2] = g.BattlerStatus.NAME[g.BattlerStatus.SLEEP]
        strings[2][2] = g.BattlerStatus.NAME[g.BattlerStatus.PARALYZE]
        strings[3][2] = g.BattlerStatus.NAME[g.BattlerStatus.SILENCE]
        strings[4][2] = g.BattlerStatus.NAME[g.BattlerStatus.STUN]
        strings[5][2] = g.BattlerStatus.NAME[g.BattlerStatus.DEATH]
        aligns = ["right", "right", "right", "right"]
        colors = [[g.WHITE, g.GRAY, g.WHITE, g.GRAY], [g.WHITE, g.GRAY, g.WHITE, g.GRAY], [g.WHITE, g.GRAY, g.WHITE, g.GRAY], [g.WHITE, g.GRAY, g.WHITE, g.GRAY], [g.WHITE, g.GRAY, g.WHITE, g.GRAY], [g.WHITE, g.GRAY, g.WHITE, g.GRAY], [g.WHITE, g.GRAY, g.WHITE, g.GRAY], [g.WHITE, g.GRAY, g.WHITE, g.GRAY], [g.WHITE, g.GRAY, g.WHITE, g.GRAY]]
        return Table(self.MC, topLeft, widths, heights, strings, aligns, colors)

    def update_res_table(self):
        strings = self.resTable.strings
        colors = self.resTable.colors

        strings[0][1] = str(math.trunc(self.currentHero.total_resD(g.DamageType.PHYS)*100))
        colors[0][1] = self.get_stat_color(self.currentHero.total_resD(g.DamageType.PHYS), self.currentHero.resD[g.DamageType.PHYS])

        strings[1][1] = str(math.trunc(self.currentHero.total_resD(g.DamageType.FIRE)*100))
        colors[1][1] = self.get_stat_color(self.currentHero.total_resD(g.DamageType.FIRE), self.currentHero.resD[g.DamageType.FIRE])

        strings[2][1] = str(math.trunc(self.currentHero.total_resD(g.DamageType.COLD)*100))
        colors[2][1] = self.get_stat_color(self.currentHero.total_resD(g.DamageType.COLD), self.currentHero.resD[g.DamageType.COLD])

        strings[3][1] = str(math.trunc(self.currentHero.total_resD(g.DamageType.ELEC)*100))
        colors[3][1] = self.get_stat_color(self.currentHero.total_resD(g.DamageType.ELEC), self.currentHero.resD[g.DamageType.ELEC])

        strings[4][1] = str(math.trunc(self.currentHero.total_resD(g.DamageType.EARTH)*100))
        colors[4][1] = self.get_stat_color(self.currentHero.total_resD(g.DamageType.EARTH), self.currentHero.resD[g.DamageType.EARTH])

        strings[5][1] = str(math.trunc(self.currentHero.total_resD(g.DamageType.WIND)*100))
        colors[5][1] = self.get_stat_color(self.currentHero.total_resD(g.DamageType.WIND), self.currentHero.resD[g.DamageType.WIND])

        strings[6][1] = str(math.trunc(self.currentHero.total_resD(g.DamageType.LIGHT)*100))
        colors[6][1] = self.get_stat_color(self.currentHero.total_resD(g.DamageType.LIGHT), self.currentHero.resD[g.DamageType.LIGHT])

        strings[7][1] = str(math.trunc(self.currentHero.total_resD(g.DamageType.DARK) * 100))
        colors[7][1] = self.get_stat_color(self.currentHero.total_resD(g.DamageType.DARK), self.currentHero.resD[g.DamageType.DARK])

        strings[8][1] = str(math.trunc(self.currentHero.total_resD(g.DamageType.CURSE) * 100))
        colors[8][1] = self.get_stat_color(self.currentHero.total_resD(g.DamageType.CURSE), self.currentHero.resD[g.DamageType.CURSE])

        strings[0][3] = str(math.trunc(self.currentHero.total_resS(g.BattlerStatus.POISON) * 100))
        colors[0][3] = self.get_stat_color(self.currentHero.total_resS(g.BattlerStatus.POISON), self.currentHero.resS[g.BattlerStatus.POISON])

        strings[1][3] = str(math.trunc(self.currentHero.total_resS(g.BattlerStatus.SLEEP) * 100))
        colors[1][3] = self.get_stat_color(self.currentHero.total_resS(g.BattlerStatus.SLEEP), self.currentHero.resS[g.BattlerStatus.SLEEP])

        strings[2][3] = str(math.trunc(self.currentHero.total_resS(g.BattlerStatus.PARALYZE) * 100))
        colors[2][3] = self.get_stat_color(self.currentHero.total_resS(g.BattlerStatus.PARALYZE), self.currentHero.resS[g.BattlerStatus.PARALYZE])

        strings[3][3] = str(math.trunc(self.currentHero.total_resS(g.BattlerStatus.SILENCE) * 100))
        colors[3][3] = self.get_stat_color(self.currentHero.total_resS(g.BattlerStatus.SILENCE), self.currentHero.resS[g.BattlerStatus.SILENCE])

        strings[4][3] = str(math.trunc(self.currentHero.total_resS(g.BattlerStatus.STUN) * 100))
        colors[4][3] = self.get_stat_color(self.currentHero.total_resS(g.BattlerStatus.STUN), self.currentHero.resS[g.BattlerStatus.STUN])

        strings[5][3] = str(math.trunc(self.currentHero.total_resS(g.BattlerStatus.DEATH) * 100))
        colors[5][3] = self.get_stat_color(self.currentHero.total_resS(g.BattlerStatus.DEATH), self.currentHero.resS[g.BattlerStatus.DEATH])

    def create_equip_list(self):
        self.currentEquipList = []
        if self.MC.menuState == g.MenuState.EQUIP_ACC:
            for item in g.INVENTORY:
                if item[0].itemType == g.ItemType.ACC:
                    self.currentEquipList.append(item[0])
        elif self.MC.menuState == g.MenuState.EQUIP_WEAPON:
            for item in g.INVENTORY:
                if item[0].itemType == self.currentHero.weaponType:
                    self.currentEquipList.append(item[0])

    def open_item_options_menu(self):
        self.render_item_options(self)

    def open_item_menu(self):
        self.update_item_table()

    def open_equip_menu(self):
        self.update_equip_slot_table()
        self.update_equip_list_table()

    def open_skill_menu(self):
        self.update_skill_table()

    def open_animagi_menu(self):
        self.update_animagi_table()
        self.update_animagi_growth_table()
        self.update_animagi_skills_table()

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

        selection = self.process_input(0, self.commandTableLength)
        if selection > -1:
            if selection == 0:
                self.selectedThing = g.MenuState.ITEM_OPTIONS
            elif selection == 1:
                self.selectedThing = g.MenuState.SKILL_HERO
                self.restore_cursor()
            elif selection == 2:
                self.selectedThing = g.MenuState.EQUIP_HERO
                self.cursorIndex = 0
            elif selection == 3:
                self.selectedThing = g.MenuState.ANIMAGI_HERO
                self.cursorIndex = 0
            elif selection == 4:
                self.selectedThing = g.MenuState.STATUS_HERO
                self.cursorIndex = 0
            elif selection == 5:
                self.selectedThing = g.MenuState.EXIT

    def process_get_skill_hero(self):
        self.skillHeroCursor = self.cursorIndex
        selection = self.process_input(0, len(g.partyList) - 1)
        if selection > -1:
            self.currentHero = g.partyList[selection]
            self.MC.change_state(g.MenuState.SKILL)
            self.cursorIndex = 0

    def process_get_equip_hero(self):
        self.equipHeroCursor = self.cursorIndex
        selection = self.process_input(0, len(g.partyList) - 1)
        if selection > -1:
            self.currentHero = g.partyList[selection]
            self.MC.change_state(g.MenuState.EQUIP)
            self.cursorIndex = 0

    def process_get_animagi_hero(self):
        self.animagiHeroCursor = self.cursorIndex
        selection = self.process_input(0, len(g.partyList) - 1)
        if selection > -1:
            self.currentHero = g.partyList[selection]
            self.MC.change_state(g.MenuState.ANIMAGI)
            self.open_animagi_menu()
            self.cursorIndex = 0

    def process_get_status_hero(self):
        self.statusHeroCursor = self.cursorIndex
        selection = self.process_input(0, len(g.partyList) - 1)
        if selection > -1:
            self.currentHero = g.partyList[selection]
            self.MC.change_state(g.MenuState.STATUS)

    def process_get_status(self):
        self.statusHeroCursor = self.cursorIndex
        self.process_input(0, len(g.partyList) - 1)

    def process_get_item_options(self):
        self.itemOptionsCursor = self.cursorIndex
        selection = self.process_input(0, self.itemOptionsTableLength)
        if selection > -1:
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

    def process_get_item(self):
        self.itemCursor = self.cursorIndex

        if self.itemCursor + self.itemCursorOffset != self.itemCursorPrev + self.itemCursorOffsetPrev:
            self.update_item_table()

        self.itemCursorPrev = self.itemCursor
        self.itemCursorOffsetPrev = self.itemCursorOffset

        selection = self.process_input(0, self.itemTableLength)
        if selection > -1:
            itemIndex = selection + self.itemCursorOffset
            if g.INVENTORY[itemIndex][0].usableField:
                self.currentItem = g.INVENTORY[itemIndex][0]
                self.currentItem.useAction.start(self.MC)

    def process_get_item_organize(self):
        self.itemCursor = self.cursorIndex

        if self.itemCursor + self.itemCursorOffset != self.itemCursorPrev + self.itemCursorOffsetPrev:
            self.update_item_table()

        self.itemCursorPrev = self.itemCursor
        self.itemCursorOffsetPrev = self.itemCursorOffset

        selection = self.process_input(0, self.itemTableLength)
        if selection > -1:
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

    def process_get_equip_slot(self):
        self.equipCursor = self.cursorIndex
        selection = self.process_input(0, self.equipSlotTableLength-1)
        if selection > -1:
            if selection == 0:
                self.MC.change_state(g.MenuState.EQUIP_WEAPON)
                self.currentEquipSlot = "wpn"
            elif selection == 1:
                self.MC.change_state(g.MenuState.EQUIP_ACC)
                self.currentEquipSlot = "acc1"
            elif selection == 2:
                self.MC.change_state(g.MenuState.EQUIP_ACC)
                self.currentEquipSlot = "acc2"
            self.equipInfoPage = 0
            self.create_equip_list()
            self.equipListCursor = 0
            self.equipListCursorOffset = 0
            self.cursorIndex = 0

    def process_get_equip(self):
        if len(self.currentEquipList) == 0:
            self.MC.prev_state()
            self.restore_cursor()
        self.equipListCursor = self.cursorIndex
        selection = self.process_input(0, self.equipListTableLength)
        if selection > -1:
            itemIndex = selection + self.equipListCursorOffset
            inv.equip(self.currentHero, self.currentEquipList[itemIndex].name, self.currentEquipSlot)
            self.MC.prev_state()
            self.restore_cursor()

    def process_get_skill(self):
        self.skillCursor = self.cursorIndex
        selection = self.process_input(0, self.skillTableLength)
        if selection > -1:
            skillIndex = selection + self.skillCursorOffset
            if self.currentHero.skills[skillIndex].usableField:
                if db.Skill.check_cost(self.currentHero,  self.currentHero.skills[skillIndex]):
                    self.currentSkill = self.currentHero.skills[skillIndex]
                    self.currentSkill.useAction.start(self.MC, self.currentHero)

    def process_get_animagi(self):
        self.animagiCursor = self.cursorIndex

        if self.animagiCursor + self.animagiCursorOffset != self.animagiCursorPrev + self.animagiCursorOffsetPrev:
            self.update_animagi_table()
            self.update_animagi_growth_table()
            self.update_animagi_skills_table()

        self.animagiCursorPrev = self.animagiCursor
        self.animagiCursorOffsetPrev = self.animagiCursorOffset

        selection = self.process_input(0, self.animagiTableLength)
        if selection > -1:
            selIndex = self.animagiCursor + self.animagiCursorOffset
            if (anmr.can_level(g.ANIMAGI[selIndex], self.currentHero)):
                self.MC.change_state(g.MenuState.ANIMAGI_CONFIRM)
                self.cursorIndex = 1

    def process_get_animagi_confirm(self):
        self.animagiConfirmCursor = self.cursorIndex
        selection = self.process_input(0, 1)
        if selection > -1:
            if selection == 0:
                selIndex = self.animagiCursor + self.animagiCursorOffset
                anmr.level_up(g.ANIMAGI[selIndex], self.currentHero)
                self.update_animagi_table()
                self.update_animagi_growth_table()
                self.update_animagi_skills_table()
                self.MC.prev_state()
                self.restore_cursor()
            else:
                self.MC.prev_state()
                self.restore_cursor()

    def process_get_target(self):
        if self.validTargets:
            selection = self.process_input(0, len(self.validTargets)-1)
            if selection > -1:
                self.selectedThing = self.validTargets[selection]
                self.targetCursor = self.cursorIndex
        else:
            self.helpLabel = ""
            self.MC.prev_state()
            self.restore_cursor()

    def render_target_cursor(self):
        curTarget = self.validTargets[self.cursorIndex]
        targetIndex = g.partyList.index(curTarget)
        self.MC.controller.viewSurf.blit(self.targetCursorImage, utility.add_tuple(self.portraitAnchor[targetIndex], self.targetCursorPosOffset))

    def render_skill_hero_cursor(self):
        self.MC.controller.viewSurf.blit(self.cursorHeroImage, utility.add_tuple(self.portraitAnchor[self.skillHeroCursor], self.skillHeroCursorPosOffset))

    def render_equip_hero_cursor(self):
        self.MC.controller.viewSurf.blit(self.cursorHeroImage, utility.add_tuple(self.portraitAnchor[self.equipHeroCursor], self.skillHeroCursorPosOffset))

    def render_animagi_hero_cursor(self):
        self.MC.controller.viewSurf.blit(self.cursorHeroImage, utility.add_tuple(self.portraitAnchor[self.animagiHeroCursor], self.skillHeroCursorPosOffset))

    def render_status_hero_cursor(self):
        self.MC.controller.viewSurf.blit(self.cursorHeroImage, utility.add_tuple(self.portraitAnchor[self.statusHeroCursor], self.skillHeroCursorPosOffset))

    def render_bar(self, pos, curVal, maxVal, color):
        percent = curVal / maxVal
        width = math.floor(97 * percent)
        rect = pygame.Rect(pos, (width, 4))

        pygame.draw.rect(self.MC.controller.viewSurf, color, rect, 0)

    def render_main_window(self):
        self.MC.controller.viewSurf.blit(self.mainPanel, (0, 0))

        #Draw basic info for each hero
        index = 0
        for hero in g.partyList:
            offset = self.mainAnchor[index]
            offset = utility.add_tuple(offset, (4, 0))
            self.MC.controller.viewSurf.blit(hero.icon, offset)

            offset = utility.add_tuple(offset, (25, -8))
            self.MC.controller.TM.draw_text(str(hero.attr['name']), offset, g.WHITE)
            self.MC.controller.TM.draw_text("Lv " + str(hero.attr['lvl']), utility.add_tuple(offset, (0,13)), g.WHITE)
            self.render_meter(hero.skillType, utility.add_tuple(offset, (71,19)))

            self.render_bar(utility.add_tuple(self.mainAnchor[index], (2, 31)), hero.attr['hp'], hero.totalMaxHP, g.HP_RED)
            offset = utility.add_tuple(offset, (69, 28))
            self.MC.controller.TM.draw_text_shaded_ralign(str(hero.totalMaxHP), offset, g.WHITE)
            self.MC.controller.TM.draw_text_shaded_ralign("/", utility.add_tuple(offset, (-29, 0)), g.WHITE)
            self.MC.controller.TM.draw_text_shaded_ralign(str(hero.attr['hp']), utility.add_tuple(offset, (-34, 0)), g.WHITE)

            self.render_bar(utility.add_tuple(self.mainAnchor[index], (2, 47)), hero.attr['sp'], hero.totalMaxSP, g.SP_BLUE)
            offset = utility.add_tuple(offset, (0, 16))
            self.MC.controller.TM.draw_text_shaded_ralign(str(hero.totalMaxSP), offset, g.WHITE)
            self.MC.controller.TM.draw_text_shaded_ralign("/", utility.add_tuple(offset, (-29, 0)), g.WHITE)
            self.MC.controller.TM.draw_text_shaded_ralign(str(hero.attr['sp']), utility.add_tuple(offset, (-34, 0)), g.WHITE)


            index += 1

    def render_animagi_window(self):
        self.MC.controller.viewSurf.blit(self.animagiPanel, (0,0))
        selIndex = self.animagiCursor + self.animagiCursorOffset

        if g.ANIMAGI:
            self.MC.controller.TM.draw_text_ralign(str(1 + selIndex) + "/" + str(len(g.ANIMAGI)), self.equipIndexAnchor, g.WHITE)

           # self.update_animagi_table_strings()
            self.animagiTable.render(self.animagiCursor)

            #draw animagus growth page
            if self.animagiPage == 0:
                self.MC.controller.TM.draw_text_centered("Growth", self.animagiPageAnchor, g.WHITE)

                #self.update_animagi_growth_table_strings()
                self.animagiGrowthTable.render()

            #draw animagus skill page
            elif self.animagiPage == 1:
                self.MC.controller.TM.draw_text_centered("Skills", self.animagiPageAnchor, g.WHITE)

                #self.update_animagi_skills_strings()
                self.animagiSkillsTable.render()

            #always draw level up info
            self.MC.controller.TM.draw_text("Anima", self.animagiStatsAnchor[0], g.WHITE)
            if self.currentHero.exp >= g.ANIMAGI[selIndex].levelUpAt * self.currentHero.attr['lvl']:
                color = g.GREEN
            else:
                color = g.RED
            self.MC.controller.TM.draw_text_ralign(str(self.currentHero.exp), utility.add_tuple(self.animagiStatsAnchor[0], (108, 0)), color)

            if g.ANIMAGI[selIndex].level < g.ANIMAGUS_MAX_LEVEL:
                self.MC.controller.TM.draw_text("To Next", self.animagiStatsAnchor[1], g.WHITE)
                self.MC.controller.TM.draw_text_ralign(str(g.ANIMAGI[selIndex].levelUpAt * self.currentHero.attr['lvl']), utility.add_tuple(self.animagiStatsAnchor[1], (108, 0)), g.GRAY)
            else:
                self.MC.controller.TM.draw_text_ralign("Max Level", utility.add_tuple(self.animagiStatsAnchor[1], (108, 0)), g.GRAY)

            #draw confirm level up
            if self.MC.menuState == g.MenuState.ANIMAGI_CONFIRM:
                self.MC.controller.viewSurf.blit(self.itemOptionsPanel, (0, 0))
                self.MC.controller.TM.draw_text("Level Up?", self.itemOptionsAnchor[0], g.WHITE)
                self.MC.controller.TM.draw_text("Confirm", self.itemOptionsAnchor[1], g.GRAY)
                self.MC.controller.TM.draw_text("Cancel", self.itemOptionsAnchor[2], g.GRAY)
                self.MC.controller.viewSurf.blit(self.cursorImage, utility.add_tuple(self.itemOptionsAnchor[self.animagiConfirmCursor+1], self.itemOptionsCursorPosOffset))

        else:
            self.MC.controller.TM.draw_text("No Animagi", self.animagiListAnchor[0], g.WHITE)

    def render_equip_window(self):
        self.MC.controller.viewSurf.blit(self.equipPanel, (0,0))

        if self.MC.menuState == g.MenuState.EQUIP_WEAPON or self.MC.menuState == g.MenuState.EQUIP_ACC:
            selIndex = self.equipListCursor + self.equipListCursorOffset
            self.MC.controller.TM.draw_text_ralign(str(1 + selIndex) + "/" + str(len(self.currentEquipList)), self.equipIndexAnchor, g.WHITE)

            index = 0
            if selIndex < len(self.currentEquipList):

                self.update_equip_list_table()
                self.equipListTable.render(self.equipListCursor)

                #Always show names of current and selected equip
                if self.currentHero.equip[self.currentEquipSlot].name != "":
                    self.MC.controller.TM.draw_text(self.currentHero.equip[self.currentEquipSlot].name, self.equipCurAnchor, g.WHITE)

                self.MC.controller.TM.draw_text(self.currentEquipList[selIndex].name, self.equipSelAnchor, g.WHITE)

                #Show stats of current and selected equip
                if self.equipInfoPage == 0:
                    #current
                    if self.currentHero.equip[self.currentEquipSlot].name != "":
                        self.update_equip_cur_stats()
                        self.equipCurStatsTable.render()

                    #selected
                    self.update_equip_sel_stats()
                    self.equipSelStatsTable.render()

                #Show resistances
                elif self.equipInfoPage == 1:
                    #current
                    if self.currentHero.equip[self.currentEquipSlot].name != "":
                        self.update_equip_cur_res()
                        self.equipCurResTable.render()

                    #selected
                    self.update_equip_sel_res()
                    self.equipSelResTable.render()

                #Show descriptions
                elif self.equipInfoPage == 2:
                    # current
                    if self.currentHero.equip[self.currentEquipSlot].desc != "":
                        self.MC.controller.TM.draw_text_f(self.currentHero.equip[self.currentEquipSlot].desc, utility.add_tuple(self.equipCurAnchor, (0,10)), g.GRAY, 108)
                    # selected
                    self.MC.controller.TM.draw_text_f(self.currentEquipList[selIndex].desc, utility.add_tuple(self.equipSelAnchor, (0,10)), g.GRAY, 108)


        else:
            self.update_equip_slot_table()
            self.equipSlotTable.render(self.equipCursor)

    def render_item_options(self):
        self.MC.controller.viewSurf.blit(self.itemOptionsPanel, (0,0))
        self.itemOptionsTable.render(self.itemOptionsCursor)

    def render_skill_window(self):

        #Move UI over when targeting
        if self.MC.menuState == g.MenuState.TARGET_SKILL:
            globalOffset = (54, 0)
            helpWidth = 60
        else:
            globalOffset = (0, 0)
            helpWidth = 108

        #Draw panel and headers
        self.MC.controller.viewSurf.blit(self.skillPanel, globalOffset)
        self.MC.controller.TM.draw_text("SP: ", utility.add_tuple(self.skillHeroAnchor, globalOffset), g.WHITE)
        self.MC.controller.TM.draw_text_ralign(str(self.currentHero.attr['sp']) + "/" + str(self.currentHero.baseMaxSP), utility.add_tuple(self.skillHeroAnchor, utility.add_tuple(globalOffset, (71, 0))), g.WHITE)
        self.MC.controller.TM.draw_text_ralign(str(1 + self.skillCursor + self.skillCursorOffset) + "/" + str(len(self.currentHero.skills)), utility.add_tuple(self.skillIndexAnchor, globalOffset), g.WHITE)

        #Draw table
        self.update_skill_table()
        self.skillTable.render(self.skillCursor, globalOffset)

        #Draw current skill description
        if self.skillCursor + self.skillCursorOffset < len(self.currentHero.skills):
            curSkill = self.currentHero.skills[self.skillCursor + self.skillCursorOffset]
            if curSkill.desc != "":
                self.MC.controller.TM.draw_text_f(curSkill.desc, utility.add_tuple(self.skillDescAnchor, globalOffset), g.WHITE, helpWidth)

    def render_item_window(self):
        selIndex = self.currentIndex - self.itemCursorOffset

        #Move everything over when targeting
        if self.MC.menuState == g.MenuState.TARGET_ITEM:
            globalOffset = (54, 0)
            helpWidth = 60
        else:
            globalOffset = (0, 0)
            helpWidth = 108

        #Draw panel and index
        self.MC.controller.viewSurf.blit(self.itemPanel, globalOffset)
        self.MC.controller.TM.draw_text_ralign(str(1 + self.itemCursor + self.itemCursorOffset) + "/" + str( g.INVENTORY_MAX_SLOTS), utility.add_tuple(self.itemIndexAnchor, globalOffset), g.WHITE)

        #Draw table
        self.update_item_table()
        if (self.MC.menuState == g.MenuState.ITEM_OPTIONS):
            cursor = -1
        else:
            cursor = self.itemCursor
        self.itemTable.render(cursor, globalOffset)

        #Draw arrange secondary cursor
        if self.MC.menuState != g.MenuState.ITEM_OPTIONS:
            if self.MC.menuState == g.MenuState.ITEM_ORGANIZE and selIndex >= 0 and selIndex <= 8:
                self.MC.controller.viewSurf.blit(self.cursorSelImage, utility.add_tuple(self.itemAnchor[selIndex], utility.add_tuple(globalOffset, self.itemCursorPosOffset)))

        #Draw current item description
        if selIndex < g.INVENTORY_MAX_SLOTS:
            curItem = g.INVENTORY[selIndex][0]
            if curItem.desc != "":
                parsedStr = self.MC.controller.TM.parse_string(curItem.desc, helpWidth)[0]

                curOffset = utility.add_tuple(globalOffset, (0, 0))
                lineOffset = (0, 11)

                index = 0
                for line in range(0, len(parsedStr)):
                    self.MC.controller.TM.draw_text(parsedStr[index], utility.add_tuple(self.itemDescAnchor, curOffset), g.WHITE)
                    curOffset = utility.add_tuple(curOffset, lineOffset)
                    index += 1

    def render_stats_window(self):
        self.currentHero = g.partyList[self.cursorIndex]
        #self.MC.controller.viewSurf.blit(self.cursorHeroImage, utility.add_tuple(self.portraitAnchor[self.cursorIndex], self.skillHeroCursorPosOffset))

        if (self.statusPage == 0):
            self.MC.controller.viewSurf.blit(self.statsPanel, (0,0))

            self.MC.controller.TM.draw_text(self.currentHero.attr['name'] + ", " + self.currentHero.attr['title'], self.statsAnchor[0], g.GRAY)

            self.MC.controller.TM.draw_text_ralign("HP", utility.add_tuple(self.statsAnchor[1], (-68, 0)), g.WHITE)
            color = self.get_stat_color(self.currentHero.totalMaxHP, self.currentHero.baseMaxHP)
            self.MC.controller.TM.draw_text_ralign(str(self.currentHero.totalMaxHP), self.statsAnchor[1], color)
            self.MC.controller.TM.draw_text_ralign("/", utility.add_tuple(self.statsAnchor[1], (-30, 0)), g.WHITE)
            self.MC.controller.TM.draw_text_ralign(str(self.currentHero.attr['hp']), utility.add_tuple(self.statsAnchor[1], (-34, 0)), g.GRAY)

            self.MC.controller.TM.draw_text_ralign("SP", utility.add_tuple(self.statsAnchor[2], (-68, 0)), g.WHITE)
            color = self.get_stat_color(self.currentHero.totalMaxSP, self.currentHero.baseMaxSP)
            self.MC.controller.TM.draw_text_ralign(str(self.currentHero.totalMaxSP), self.statsAnchor[2], color)
            self.MC.controller.TM.draw_text_ralign("/", utility.add_tuple(self.statsAnchor[2], (-30, 0)), g.WHITE)
            self.MC.controller.TM.draw_text_ralign(str(self.currentHero.attr['sp']), utility.add_tuple(self.statsAnchor[2], (-34, 0)), g.GRAY)

            self.MC.controller.TM.draw_text_ralign(g.SkillType.NAME[self.currentHero.skillType], utility.add_tuple(self.statsAnchor[2], (-68, 10)), g.GRAY)
            self.render_meter(self.currentHero.skillType, utility.add_tuple(self.statsAnchor[2], (-34, 10)))

            self.MC.controller.TM.draw_text_ralign("Anima", utility.add_tuple(self.statsAnchor[2], (-68, 20)), g.WHITE)
            self.MC.controller.TM.draw_text_ralign(str(self.currentHero.exp), utility.add_tuple(self.statsAnchor[2], (0, 20)), g.GRAY)

            self.update_stats_table()
            self.statsTable.render()

        elif (self.statusPage == 1):
            self.MC.controller.viewSurf.blit(self.resPanel, (0, 0))

            self.update_res_table()
            self.resTable.render()


        self.MC.controller.TM.draw_text_centered(str(self.statusPage + 1) + "/" + str(self.statusPages), self.statusPageAnchor, g.WHITE)

    def get_stat_color(self, total, base):
        if total > base:
            return g.GREEN
        elif base > total:
            return g.RED
        else:
            return g.GRAY

    def render_meter(self, skillType, pos):
        pos = utility.add_tuple(pos, self.meterIconOffset)
        offset = (5, 0)
        if skillType == g.SkillType.BLOOD:
            iconImg = self.iconBlood
        elif skillType == g.SkillType.MOON:
            iconImg = self.iconMoon
        if skillType != g.SkillType.MUSIC:
            for i in range (0, g.meter[skillType]):
                self.MC.controller.viewSurf.blit(iconImg, pos)
                pos = utility.add_tuple(pos, offset)
        else:
            for i in g.meter[skillType]:
                self.MC.controller.viewSurf.blit(self.iconNotes[i], utility.add_tuple(pos, (0,1)))
                pos = utility.add_tuple(pos, offset)

    def render_command_window(self):
        #self.MC.controller.viewSurf.blit(self.commandPanel, (0, 0))
        self.commandTable.render(self.commandCursor)

    def render_info_window(self):
        #self.MC.controller.viewSurf.blit(self.infoPanel, (0, 0))
        self.MC.controller.TM.draw_text("GP", self.infoAnchor, g.WHITE)
        self.MC.controller.TM.draw_text_ralign(str(g.GP), utility.add_tuple(self.infoAnchor, (72, 11)), g.WHITE)
        self.MC.controller.TM.draw_text("Time", utility.add_tuple(self.infoAnchor, (0, 22)), g.WHITE)
        self.MC.controller.TM.draw_text_ralign(g.playTimeSecText, utility.add_tuple(self.infoAnchor, (72, 33)), g.WHITE)
        self.MC.controller.TM.draw_text_ralign(":", utility.add_tuple(self.infoAnchor, (59, 33)), g.WHITE)
        self.MC.controller.TM.draw_text_ralign(g.playTimeMinText, utility.add_tuple(self.infoAnchor, (57, 33)), g.WHITE)
        self.MC.controller.TM.draw_text_ralign(":", utility.add_tuple(self.infoAnchor, (44, 33)), g.WHITE)
        self.MC.controller.TM.draw_text_ralign(g.playTimeHourText, utility.add_tuple(self.infoAnchor, (42, 33)), g.WHITE)

    def restore_cursor(self):
        if self.MC.menuState == g.MenuState.MENU:
            self.cursorIndex = self.commandCursor
        elif self.MC.menuState == g.MenuState.ITEM or self.MC.menuState == g.MenuState.ITEM_ORGANIZE:
            self.cursorIndex = self.itemCursor
        elif self.MC.menuState == g.MenuState.ITEM_OPTIONS:
            self.cursorIndex = self.itemOptionsCursor
        elif self.MC.menuState == g.MenuState.SKILL_HERO:
            self.cursorIndex = self.skillHeroCursor
        elif self.MC.menuState == g.MenuState.SKILL:
            self.cursorIndex = self.skillCursor
        elif self.MC.menuState == g.MenuState.EQUIP:
            self.cursorIndex = self.equipCursor
        elif self.MC.menuState == g.MenuState.EQUIP_HERO:
            self.cursorIndex = self.equipHeroCursor
        elif self.MC.menuState == g.MenuState.ANIMAGI_HERO:
            self.cursorIndex = self.animagiHeroCursor
        elif self.MC.menuState == g.MenuState.ANIMAGI:
            self.cursorIndex = self.animagiCursor

        self.currentIndex = -1

    def process_input(self, cMin, cMax):
        dt = self.MC.controller.clock.get_time()
        if (g.cursorTimer >= 0):
            g.cursorTimer -= dt
        if (g.confirmTimer >= 0):
            g.confirmTimer -= dt

        if self.MC.controller.eventKeys[g.keyDown]:
            if g.cursorTimer < 0:
                g.cursorTimer = g.CURSOR_DELAY
                self.cursorIndex += 1
        elif self.MC.controller.eventKeys[g.keyUp]:
            if g.cursorTimer < 0:
                g.cursorTimer = g.CURSOR_DELAY
                self.cursorIndex -= 1
        elif self.MC.controller.eventKeys[g.keyLeft]:
            if g.cursorTimer < 0:
                g.cursorTimer = g.CURSOR_DELAY
                if self.MC.menuState == g.MenuState.ITEM or self.MC.menuState == g.MenuState.ITEM_ORGANIZE:
                    if self.itemCursorOffset - cMax > 0:
                        self.itemCursorOffset -= cMax
                    elif self.itemCursorOffset == 0:
                        self.itemCursorOffset = g.INVENTORY_MAX_SLOTS - cMax
                    else:
                        self.itemCursorOffset = 0
                elif self.MC.menuState == g.MenuState.SKILL:
                    if self.skillHeroCursor > 0:
                        self.skillHeroCursor -= 1
                    else:
                        self.skillHeroCursor = len(g.partyList) - 1
                    self.currentHero = g.partyList[self.skillHeroCursor]
                    self.cursorIndex = 0
                    self.skillCursorOffset = 0
                elif self.MC.menuState == g.MenuState.EQUIP:
                    if self.equipHeroCursor > 0:
                        self.equipHeroCursor -= 1
                    else:
                        self.equipHeroCursor = len(g.partyList) - 1
                    self.currentHero = g.partyList[self.equipHeroCursor]
                elif self.MC.menuState == g.MenuState.EQUIP_WEAPON or self.MC.menuState == g.MenuState.EQUIP_ACC:
                    if self.equipInfoPage <= 0:
                        self.equipInfoPage = self.equipInfoPages-1
                    else:
                        self.equipInfoPage -= 1
                elif self.MC.menuState == g.MenuState.STATUS:
                    if self.statusPage <= 0:
                        self.statusPage = self.statusPages-1
                    else:
                        self.statusPage -= 1
                elif self.MC.menuState == g.MenuState.ANIMAGI:
                    if self.animagiPage <= 0:
                        self.animagiPage = self.animagiPages-1
                    else:
                        self.animagiPage -= 1
        elif self.MC.controller.eventKeys[g.keyRight]:
            if g.cursorTimer < 0:
                g.cursorTimer = g.CURSOR_DELAY
                if self.MC.menuState == g.MenuState.ITEM or self.MC.menuState == g.MenuState.ITEM_ORGANIZE:
                    if self.itemCursorOffset + cMax < g.INVENTORY_MAX_SLOTS:
                        self.itemCursorOffset += cMax
                    elif self.itemCursorOffset == g.INVENTORY_MAX_SLOTS - cMax:
                        self.itemCursorOffset = 0
                    else:
                        self.itemCursorOffset = g.INVENTORY_MAX_SLOTS - cMax
                elif self.MC.menuState == g.MenuState.SKILL:
                    if self.skillHeroCursor < len(g.partyList)-1:
                        self.skillHeroCursor += 1
                    else:
                        self.skillHeroCursor = 0
                    self.currentHero = g.partyList[self.skillHeroCursor]
                    self.cursorIndex = 0
                    self.skillCursorOffset = 0
                elif self.MC.menuState == g.MenuState.EQUIP:
                    if self.equipHeroCursor < len(g.partyList)-1:
                        self.equipHeroCursor += 1
                    else:
                        self.equipHeroCursor = 0
                    self.currentHero = g.partyList[self.equipHeroCursor]
                elif self.MC.menuState == g.MenuState.EQUIP_WEAPON or self.MC.menuState == g.MenuState.EQUIP_ACC:
                    if self.equipInfoPage >= self.equipInfoPages-1:
                        self.equipInfoPage = 0
                    else:
                        self.equipInfoPage += 1
                elif self.MC.menuState == g.MenuState.STATUS:
                    if self.statusPage >= self.statusPages-1:
                        self.statusPage = 0
                    else:
                        self.statusPage += 1
                elif self.MC.menuState == g.MenuState.ANIMAGI:
                    if self.animagiPage >= self.animagiPages-1:
                        self.animagiPage = 0
                    else:
                        self.animagiPage += 1

        elif self.MC.controller.eventKeys[g.keyConfirm]:
            if g.confirmTimer < 0:
                g.confirmTimer = g.CONFIRM_DELAY
                self.helpLabel = ""
                return self.cursorIndex
        elif self.MC.controller.eventKeys[g.keyCancel]:
            if g.confirmTimer < 0:
                g.confirmTimer = g.CONFIRM_DELAY
                if self.MC.menuState != g.MenuState.MENU:
                    self.MC.prev_state()
                    self.restore_cursor()
                    return -1 #return here to prevent the cursor from limiting prematurely
                else:
                    self.MC.change_state(g.MenuState.EXIT)
                    return -1
        elif self.MC.controller.eventKeys[g.keyMenu]:
            if g.confirmTimer < 0:
                g.confirmTimer = g.CONFIRM_DELAY
                if self.MC.menuState == g.MenuState.EQUIP:
                    if self.cursorIndex == 1:
                        inv.equip(self.currentHero, "", "acc1")
                    elif self.cursorIndex == 2:
                        inv.equip(self.currentHero, "", "acc2")

        self.limit_cursor(cMin, cMax)
        return -1

    def limit_cursor(self, cMin, cMax):
        if self.MC.menuState == g.MenuState.ITEM or self.MC.menuState == g.MenuState.ITEM_ORGANIZE:
            if self.cursorIndex > self.itemTableLength - 1:
                self.itemCursorOffset += 1
                self.cursorIndex -= 1
            elif self.cursorIndex < 0:
                self.itemCursorOffset -= 1
                self.cursorIndex += 1

            if self.itemCursorOffset > g.INVENTORY_MAX_SLOTS - self.itemTableLength:
                self.itemCursorOffset = 0
                self.cursorIndex = 0
            elif self.itemCursorOffset < 0:
                self.itemCursorOffset = g.INVENTORY_MAX_SLOTS - self.itemTableLength
                self.cursorIndex = self.itemTableLength - 1

        elif self.MC.menuState == g.MenuState.SKILL:
            maxLength = min(len(self.currentHero.skills) - 1, self.skillTableLength - 1)
            if self.cursorIndex > maxLength:
                self.skillCursorOffset += 1
                self.cursorIndex -= 1
            elif self.cursorIndex < 0:
                self.skillCursorOffset -= 1
                self.cursorIndex += 1

            if self.skillCursorOffset + maxLength > len(self.currentHero.skills) - 1:
                self.skillCursorOffset = 0
                self.cursorIndex = 0
            elif self.skillCursorOffset < 0:
                self.skillCursorOffset = len(self.currentHero.skills) - maxLength - 1
                self.cursorIndex = maxLength

        elif self.MC.menuState == g.MenuState.EQUIP_WEAPON or self.MC.menuState == g.MenuState.EQUIP_ACC:
            maxLength = min(len(self.currentEquipList) - 1, self.skillTableLength - 1)
            if self.cursorIndex > maxLength:
                self.equipListCursorOffset += 1
                self.cursorIndex -= 1
            elif self.cursorIndex < 0:
                self.equipListCursorOffset -= 1
                self.cursorIndex += 1

            if self.equipListCursorOffset + maxLength > len(self.currentEquipList) - 1:
                self.equipListCursorOffset = 0
                self.cursorIndex = 0
            elif self.equipListCursorOffset < 0:
                self.equipListCursorOffset = len(self.currentEquipList) - maxLength - 1
                self.cursorIndex = maxLength

        elif self.MC.menuState == g.MenuState.ANIMAGI:
            maxLength = min(len(g.ANIMAGI) - 1, self.animagiTableLength - 1)
            if self.cursorIndex > maxLength:
                self.animagiCursorOffset += 1
                self.cursorIndex -= 1
            elif self.cursorIndex < 0:
                self.animagiCursorOffset -= 1
                self.cursorIndex += 1

            if self.animagiCursorOffset + maxLength > len(g.ANIMAGI) - 1:
                self.animagiCursorOffset = 0
                self.cursorIndex = 0
            elif self.animagiCursorOffset < 0:
                self.animagiCursorOffset = len(g.ANIMAGI) - maxLength - 1
                self.cursorIndex = maxLength

        elif self.cursorIndex > cMax:
            self.cursorIndex = cMin
        elif self.cursorIndex < cMin:
            self.cursorIndex = cMax

    def update(self):
        self.MC.controller.viewSurf.fill(g.BLACK)
        self.render_main_window()
        self.render_info_window()

        if not self.MC.menuState == g.MenuState.ITEM_OPTIONS and not self.MC.menuState == g.MenuState.ITEM_ORGANIZE and not self.MC.menuState == g.MenuState.ITEM:
            self.render_command_window()

        if self.MC.menuState == g.MenuState.ITEM_OPTIONS:
            self.render_item_window()
            self.render_item_options()
            self.process_get_item_options()
        elif self.MC.menuState == g.MenuState.ITEM_ORGANIZE:
            self.render_item_options()
            self.render_item_window()
            self.process_get_item_organize()
        elif self.MC.menuState == g.MenuState.ITEM:
            self.render_item_options()
            self.render_item_window()
            self.process_get_item()
        elif self.MC.menuState == g.MenuState.TARGET_ITEM:
            self.render_item_options()
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
        elif self.MC.menuState == g.MenuState.STATUS_HERO:
            self.render_status_hero_cursor()
            self.process_get_status_hero()
        elif self.MC.menuState == g.MenuState.STATUS:
            self.render_status_hero_cursor()
            self.render_stats_window()
            self.process_get_status()
        elif self.MC.menuState == g.MenuState.EQUIP_HERO:
            self.render_equip_hero_cursor()
            self.process_get_equip_hero()
        elif self.MC.menuState == g.MenuState.EQUIP:
            self.render_equip_hero_cursor()
            self.render_equip_window()
            self.process_get_equip_slot()
        elif self.MC.menuState == g.MenuState.EQUIP_WEAPON or self.MC.menuState == g.MenuState.EQUIP_ACC:
            self.render_equip_hero_cursor()
            self.render_equip_window()
            self.process_get_equip()
        elif self.MC.menuState == g.MenuState.ANIMAGI_HERO:
            self.render_animagi_hero_cursor()
            self.process_get_animagi_hero()
        elif self.MC.menuState == g.MenuState.ANIMAGI:
            self.render_animagi_hero_cursor()
            self.render_animagi_window()
            self.process_get_animagi()
        elif self.MC.menuState == g.MenuState.ANIMAGI_CONFIRM:
            self.render_animagi_hero_cursor()
            self.render_animagi_window()
            self.process_get_animagi_confirm()
        elif self.MC.menuState == g.MenuState.MENU:
            self.process_get_command()

        if self.selectedThing != None:
            returnVal = self.selectedThing
            self.selectedThing = None
            return returnVal
        else:
            return None

class Table ():

    def __init__(self, MC, topLeft, widths, heights, strings, aligns, colors):
        self.MC = MC
        self.TM = MC.controller.TM
        self.topLeft = topLeft
        self.widths = widths
        self.heights = heights
        self.cols = len(self.widths)
        self.rows = len(self.heights)
        self.strings = strings
        self.aligns = aligns
        self.colors = colors

        if not colors:
            for y in range(0, self.rows):
                self.colors.append([])
                for x in range(0, self.cols):
                    self.colors[y].append(g.WHITE)

    def updateString(self, string, x, y):
        self.strings[x][y] = string

    def render(self, cursor = -1, globalOffset = (0,0)):
        globalOffset = utility.add_tuple(self.topLeft, globalOffset)
        offset = globalOffset

        for y in range(0, self.rows):
            for x in range(0, self.cols):
                if self.aligns[x] == "left":
                    self.TM.draw_text_f(self.strings[y][x], offset, self.colors[y][x])
                elif self.aligns[x] == "right":
                    self.TM.draw_text_fr(self.strings[y][x], utility.add_tuple(offset, (self.widths[x], 0)), self.colors[y][x])
                offset = utility.add_tuple(offset, (self.widths[x], 0))
            if cursor == y:
                self.MC.controller.viewSurf.blit(self.MC.UI.cursorImage, utility.add_tuple((globalOffset[0], offset[1]), self.MC.UI.hCursorPosOffset))
            offset = utility.add_tuple((globalOffset[0], offset[1]), (0, self.heights[y]))
