import math
import random
import heapq

import pygame
import pygame.locals

import my_globals as g
import database as db
import battle_command as cmd
import battle_ai as bai
import event
import inventory
import utility


###################
##CONTROL CLASSES##
###################

class BattleController (object):
    
    def __init__(self, controller, initiative = -1):
        self.CONTROLLER = controller
        self.UI = BattleUI(self)
        
        random.seed()
        
        self.BATTLE_STATE = g.BattleState.FIGHT
        self.PREV_BATTLE_STATE = self.BATTLE_STATE
        
        self.battlers = []
        self.battlerCount = 0

        if (initiative != -1):
            self.initiative = initiative
        else:
            roll = random.randint(0, 100)
            if (roll < 50):
                utility.log ("Initiative NONE")
                self.initiative = g.Initiative.NONE
            elif (roll < 75):
                utility.log ("Initiative PARTY")
                self.UI.create_message("First strike!")
                self.initiative = g.Initiative.PARTY
            else:
                utility.log ("Initiative ENEMY")
                self.UI.create_message("Ambush!")
                self.initiative = g.Initiative.ENEMY
        
        #heroes
        for hero in g.PARTY_LIST:
            isHero = True
            NAME = hero.attr["name"]
            LV = hero.attr["lvl"]
            HP = hero.attr["hp"]
            MAXHP = hero.baseMaxHP
            SP = hero.attr["sp"]
            MAXSP = hero.baseMaxSP
            ATK = hero.baseAtk
            DEF = hero.baseDef
            MATK = hero.baseMAtk
            MDEF = hero.baseMDef
            HIT = hero.baseHit
            EVA = hero.baseEva
            AGI = hero.attr["agi"]
            LCK = hero.attr["lck"]
            SPR = hero.spr
            size = hero.size
            icon = hero.icon
            resD = hero.resD
            resS = hero.resS
            
            battler = BattleActor(self, isHero, NAME, SPR, size, icon, resD, resS, None, LV, HP, MAXHP, SP, MAXSP, ATK, DEF, MATK, MDEF, AGI, LCK, HIT, EVA)
            self.battlers.append(battler)

        #enemies
        self.monsterCounters = {}
        for monster in g.MONSTER_LIST:
            isHero = False
            NAME = monster.attr["name"]
            LV = monster.attr["lvl"]
            HP = MAXHP = monster.attr["hp"]
            SP = MAXSP = monster.attr["sp"]
            ATK = monster.attr["atk"]
            DEF = monster.attr["def"]
            MATK = monster.attr["matk"]
            MDEF = monster.attr["mdef"]
            HIT = monster.attr["hit"]
            EVA = monster.attr["eva"]
            AGI = monster.attr["agi"]
            LCK = monster.attr["lck"]
            SPR = monster.spr
            size = monster.size
            icon = monster.icon
            resD = monster.resD
            resS = monster.resS
            ai = bai.dic[NAME]
            
            if NAME in self.monsterCounters:
                self.monsterCounters[NAME] += 1
                #NAME += str(self.monsterCounters[NAME])
            else:
                self.monsterCounters[NAME] = 1
            
            battler = BattleActor(self, isHero, NAME, SPR, size, icon, resD, resS, ai, LV, HP, MAXHP, SP, MAXSP, ATK, DEF, MATK, MDEF, AGI, LCK, HIT, EVA)
            self.battlers.append(battler)
        
        self.rounds = 0
        self.turnOrder = []
        
        self.currentBattler = None
        self.queuedAction = None
        self.UI_CALLBACK = None
        self.eventQueue = event.EventQueue()

    def change_state(self, state):
        self.PREV_BATTLE_STATE = self.BATTLE_STATE
        self.BATTLE_STATE = state
        
        utility.log("BATTLE STATE CHANGED: " + str(self.PREV_BATTLE_STATE) + " >> " + str(self.BATTLE_STATE))

    def prev_state(self):
        self.BATTLE_STATE = self.PREV_BATTLE_STATE

    def update(self):
        eventCallback = self.eventQueue.run()
        
        if not self.UI.messageList and eventCallback < 0:
            if self.BATTLE_STATE == g.BattleState.AI:
                self.UI.update()
                if g.AI_TIMER > 0 and self.currentBattler.HP > 0:
                    g.AI_TIMER -= self.CONTROLLER.CLOCK.get_time()
                else:
                    self.currentBattler.take_turn()
            elif (self.BATTLE_STATE == g.BattleState.COMMAND or
                  self.BATTLE_STATE == g.BattleState.ITEM or
                  self.BATTLE_STATE == g.BattleState.SKILL):
                self.UI_CALLBACK = self.UI.update()
                if self.UI_CALLBACK != None:
                    self.UI_CALLBACK.start(self.currentBattler)
            elif self.BATTLE_STATE == g.BattleState.TARGET:
                self.UI_CALLBACK = self.UI.update()
                if self.UI_CALLBACK != None:
                    self.queuedAction(self.currentBattler, self.UI_CALLBACK)
            elif self.BATTLE_STATE == g.BattleState.FIGHT:
                if self.enemies_alive() and self.heroes_alive():
                    if self.turnOrder:
                        battler = self.next_turn()
                        if battler != None:
                            if (battler.isHero):
                                battler.take_turn()
                            else:
                                self.currentBattler = battler
                                g.AI_TIMER = g.AI_DELAY
                                self.change_state(g.BattleState.AI)
                                self.UI.change_state(g.BattleUIState.AI)
                    else:
                        self.next_round()
                else:
                    if self.heroes_alive():
                        self.change_state(g.BattleState.WIN)
                    else:
                        self.change_state(g.BattleState.LOSE)
        else:
            self.UI.update()

    def next_turn(self):
        nextBattler = self.turnOrder[0]
        del self.turnOrder[0]
        for battler in self.battlers:
            battler.turnOrder -= 1
        return nextBattler

    def next_round(self):
        self.rounds += 1
        
        utility.log("", g.LogLevel.FEEDBACK)
        utility.log("***********", g.LogLevel.FEEDBACK)
        utility.log("ROUND " + str(self.rounds), g.LogLevel.FEEDBACK)
        utility.log("***********", g.LogLevel.FEEDBACK)
        
        self.list_heroes()
        self.list_enemies()
        self.get_new_turn_order()

        utility.log("", g.LogLevel.FEEDBACK)
        utility.log("TURN ORDER", g.LogLevel.FEEDBACK)

    def first_hero(self):
        for battler in self.battlers:
            if (battler.HP > 0):
                if battler.isHero:
                    return battler
        return None

    def first_enemy(self):
        for battler in self.battlers:
            if (battler.HP > 0):
                if not battler.isHero:
                    return battler
        return None

    def get_new_turn_order(self):
        turnQueue = []
        heapq.heapify(turnQueue)
        counter = 0
        for battler in self.battlers:
            if (battler.HP > 0):
                counter += 1
                entry = [-battler.AGI, counter, battler]
                if self.initiative == g.Initiative.PARTY:
                    if battler.isHero:
                        heapq.heappush(turnQueue, entry)
                    else:
                        battler.turnOrder = -99
                elif self.initiative == g.Initiative.ENEMY:
                    if not battler.isHero:
                        heapq.heappush(turnQueue, entry)
                    else:
                        battler.turnOrder = -99
                else:
                    heapq.heappush(turnQueue, entry)
                    
        self.turnOrder = [heapq.heappop(turnQueue)[2] for i in range(len(turnQueue))]
        
        index = 0
        for battler in self.turnOrder:
            battler.turnOrder = index
            index += 1
        self.initiative = g.Initiative.NONE
        utility.log(self.turnOrder)
        
    
    def remove_turn(self, battler):
        entry = self.turnFinder.pop(battler)
        entry[-1] = None            

    def list_enemies(self):
        
        utility.log("", g.LogLevel.FEEDBACK)
        utility.log("*ENEMIES*", g.LogLevel.FEEDBACK)
        
        for battler in self.battlers:
            if not battler.isHero:
                utility.log(battler.NAME)
                if (battler.HP > 0):
                    utility.log("HP: " + str(battler.HP), g.LogLevel.FEEDBACK)
                else:
                    utility.log("DEAD", g.LogLevel.FEEDBACK)

    def list_heroes(self):
        utility.log("", g.LogLevel.FEEDBACK)
        utility.log("*HEROES*", g.LogLevel.FEEDBACK)
        for battler in self.battlers:
            if battler.isHero:
                utility.log(battler.NAME)
                if (battler.HP > 0):
                    utility.log("HP: " + str(battler.HP), g.LogLevel.FEEDBACK)
                else:
                    utility.log("DEAD", g.LogLevel.FEEDBACK)

    def enemies_alive(self):
        for battler in self.battlers:
            if not battler.isHero:
                if battler.HP > 0:
                    return True
        return False

    def heroes_alive(self):
        for battler in self.battlers:
            if battler.isHero:
                if battler.HP > 0:
                    return True
        return False

    def hit_calc(self, user, target):
        roll = random.randint(0, 100)
        if roll < user.HIT:
            return True
        else:
            self.UI.create_popup("MISS", target.spr.pos)
            utility.log("Missed!", g.LogLevel.FEEDBACK)
            return False

    def dodge_calc(self, user, target):
        roll = random.randint(0, 100)
        if roll < target.EVA:
            self.UI.create_popup("DODGE", target.spr.pos)
            utility.log("Dodged!", g.LogLevel.FEEDBACK)
            return True
        else:
            return False

    def crit_calc(self, user, target):
        roll = random.randint(0, 255)
        utility.log("Crit roll : " + str(roll))
        if roll < user.LCK:
            utility.log("Crit!", g.LogLevel.FEEDBACK)
            return True
        else:
            return False

    def status_calc(self, battler, status, rate):
        rate = 100-rate
        resOffset = -math.floor(100*battler.resS[status])
        minRoll = 0+resOffset
        maxRoll = 99+resOffset

        roll = random.randint(minRoll, maxRoll)
        
        utility.log("Roll Range: " + str(minRoll) + " - " + str(maxRoll))
        utility.log("Roll: " + str(roll))
        utility.log("Roll needed: " + str(rate))

        return roll >= rate

    def phys_def_calc(self, user, target):
        modValue = 0
        if (target.mods[g.BattlerStatus.DEFEND] > 0):
            utility.log(target.NAME + " has a defense bonus", g.LogLevel.FEEDBACK)
            modValue = target.DEF // 2
        defTotal = target.DEF + modValue
        utility.log("DEF: " + str(target.DEF) + " (+" + str(modValue) + ")")
        return defTotal

    def phys_dmg_calc(self, user, target):
        dmgMax = user.ATK * 2
        dmgMin = dmgMax - (user.ATK // 2)
        dmg = random.randint(dmgMin, dmgMax)
        utility.log("ATK: " + str(dmg) + " (" + str(dmgMin) + "," + str(dmgMax) + ")")
        if (dmg < 0):
            dmg = 0
        return dmg

    def poison_dmg_calc(self, battler):
        dmgMin = max(1, battler.MAXHP // 10)
        dmgMax = dmgMin + (dmgMin // 2)
        dmg = random.randint(dmgMin, dmgMax)
        return dmg

##############
##UI CLASSES##
##############

class BattleUI (object):
    def __init__(self, bc):
        self.BC = bc
        self.UI_STATE = g.BattleUIState.DEFAULT
        self.PREV_UI_STATE = self.UI_STATE
        self.output = []
        self.cursorPos = (0,0)
        self.cursorImage = pygame.image.load("spr/cursor-h.png")
        self.cursorRect = self.cursorImage.get_rect()
        self.heroStatusAnchors = [(101, 91), (101, 109), (101, 127)]
        self.cmdAnchors = [(8,92), (8,102), (8, 112), (8,122), (8,132)]
        self.tgtAnchors = [(8,92), (8,102), (8, 112), (8,122), (8,132)]
        self.itemAnchors = [(8,92), (8,102), (8, 112), (8,122), (8,132)]
        self.outAnchors = [(2, 66), (2, 58), (2,50), (2,42), (2,34), (2, 26), (2, 18), (2,10), (2,2)]
        self.battlerAnchors = [(124, 48), (132, 64), (140, 80), (38, 64), (22, 80), (54, 48), (62, 76), (78, 60)]
        self.turnBannerAnchor = (2, 0)
        self.turnAnchors = [(8, 0), (34, 0), (59, 0), (84, 0), (109, 0), (134, 0), (159, 0), (185, 0), (185, 0), (185, 0), (185, 0)]

        self.cursorIndex = 0
        self.commandCursor = 0
        self.targetCursor = 0
        self.skillCursor = 0
        self.itemCursor = 0
        self.skillSelectOffset = 0
        self.itemSelectOffset = 0

        self.windowImage = pygame.image.load("spr/battle/ui-window.png")
        self.windowAnchors = [(0,85)]

        self.battlerCursorOffset = (-4, -8)
        self.currentTurnCursor = pygame.image.load("spr/battle/cursor-turn.png")
        self.currentTargetCursor = pygame.image.load("spr/battle/cursor-target.png")
        self.currentTargetTurnCursor = pygame.image.load("spr/battle/cursor-target2.png")

        self.iconDead = pygame.image.load("spr/battle/icon-cross.png")
        self.iconDown = pygame.image.load("spr/battle/icon-down.png")
        self.iconDefend = pygame.image.load("spr/battle/icon-shield.png")
        self.iconPoison = pygame.image.load("spr/battle/icon-poison.png")

        self.turnImage = pygame.image.load("spr/battle/turn.png")
        self.heroTurnImage = pygame.image.load("spr/battle/turn-hero.png")
        self.monTurnImage = pygame.image.load("spr/battle/turn-mon.png")

        self.messageBoxImage = pygame.image.load("spr/battle/message-box.png")

        self.currentUser = 0
        self.validTargets = []

        self.popupList = []
        self.messageList = []
        
        self.selectedThing = None
        self.queuedMethod = None

    def get_command(self, user):
        self.currentUser = user
        self.selectedThing = None
        
        self.cursorIndex = self.targetCursor
        self.init_cursor()

        self.change_state(g.BattleUIState.COMMAND)

    def get_target(self, user, validTargets):
        self.currentUser = user
        self.validTargets = validTargets
        self.selectedThing = None
        
        self.cursorIndex = self.targetCursor
        self.init_cursor()

        self.change_state(g.BattleUIState.TARGET)

    def get_item(self, user):
        self.currentUser = user
        self.selectedThing = None
        
        self.cursorIndex = self.itemCursor
        self.init_cursor()

        self.change_state(g.BattleUIState.ITEM)

    def process_get_command(self):
        selection = self.process_input(0, len(self.currentUser.commands)-1)
        if (selection > -1):
            self.selectedThing = self.currentUser.commands[selection]
            self.commandCursor = self.cursorIndex
            self.UI_STATE = g.BattleUIState.DEFAULT

    def process_get_target(self):
        selection = self.process_input(0, len(self.validTargets)-1)
        if (selection > -1):
            self.selectedThing = self.validTargets[selection]
            self.targetCursor = self.cursorIndex
            self.UI_STATE = g.BattleUIState.DEFAULT

    def process_get_item(self):
        minIndex = max(0, self.itemSelectOffset)
        maxIndex = min(99, self.itemSelectOffset + 5)
        selection = self.process_input(0, 4)
        if (selection > -1):
            #item = g.INVENTORY[selection + self.itemSelectOffset][0]
            if item.battleAction != None:
                inventory.remove_item(item.name)
                self.selectedThing = db.InvItem.dic[item.name].battleAction
                self.itemCursor = self.cursorIndex
                self.UI_STATE = g.BattleUIState.DEFAULT

    def render_command_window(self):
        index = 0
        for command in self.currentUser.commands:
            self.BC.CONTROLLER.TEXT_MANAGER.draw_text(command.name(), self.cmdAnchors[index], g.WHITE)
            index += 1
        self.BC.CONTROLLER.VIEW_SURF.blit(self.cursorImage, utility.add_tuple(self.cmdAnchors[self.cursorIndex],(-self.cursorImage.get_width(),0)))

    def render_target_window(self):
        index = 0
        for target in self.validTargets:
            self.BC.CONTROLLER.TEXT_MANAGER.draw_text(target.NAME, self.tgtAnchors[index], g.WHITE)
            index += 1
        self.BC.CONTROLLER.VIEW_SURF.blit(self.cursorImage, utility.add_tuple(self.tgtAnchors[self.cursorIndex],(-self.cursorImage.get_width(),0)))

    def render_item_window(self):
##        if self.cursorIndex  < 0:
##            self.cursorIndex = 0
##        if self.cursorIndex > 4:
##            self.cursorIndex = 4
        index = self.itemSelectOffset
        for i in range(self.itemSelectOffset, self.itemSelectOffset+5):
            if i < g.INVENTORY_MAX_SLOTS - 5:
                item = g.INVENTORY[index][0]
                if (item.name != ""):
                    self.BC.CONTROLLER.TEXT_MANAGER.draw_text(item.name, self.itemAnchors[index], g.WHITE)
                    self.BC.CONTROLLER.TEXT_MANAGER.draw_text_ralign(str(g.INVENTORY[index][1]), utility.add_tuple(self.itemAnchors[index], (80, 0)), g.WHITE)
                index += 1
        self.BC.CONTROLLER.VIEW_SURF.blit(self.cursorImage, utility.add_tuple(self.itemAnchors[self.cursorIndex], (-self.cursorImage.get_width(),0)))
                

    def render_hero_status(self):
        self.BC.CONTROLLER.VIEW_SURF.blit(self.windowImage, self.windowAnchors[0])
        index = 0
        for hero in self.BC.battlers:
            iconOffset = (0, 7)
            iconOffsetH = (9, 0)
            if (hero.isHero):
                self.BC.CONTROLLER.TEXT_MANAGER.draw_text(hero.NAME, self.heroStatusAnchors[index], g.WHITE)
                self.BC.CONTROLLER.TEXT_MANAGER.draw_text_ralign(str(hero.HP), utility.add_tuple(self.heroStatusAnchors[index], (56, 0)), g.WHITE)
                if hero.mods[g.BattlerStatus.STUN] > 0:
                    self.BC.CONTROLLER.VIEW_SURF.blit(self.iconDown, utility.add_tuple(self.heroStatusAnchors[index], iconOffset))
                    iconOffset = utility.add_tuple(iconOffset, iconOffsetH)
                if hero.mods[g.BattlerStatus.DEFEND] > 0:
                    self.BC.CONTROLLER.VIEW_SURF.blit(self.iconDefend, utility.add_tuple(self.heroStatusAnchors[index], iconOffset))
                    iconOffset = utility.add_tuple(iconOffset, iconOffsetH)
                if hero.mods[g.BattlerStatus.POISON] > 0:
                    self.BC.CONTROLLER.VIEW_SURF.blit(self.iconPoison, utility.add_tuple(self.heroStatusAnchors[index], iconOffset))
                    iconOffset = utility.add_tuple(iconOffset, iconOffsetH)
                #self.BC.CONTROLLER.TEXT_MANAGER.draw_text_ralign(str(hero.SP), utility.add_tuple(self.heroStatusAnchors[index], (56, 0)), g.WHITE)
                index += 1

    def render_turn_cursor(self):
        if self.BC.currentBattler:
            cursorOffset = utility.add_tuple((0, -self.BC.currentBattler.size), self.battlerCursorOffset)
            if self.BC.currentBattler:
                self.BC.CONTROLLER.VIEW_SURF.blit(self.currentTurnCursor, utility.add_tuple(self.BC.currentBattler.spr.pos, cursorOffset))

    def render_target_cursor(self):
        battler = self.validTargets[self.cursorIndex]
        if battler:
            cursorOffset = utility.add_tuple((0, -battler.size), self.battlerCursorOffset)
            self.BC.CONTROLLER.VIEW_SURF.blit(self.currentTargetCursor, utility.add_tuple(battler.spr.pos, cursorOffset))
            if battler.turnOrder >= 0:
                #this is currently rendering over any icons in the turn area
                self.BC.CONTROLLER.VIEW_SURF.blit(self.currentTargetTurnCursor, utility.add_tuple(self.turnAnchors[battler.turnOrder], (2,0)))

    def render_battlers(self):
        dt = self.BC.CONTROLLER.CLOCK.get_time()
        surf = self.BC.CONTROLLER.VIEW_SURF
        
        index = 0
        for battler in self.BC.battlers:
            if battler.spr.animated:
                battler.spr.animate(dt)
                battler.spr.draw(surf)
            else:
                iconOffset = (0, -16)
                iconOffsetH = (-8, 0)
                if battler.HP > 0:
                    battler.spr.draw(surf)
                    if battler.mods[g.BattlerStatus.DEFEND] > 0:
                        self.BC.CONTROLLER.VIEW_SURF.blit(self.iconDefend, utility.add_tuple(battler.spr.pos, iconOffset))
                        iconOffset = utility.add_tuple(iconOffset, iconOffsetH)
                    if battler.mods[g.BattlerStatus.STUN] > 0:
                        self.BC.CONTROLLER.VIEW_SURF.blit(self.iconDown, utility.add_tuple(battler.spr.pos, iconOffset))
                        iconOffset = utility.add_tuple(iconOffset, iconOffsetH)
                    if battler.mods[g.BattlerStatus.POISON] > 0:
                        self.BC.CONTROLLER.VIEW_SURF.blit(self.iconPoison, utility.add_tuple(battler.spr.pos, iconOffset))
                        iconOffset = utility.add_tuple(iconOffset, iconOffsetH)
            index += 1

    def render_turns(self):
        self.BC.CONTROLLER.VIEW_SURF.blit(self.turnImage, self.turnBannerAnchor)
        for battler in self.BC.turnOrder:
            if (battler.isHero):
                img = self.heroTurnImage
            else:
                img = self.monTurnImage
                
            anchorIndex = battler.turnOrder
            self.BC.CONTROLLER.VIEW_SURF.blit(img, self.turnAnchors[anchorIndex])
            self.BC.CONTROLLER.VIEW_SURF.blit(battler.icon, utility.add_tuple(self.turnAnchors[anchorIndex], (3,0)))
            label = battler.NAME[0:5]
            self.BC.CONTROLLER.TEXT_MANAGER.draw_text(label, utility.add_tuple(self.turnAnchors[anchorIndex], (2,17)), g.WHITE, g.FONT_SML)

            iconOffset = (0, 0)
            iconOffsetH = (9, 0)
            
            if (battler.HP <= 0):
                self.BC.CONTROLLER.VIEW_SURF.blit(self.iconDead, utility.add_tuple(self.turnAnchors[anchorIndex], iconOffset))
                iconOffset = utility.add_tuple(iconOffset, iconOffsetH)
            if battler.mods[g.BattlerStatus.STUN] > 0:
                self.BC.CONTROLLER.VIEW_SURF.blit(self.iconDown, utility.add_tuple(self.turnAnchors[anchorIndex], iconOffset))
                iconOffset = utility.add_tuple(iconOffset, iconOffsetH)
            if battler.mods[g.BattlerStatus.DEFEND] > 0:
                self.BC.CONTROLLER.VIEW_SURF.blit(self.iconDefend, utility.add_tuple(self.turnAnchors[anchorIndex], iconOffset))
                iconOffset = utility.add_tuple(iconOffset, iconOffsetH)
            if battler.mods[g.BattlerStatus.POISON] > 0:
                self.BC.CONTROLLER.VIEW_SURF.blit(self.iconPoison, utility.add_tuple(self.turnAnchors[anchorIndex], iconOffset))
                iconOffset = utility.add_tuple(iconOffset, iconOffsetH)
               

    def render_output(self, maxLines = 6):
        lineCount = 0
        for line in reversed(self.output):
            self.BC.CONTROLLER.TEXT_MANAGER.draw_text(line, self.outAnchors[lineCount])
            lineCount += 1
            if lineCount > maxLines-1:
                break

    def init_cursor(self):
        g.CURSOR_TIMER = 0
        g.CONFIRM_TIMER = g.CONFIRM_DELAY     

    def update(self):
        self.BC.CONTROLLER.VIEW_SURF.fill(g.GREEN_BLUE)
        self.render_hero_status()
        self.render_battlers()
        
        self.render_turns()
        self.render_turn_cursor()

        if (self.UI_STATE == g.BattleUIState.TARGET):
            self.process_get_target()
            self.render_target_window()
            self.render_target_cursor()
        elif (self.UI_STATE == g.BattleUIState.COMMAND):
            self.process_get_command()
            self.render_command_window()
        elif (self.UI_STATE == g.BattleUIState.ITEM):
            self.process_get_item()
            self.render_item_window()

        if self.messageList:
            if self.messageList[0].life > 0:
                self.messageList[0].update()
            else:
                del self.messageList[0]

        if self.popupList:
            if self.popupList[0].life > 0:
                self.popupList[0].update()
            else:
                del self.popupList[0]
        
        self.BC.CONTROLLER.window_render()

        if self.selectedThing != None:
            returnVal = self.selectedThing
            self.selectedThing = None
            return returnVal
        else:
            return None
        

    def change_state(self, state):
        self.PREV_UI_STATE = self.UI_STATE
        self.UI_STATE = state
        utility.log("UI STATE CHANGED: " + str(self.PREV_UI_STATE) + " >> " + str(self.UI_STATE))

    def prev_state(self):
        utility.log(self.UI_STATE)
        utility.log(self.BC.BATTLE_STATE)
        
        self.UI_STATE = self.PREV_UI_STATE
        self.BC.prev_state()
        
        utility.log()
        utility.log(self.UI_STATE)
        utility.log(self.BC.BATTLE_STATE)

    def process_input(self, cMin, cMax):
        dT = self.BC.CONTROLLER.CLOCK.get_time()
        if (g.CURSOR_TIMER >= 0):
            g.CURSOR_TIMER -= dT
        if (g.CONFIRM_TIMER >= 0):
            g.CONFIRM_TIMER -= dT   
        
        if self.BC.CONTROLLER.KEYS[g.KEY_DOWN]:
            if g.CURSOR_TIMER < 0:
                g.CURSOR_TIMER = g.CURSOR_DELAY
                self.cursorIndex += 1
                if self.cursorIndex > cMax:
                    self.cursorIndex = cMin
        elif self.BC.CONTROLLER.KEYS[g.KEY_UP]:
            if g.CURSOR_TIMER < 0:
                g.CURSOR_TIMER = g.CURSOR_DELAY
                self.cursorIndex -= 1
                if self.cursorIndex < cMin:
                    self.cursorIndex = cMax
        elif self.BC.CONTROLLER.KEYS[g.KEY_CONFIRM]:
            if g.CONFIRM_TIMER < 0:
                g.CURSOR_TIMER = g.CURSOR_DELAY
                return self.cursorIndex
        elif self.BC.CONTROLLER.KEYS[g.KEY_CANCEL]:
            if g.CONFIRM_TIMER < 0:
                g.CURSOR_TIMER = g.CURSOR_DELAY
                if (self.UI_STATE == g.BattleUIState.TARGET or
                    self.UI_STATE == g.BattleUIState.ITEM or
                    self.UI_STATE == g.BattleUIState.SKILL):
                    
                    self.cursorIndex = self.commandCursor
                    self.change_state(g.BattleUIState.COMMAND)
                    self.BC.change_state(g.BattleState.COMMAND)
                    
        return -1

    def create_popup(self, string, pos, col = g.WHITE, life = g.BATTLE_POPUP_LIFE):
        self.popupList.append(BattleUIPopup(self, string, pos, col, life))

    def create_message(self, string, life = g.BATTLE_MESSAGE_LIFE):
        self.messageList.append(BattleUIMessage(self, string, life))
    
class BattleUIPopup (object):
    def __init__(self, ui, string, pos, col, life):
        self.ui = ui
        self.string = string
        self.col = col
        self.life = life
        self.halfLife = life // 2
        self.halfTrigger = False
        self.speed = .6
        self.x = pos[0]
        self.y = pos[1] + self.ui.battlerCursorOffset[1]

    def update(self):
        if self.life < self.halfLife and not self.halfTrigger:
            self.halfTrigger = True
            self.speed *= -1
        self.y -= self.speed
        self.life -= self.ui.BC.CONTROLLER.CLOCK.get_time()
        self.ui.BC.CONTROLLER.TEXT_MANAGER.draw_text_shaded_centered(self.string, (self.x, math.floor(self.y)), self.col)

class BattleUIMessage (object):
    def __init__(self, ui, string, life):
        self.ui = ui
        self.string = string
        self.life = life
        self.boxPos = (0,0)
        self.textPos = (80, 11)
        #self.textPos = utility.add_tuple((80,4), (-g.FONT_LRG.size(string)[0] // 2, 0))

    def update(self):
        self.life -= self.ui.BC.CONTROLLER.CLOCK.get_time()
        self.ui.BC.CONTROLLER.VIEW_SURF.blit(self.ui.messageBoxImage, self.boxPos)
        self.ui.BC.CONTROLLER.TEXT_MANAGER.draw_text_centered(self.string, self.textPos, g.WHITE, g.FONT_LRG)
        #self.ui.BC.CONTROLLER.TEXT_MANAGER.draw_text(self.string, self.textPos, g.WHITE, g.FONT_LRG)

#################
##ACTOR CLASSES##
#################

class Sprite (pygame.sprite.Sprite):

    def __init__(self, frameset, frameSize, anchor, animated = False, animTime = 200):
        pygame.sprite.Sprite.__init__(self)
        
        self.frameCache = utility.TileCache(frameSize, frameSize)
        self.frameset = self.frameCache[frameset]
        self.animations = {}
        
        if (animated):
            self.init_basic_animations()
        else:
            self.create_animation('idle', [(0,0)])
        
        self.animated = animated
        self.paused = not animated
        self.animTime = animTime
        self.curTime = 0
        self.curFrame = 0
        self.curAnim = 'idle'


        self.image = None
        self.set_anim(self.curAnim, True)
        self.rect = self.image.get_rect()
        self.anchor = anchor
        self.pos = self.anchor

    @property
    def pos(self):
        return self.rect.midbottom

    @pos.setter
    def pos(self, pos):
        self.rect.midbottom = pos
        
    def move_ip(self, offset):
        self.offset = offset
        self.rect.midbottom = utility.add_tuple(self.pos, self.offset)
        
    def init_basic_animations(self):
        framelist = [(1,0),
                     (0,0),
                     (1,0),
                     (2,0)]
        self.create_animation("idle", framelist)
        
        framelist = [(1,1),
                     (0,1),
                     (1,1),
                     (2,1)]
        self.create_animation("defend", framelist)
        
        framelist = [(0,1)]
        self.create_animation("attack", framelist)
        
        framelist = [(0,4)]
        self.create_animation("dead", framelist)
        
        framelist = [(0,2)]
        self.create_animation("damage", framelist)
        
        framelist = [(0,2)]
        self.create_animation("stun", framelist)
        
        framelist = [(1,3),
                     (0,3),
                     (1,3),
                     (2,3)]
        self.create_animation("poison", framelist)
        
        framelist = [(1,5),
                     (0,5),
                     (1,5),
                     (2,5)]
        self.create_animation("sleep", framelist)


    def create_animation(self, key, framelist):
        framecount = len(framelist)
        frames = []
        for i in range(0, framecount):
            row = framelist[i][0]
            col = framelist[i][1]
            frames.append(self.frameset[row][col])
        self.animations[key] = frames

    def set_anim(self, key, reset = False):
        lastAnim = self.curAnim
        if (self.curAnim != key or reset):
            self.curAnim = key
            self.curFrame = 0
            self.curTime = 0
            try:
                self.image = self.animations[self.curAnim][self.curFrame]
            except KeyError:
                self.curAnim = lastAnim
                self.image = self.animations[self.curAnim][self.curFrame]
                utility.log("ERROR: tried to set a non-existant animation. Reverting to the previous animation", g.LogLevel.ERROR)

    def animate(self, dt):
        if (self.animated and not self.paused):
            self.curTime += dt;
            if (self.curTime > self.animTime):
                self.curFrame += 1
                if (self.curFrame >= len(self.animations[self.curAnim])):
                    self.curFrame = 0
                self.image = self.animations[self.curAnim][self.curFrame]
                self.curTime = 0

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class BattleActor (object):
    
    def __init__(self, BC, isHero, NAME, spr, size, icon, resD, resS, ai = None, LV = 1, HP=10, MAXHP = 10, SP = 10, MAXSP = 10, ATK = 5, DEF = 5, MATK = 5, MDEF = 5, AGI = 5, LCK = 5, HIT = 95, EVA = 5, RES = {}):
        self.BC = BC
        self.isHero = isHero
        self.NAME = NAME
        self.LV = LV
        self.HP = HP
        self.MAXHP = MAXHP
        self.SP = SP
        self.MAXSP = MAXSP
        self.ATK = ATK
        self.DEF = DEF
        self.MATK = MATK
        self.MDEF = MDEF
        self.AGI = AGI
        self.LCK = LCK
        self.HIT = HIT
        self.EVA = EVA

        self.resD = resD
        self.resS = resS

        self.mods = {}
        self.mods[g.BattlerStatus.DEFEND] = 0
        self.mods[g.BattlerStatus.SLEEP] = 0
        self.mods[g.BattlerStatus.POISON] = 0
        self.mods[g.BattlerStatus.SILENCE] = 0
        self.mods[g.BattlerStatus.STUN] = 0
        self.mods[g.BattlerStatus.PARALYZE] = 0

        self.currentTurnPos = 0

        self.battlerIndex = self.BC.battlerCount
        self.BC.battlerCount += 1

        self.size = size
        self.spr = Sprite(spr, size, self.BC.UI.battlerAnchors[self.battlerIndex], self.isHero)
        self.icon = icon
        
        self.aggro = random.randint(0, math.floor(self.HP // 10))

        self.ai = ai
        self.isAI = (not self.isHero)
        if not self.isAI:
            self.commands = []
            self.commands.append(cmd.Attack)
            self.commands.append(cmd.Defend)
            self.commands.append(cmd.UseItem)

    @property
    def hpPercent (self):
        return (self.HP / self.MAXHP)*100

    def aggro_up(self, value=-1):
        if value < 0:
            value = random.randint(1, 1+self.hpPercent//2)
        self.aggro += value
        if (self.aggro > 100):
            self.aggro = 100

    def aggro_down(self, value=-1):
        if value < 0:
            value = random.randint(1, self.hpPercent//4)
        self.aggro -= value
        if (self.aggro < 0):
            self.aggro = 0

    def aggro_half(self):
        self.aggro = self.aggro // 2

    def can_act(self):
        utility.log()
        if (self.HP == 0):
            return False
        elif (self.mods[g.BattlerStatus.SLEEP] > 0):
            self.BC.UI.create_popup("zzZ", self.spr.pos)
            utility.log(self.NAME + " is asleep.", g.LogLevel.FEEDBACK)
            return False
        elif (self.mods[g.BattlerStatus.STUN] > 0):
            self.BC.UI.create_popup("SKIP", self.spr.pos)
            utility.log(self.NAME + " is stunned.", g.LogLevel.FEEDBACK)
            return False
        elif (self.mods[g.BattlerStatus.PARALYZE] > 0):
            utility.log(self.NAME  + " is paralyzed.", g.LogLevel.FEEDBACK)
            return False
        else:
            utility.log("It's " + self.NAME + "'s turn.", g.LogLevel.FEEDBACK)
            return True

    def reset_anim(self):
        if self.spr.animated:
            if self.HP > 0:
                if self.mods[g.BattlerStatus.DEFEND]:
                    self.spr.set_anim("defend")
                elif self.mods[g.BattlerStatus.STUN]:
                    self.spr.set_anim("stun")
                elif self.mods[g.BattlerStatus.POISON]:
                    self.spr.set_anim("poison")
                elif self.mods[g.BattlerStatus.SLEEP]:
                    self.spr.set_anim("sleep")
                elif self.mods[g.BattlerStatus.PARALYZE]:
                    self.spr.set_anim("stun")
                else:
                    self.spr.set_anim("idle")
            else:
                self.spr.set_anim("dead")

            
    def before_turn(self):
        self.mods[g.BattlerStatus.DEFEND] -= 1
        self.mods[g.BattlerStatus.SLEEP] -= 1
        self.mods[g.BattlerStatus.PARALYZE] -= 1
        self.min_mods()

        if self.mods[g.BattlerStatus.POISON] > 0:
            self.take_damage(self.BC.poison_dmg_calc(self), g.DamageType.POISON)

        self.reset_anim()

    def after_turn(self):
        self.mods[g.BattlerStatus.STUN] -= 1
        self.min_mods()
        self.BC.change_state(g.BattleState.FIGHT)

    def min_mods(self):
        for mod in self.mods:
            if (self.mods[mod] < 0):
                self.mods[mod] = 0

    def take_turn(self):
        self.BC.currentBattler = self
        if self.isAI:
            utility.log(self.NAME + " is AI")
            self.ai.run(self)
        else:
            self.before_turn()
            if (self.can_act()):
                self.BC.change_state(g.BattleState.COMMAND)
                self.BC.UI.get_command(self)
            else:
                self.after_turn()

    def stun(self, rate = 100):
        self.aggro_down()
        if self.BC.status_calc(self, g.BattlerStatus.STUN, rate):
            if self.mods[g.BattlerStatus.DEFEND] > 0:
                self.mods[g.BattlerStatus.DEFEND] = 0
                self.BC.UI.create_popup("BREAK", self.spr.pos)
                utility.log(self.NAME + "'s defense was broken!", g.LogLevel.FEEDBACK)
            else:
                self.BC.UI.create_popup("STUN", self.spr.pos)
                utility.log(self.NAME + " is stunned!", g.LogLevel.FEEDBACK)
                self.mods[g.BattlerStatus.STUN] = 1
                self.reset_anim()
        else:
            self.BC.UI.create_popup("RES", self.spr.pos)
            utility.log(self.NAME + " resisted stun", g.LogLevel.FEEDBACK)

    def poison(self, rate = 100):
        self.aggro_down()
        if self.BC.status_calc(self, g.BattlerStatus.POISON, rate):
            self.BC.UI.create_popup("PSN", self.spr.pos)
            self.mods[g.BattlerStatus.POISON] = 1
            self.reset_anim()
        else:
            self.BC.UI.create_popup("RES", self.spr.pos)
            utility.log(self.NAME + " resisted poison", g.LogLevel.FEEDBACK)

    def death(self, rate = 100):
        self.aggro_down()
        if self.BC.status_calc(self, g.BattlerStatus.DEATH, rate):
            self.BC.UI.create_popup("DEATH", self.spr.pos)
            self.kill()
        else:
            self.BC.UI.create_popup("RES", self.spr.pos)
            utility.log(self.NAME + " resisted poison", g.LogLevel.FEEDBACK)

    def take_damage(self, damage, damageType = g.DamageType.NONE):
        self.aggro_down()

        damage -= math.floor(damage * self.resD[damageType])
        if damage >= 0:
            col = g.WHITE
        else:
            col = g.GREEN
            
        self.HP -= damage
        utility.log(self.NAME + " takes " + str(damage) + " damage!")
        self.BC.UI.create_popup(str(abs(damage)), self.spr.pos, col)
        self.check_hp()
        

    def heal_hp(self, damage, damageType = g.DamageType.NONE):
        damage -= math.floor(damage * self.resD[damageType])
        if damage >= 0:
            col = g.GREEN
        else:
            col = g.WHITE
            
        self.HP += damage
        utility.log(self.NAME + " restores " + str(damage) + " HP!")
        self.BC.UI.create_popup(str(abs(damage)), self.spr.pos, col)
        self.check_hp()

    def check_hp(self):
        if (self.HP < 0):
            self.HP = 0
        if (self.HP > self.MAXHP):
            self.HP = self.MAXHP
        if (self.HP == 0):
            self.kill()
            utility.log(self.NAME + " died!")

    def kill(self):
        self.reset_anim()
        for mod in self.mods:
            utility.log(str (mod))
            self.mods[mod] = 0
        self.mods[g.BattlerStatus.DEATH] = 1
