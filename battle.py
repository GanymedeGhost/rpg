import math
import random
import heapq
import pygame
import pygame.locals
import my_globals as g
import database as db
import utility

#########
##ENUMS##
#########

class BattlerStatus():
    DEFEND = 0
    POISON = 1
    SLEEP = 2
    SILENCE = 3
    STUN = 4
    PARALYZE = 5

class DamageType():
    PHYS = 0
    FIRE = 1
    ICE = 2
    ELEC = 3
    WIND = 4
    LIGHT = 5
    DARK = 6
    CURSE = 7
    NONE = 8

class BattleState():
    FIGHT = 0
    WIN = 1
    LOSE = 2
    TARGET = 3
    COMMAND = 4
    AI = 5

class UIState():
    DEFAULT = 0
    TARGET = 1
    COMMAND = 2
    SKILL = 3
    ITEM = 4
    AI = 5

###################
##CONTROL CLASSES##
###################

class BattleController (object):
    def __init__(self, controller):
        self.CONTROLLER = controller
        self.UI = BattleUI(self)
        random.seed()
        self.BATTLE_STATE = BattleState.FIGHT
        self.PREV_BATTLE_STATE = self.BATTLE_STATE
        self.battlers = []
        self.battlerCount = 0
        
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
            print (NAME + " AGI: " + str(AGI))
            battler = BattleActor(self, isHero, NAME, SPR, LV, HP, MAXHP, SP, MAXSP, ATK, DEF, MATK, MDEF, AGI, LCK, HIT, EVA)
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
            print (NAME + " AGI: " + str(AGI))

            
            if NAME in self.monsterCounters:
                self.monsterCounters[NAME] += 1
                NAME += str(self.monsterCounters[NAME])
            else:
                self.monsterCounters[NAME] = 1
            
            print (self.battlerCount)
            battler = BattleActor(self, isHero, NAME, SPR, LV, HP, MAXHP, SP, MAXSP, ATK, DEF, MATK, MDEF, AGI, LCK, HIT, EVA)
            self.battlers.append(battler)
        
        self.rounds = 0
        self.turnQueue = []
        self.turnFinder = {}
        self.currentBattler = None
        self.queuedAction = None
        self.UI_CALLBACK = None

    def change_state(self, state):
        self.PREV_BATTLE_STATE = self.BATTLE_STATE
        self.BATTLE_STATE = state
        print ("BATTLE STATE CHANGED: " + str(self.PREV_BATTLE_STATE) + " >> " + str(self.BATTLE_STATE))

    def prev_state(self):
        self.BATTLE_STATE = self.PREV_BATTLE_STATE

    def update(self):
        if self.BATTLE_STATE ==  BattleState.AI:
            self.UI.update()
            if g.AI_TIMER > 0 and self.currentBattler.HP > 0:
                g.AI_TIMER -= self.CONTROLLER.CLOCK.get_time()
            else:
                self.currentBattler.take_turn()
        elif self.BATTLE_STATE == BattleState.COMMAND:
            self.UI_CALLBACK = self.UI.update()
            if self.UI_CALLBACK != None:
                self.UI_CALLBACK.start(self.currentBattler)
        elif self.BATTLE_STATE == BattleState.TARGET:
            self.UI_CALLBACK = self.UI.update()
            if self.UI_CALLBACK != None:
                self.queuedAction(self.currentBattler, self.UI_CALLBACK)
        elif self.BATTLE_STATE == BattleState.FIGHT:
            if self.enemies_alive() and self.heroes_alive():
                if self.turnQueue:
                    priority, count, battler = heapq.heappop(self.turnQueue)
                    if battler != None:
                        if (battler.isHero):
                            battler.take_turn()
                        else:
                            self.currentBattler = battler
                            g.AI_TIMER = g.AI_DELAY
                            self.change_state(BattleState.AI)
                            self.UI.change_state(UIState.AI)
                else:
                    self.next_round()
            else:
                if self.heroes_alive():
                    self.change_state(BattleState.WIN)
                else:
                    self.change_state(BattleState.LOSE)

    def next_round(self):
        self.rounds += 1
        print ()
        print ("***********")
        self.UI.print_line("ROUND " + str(self.rounds))
        print ("ROUND " + str(self.rounds))
        print ("***********")
        self.list_heroes()
        self.list_enemies()
        self.get_turn_order()

        print ()
        print ("TURN ORDER")
        turnQueueCopy = self.turnQueue[:]
        while turnQueueCopy:
            item = heapq.heappop(turnQueueCopy)
            print (item[2].NAME)

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

    def get_turn_order(self):
        self.turnQueue = []
        self.turnFinder = {}
        heapq.heapify(self.turnQueue)
        counter = 0
        for battler in self.battlers:
            if (battler.HP > 0):
                counter += 1
                entry = [-battler.AGI, counter, battler]
                self.turnFinder[battler] = entry
                heapq.heappush(self.turnQueue, entry)
    
    def remove_turn(self, battler):
        entry = self.turnFinder.pop(battler)
        entry[-1] = None            

    def list_enemies(self):
        print("")
        print("*ENEMIES*")
        for battler in self.battlers:
            if not battler.isHero:
                print (battler.NAME)
                if (battler.HP > 0):
                    print ("HP: " + str(battler.HP))
                else:
                    print ("DEAD")

    def list_heroes(self):
        print("")
        print("*HEROES*")
        for battler in self.battlers:
            if battler.isHero:
                print (battler.NAME)
                if (battler.HP > 0):
                    print ("HP: " + str(battler.HP))
                else:
                    print ("DEAD")

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
            self.UI.print_line("Missed!")
            self.UI.create_popup("Miss!", target.pos)
            print ("Missed!")
            return False

    def dodge_calc(self, user, target):
        roll = random.randint(0, 100)
        if roll < target.EVA:
            self.UI.print_line("Dodged!")
            self.UI.create_popup("Dodged!", target.pos)
            print ("Dodged!")
            return True
        else:
            return False

    def crit_calc(self, user, target):
        roll = random.randint(0, 255)
        #print ("Crit roll : " + str(roll))
        if roll < user.LCK:
            self.UI.print_line("Crit!")
            print ("Crit!")
            return True
        else:
            return False

    def phys_def_calc(self, user, target):
        modValue = 0
        if (target.mods[BattlerStatus.DEFEND] > 0):
            print (target.NAME + " has a defense bonus")
            modValue = target.DEF // 2
        defTotal = target.DEF + modValue
        #print ("DEF: " + str(target.DEF) + " (+" + str(modValue) + ")")
        return defTotal

    def phys_dmg_calc(self, user, target):
        dmgMax = user.ATK * 2
        dmgMin = dmgMax - (user.ATK // 2)
        dmg = random.randint(dmgMin, dmgMax)
        #print ("ATK: " + str(dmg) + " (" + str(dmgMin) + "," + str(dmgMax) + ")")
        if (dmg < 0):
            dmg = 0
        return dmg

##############
##UI CLASSES##
##############

class BattleUI (object):
    def __init__(self, bc):
        self.BC = bc
        self.UI_STATE = UIState.DEFAULT
        self.PREV_UI_STATE = self.UI_STATE
        self.output = []
        self.cursorPos = (0,0)
        self.cursorImage = pygame.image.load("spr/cursor-h.png")
        self.cursorRect = self.cursorImage.get_rect()
        self.heroStatusAnchors = [(101, 90), (101, 107), (101, 124)]
        self.cmdAnchors = [(8,92), (8,102), (8, 112), (8,122), (8,132)]
        self.tgtAnchors = [(8,92), (8,102), (8, 112), (8,122), (8,132), (8,142), (8,152)]
        self.outAnchors = [(2, 66), (2, 58), (2,50), (2,42), (2,34), (2, 26), (2, 18), (2,10), (2,2)]
        self.battlerAnchors = [(114, 32), (122, 48), (130, 64), (32, 31), (24, 47), (16, 63), (64, 31), (48, 47), (32, 63)]
        self.turnBannerAnchor = (2, 0)
        self.turnAnchors = [(8, 0), (34, 0), (59, 0), (84, 0), (109, 0), (134, 0), (159, 0), (185, 0), (185, 0), (185, 0), (185, 0)]

        self.cursorIndex = 0
        self.commandCursor = 0
        self.targetCursor = 0
        self.skillCursor = 0
        self.itemCursor = 0

        self.windowImage = pygame.image.load("spr/battle/ui-window.png")
        self.windowAnchors = [(0,85)]

        self.currentTurnCursor = pygame.image.load("spr/battle/cursor-turn.png")
        self.currentTargetCursor = pygame.image.load("spr/battle/cursor-target.png")

        self.turnImage = pygame.image.load("spr/battle/turn.png")
        self.heroTurnImage = pygame.image.load("spr/battle/turn-hero.png")
        self.monTurnImage = pygame.image.load("spr/battle/turn-mon.png")

        self.currentUser = 0
        self.validTargets = []
        #self.commandList = []

        self.popupList = []
        
        self.selectedThing = None
        self.queuedMethod = None

    def get_command(self, user):
        self.currentUser = user
        self.selectedThing = None
        
        self.cursorIndex = self.targetCursor
        self.init_cursor()

        self.change_state(UIState.COMMAND)

    def get_target(self, user, validTargets):
        self.currentUser = user
        self.validTargets = validTargets
        self.selectedThing = None
        
        self.cursorIndex = self.targetCursor
        self.init_cursor()

        self.change_state(UIState.TARGET)

    def process_get_command(self):
        selection = self.process_input(0, len(self.currentUser.commands)-1)
        if (selection > -1):
            self.selectedThing = self.currentUser.commands[selection]
            self.UI_STATE = UIState.DEFAULT

    def process_get_target(self):
        selection = self.process_input(0, len(self.validTargets)-1)
        if (selection > -1):
            self.selectedThing = self.validTargets[selection]
            self.UI_STATE = UIState.DEFAULT

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

    def render_hero_status(self):
        self.BC.CONTROLLER.VIEW_SURF.blit(self.windowImage, self.windowAnchors[0])
        vOffset = (0, 8)
        index = 0
        for hero in self.BC.battlers:
            if (hero.isHero):
                self.BC.CONTROLLER.TEXT_MANAGER.draw_text(hero.NAME, self.heroStatusAnchors[index], g.WHITE)
                self.BC.CONTROLLER.TEXT_MANAGER.draw_text(str(hero.HP) + "/" + str(hero.MAXHP), utility.add_tuple(self.heroStatusAnchors[index], (1, 10)), g.WHITE, g.FONT_SML)
                self.BC.CONTROLLER.TEXT_MANAGER.draw_text(str(hero.SP) + "/" + str(hero.MAXSP), utility.add_tuple(self.heroStatusAnchors[index], (30, 10)), g.WHITE, g.FONT_SML)
                #self.BC.CONTROLLER.TEXT_MANAGER.draw_text("SP:" + str(hero.SP), utility.add_tuple(self.heroStatusAnchors[index], utility.scale_tuple(vOffset, (1,2))))
                index += 1

    def render_turn_cursor(self):
        self.BC.CONTROLLER.VIEW_SURF.blit(self.currentTurnCursor, utility.add_tuple(self.battlerAnchors[self.BC.currentBattler.battlerIndex], (4, -8)))

    def render_target_cursor(self):
        self.BC.CONTROLLER.VIEW_SURF.blit(self.currentTargetCursor, utility.add_tuple(self.battlerAnchors[self.validTargets[self.cursorIndex].battlerIndex], (4, -8)))


    def render_battlers(self):
        index = 0
        for battler in self.BC.battlers:
            if battler.HP > 0:
                self.BC.CONTROLLER.VIEW_SURF.blit(battler.spr["battle"], self.battlerAnchors[index])
            index += 1

    def render_turns(self):
        self.BC.CONTROLLER.VIEW_SURF.blit(self.turnImage, self.turnBannerAnchor)
        turnQueueCopy = self.BC.turnQueue[:]
        index = 0 
        while turnQueueCopy:
            battler = heapq.heappop(turnQueueCopy)
            if (battler[2].isHero):
                img = self.heroTurnImage
            else:
                img = self.monTurnImage
            self.BC.CONTROLLER.VIEW_SURF.blit(img, self.turnAnchors[index])
            self.BC.CONTROLLER.VIEW_SURF.blit(battler[2].spr['icon'], utility.add_tuple(self.turnAnchors[index], (3,0)))
            
            label = battler[2].NAME[0:5]
            self.BC.CONTROLLER.TEXT_MANAGER.draw_text(label, utility.add_tuple(self.turnAnchors[index], (2,18)), g.WHITE, g.FONT_SML)
            index += 1
            

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

        if (self.UI_STATE == UIState.TARGET):
            self.process_get_target()
            self.render_target_window()
            self.render_target_cursor()
        elif (self.UI_STATE == UIState.COMMAND):
            self.process_get_command()
            self.render_command_window()
            
        self.render_turn_cursor()
        #self.render_output()
        self.render_turns()

        index = 0
        for popup in self.popupList:
            if popup.life > 0:
                popup.update()
            else:
                del self.popupList[index]
            index += 1
                
        
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
        print ("UI STATE CHANGED: " + str(self.PREV_UI_STATE) + " >> " + str(self.UI_STATE))

    def prev_state(self):

        print (self.UI_STATE)
        print (self.BC.BATTLE_STATE)
        self.UI_STATE = self.PREV_UI_STATE
        self.BC.prev_state()
        print()
        print (self.UI_STATE)
        print (self.BC.BATTLE_STATE)
        

    def print_line(self, string):
        self.output.append(string)

    def process_input(self, cMin, cMax):
        dT = self.BC.CONTROLLER.CLOCK.get_time()
        if (g.CURSOR_TIMER >= 0):
            g.CURSOR_TIMER -= dT
        if (g.CONFIRM_TIMER >= 0):
            g.CONFIRM_TIMER -= dT   
        
        ##self.BC.CONTROLLER.event_loop()
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
                if (self.UI_STATE == UIState.TARGET):
                    self.cursorIndex = self.commandCursor
                    self.change_state(UIState.COMMAND)
                    self.BC.change_state(BattleState.COMMAND)
                    
        return -1

    def create_popup(self, string, pos, life = g.BATTLE_POPUP_LIFE):
        self.popupList.append(BattleUIPopup(self, string, pos, life))
    
class BattleUIPopup (object):
    def __init__(self, ui, string, pos, life):
        self.ui = ui
        self.string = string
        self.life = life
        self.x = pos[0]
        self.y = pos[1]

    def update(self):
        self.y -= 0.25
        self.life -= self.ui.BC.CONTROLLER.CLOCK.get_time()
        self.ui.BC.CONTROLLER.TEXT_MANAGER.draw_text_shaded(self.string, (self.x, math.floor(self.y)))

#################
##ACTOR CLASSES##
#################

class BattleActor (object):
    
    def __init__(self, BC, isHero, NAME, spr, LV = 1, HP=10, MAXHP = 10, SP = 10, MAXSP = 10, ATK = 5, DEF = 5, MATK = 5, MDEF = 5, AGI = 5, LCK = 5, HIT = 95, EVA = 5, RES = {}):
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

        self.spr = spr

        
        self.battlerIndex = self.BC.battlerCount
        self.pos = self.BC.UI.battlerAnchors[self.battlerIndex]
        self.BC.battlerCount += 1

        if not RES:
            self.RES = {}
            for i in range(0, 8):
                self.RES[i] = 0
        else:
            self.RES = RES

        #TODO: Add damage resistances

        self.isAI = (not self.isHero)
        self.aggro = 0
        
        self.mods = {}
        self.mods[BattlerStatus.DEFEND] = 0
        self.mods[BattlerStatus.SLEEP] = 0
        self.mods[BattlerStatus.POISON] = 0
        self.mods[BattlerStatus.SILENCE] = 0
        self.mods[BattlerStatus.STUN] = 0
        self.mods[BattlerStatus.PARALYZE] = 0

        self.commands = []
        self.commands.append(CmdAttack)
        self.commands.append(CmdDefend)

    def aggro_up(self, value=10):
        self.aggro += value
        if (self.aggro > 100):
            self.aggro = 100

    def aggro_down(self, value=10):
        self.aggro -= value
        if (self.aggro < 0):
            self.aggro = 0

    def aggro_half(self):
        self.aggro = self.aggro // 2

    def can_act(self):
        print ()
        if (self.HP == 0):
            return False
        elif (self.mods[BattlerStatus.SLEEP] > 0):
            self.BC.UI.print_line(" " + self.NAME + " is asleep.")
            self.BC.UI.create_popup("zzZ", self.pos)
            print (self.NAME + " is asleep.")
            return False
        elif (self.mods[BattlerStatus.STUN] > 0):
            self.BC.UI.print_line(" " + self.NAME + " can't move.")
            self.BC.UI.create_popup("Stunned", self.pos)
            print (self.NAME + " is stunned.")
            return False
        elif (self.mods[BattlerStatus.PARALYZE] > 0):
            self.BC.UI.print_line(self.NAME + " is paralyzed.")
            print (self.NAME  + " is paralyzed.")
            return False
        else:
            self.BC.UI.print_line(" " + self.NAME + "'s turn")
            print ("It's " + self.NAME + "'s turn.")
            return True

    def stun(self):
        if self.mods[BattlerStatus.DEFEND] > 0:
            self.BC.mods[BattlerStatus.STUN] = 0
            print (self.NAME + "'s defense was broken!")
        else:
            self.BC.UI.print_line(self.NAME + " is stunned!")
            print (self.NAME + " is stunned!")
            self.mods[BattlerStatus.STUN] += 1

    def before_turn(self):
        self.BC.currentBattler = self
        self.mods[BattlerStatus.DEFEND] -= 1
        self.mods[BattlerStatus.SLEEP] -= 1
        self.mods[BattlerStatus.PARALYZE] -= 1
        for mod in self.mods:
            if (self.mods[mod] < 0):
                self.mods[mod] = 0

    def after_turn(self):
        self.mods[BattlerStatus.STUN] = 0
        self.BC.change_state(BattleState.FIGHT)

    #needs to be implemented per object
    def take_turn(self):
        self.before_turn()
        
        if (self.can_act()):
            if (not self.isAI):
                self.BC.change_state(BattleState.COMMAND)
                self.BC.UI.get_command(self)
            else:
                self.commands[0].start(self)
        else:
            self.after_turn()

    def take_damage(self, damage, damageType = DamageType.NONE):
        #TODO: implement damage types and resistances
        damage -= math.floor(damage * self.RES[damageType])
        self.HP -= damage
        self.aggro_down()
        self.BC.UI.print_line(self.NAME + " takes " + str(damage) + " damage!")
        print (self.NAME + " takes " + str(damage) + " damage!")
        self.BC.UI.create_popup(str(damage), self.pos)
        
        if (self.HP < 0):
            self.HP = 0
        if (self.HP == 0):
            self.BC.UI.print_line(self.NAME + " died!")
            print (self.NAME + " died!")
            
###################
##COMMAND CLASSES##
###################

class CmdAttack():
    def name():
        return "Attack"

    def start(user):
        if (user.isHero):
            CmdAttack.get_targets(user)
        else:
            CmdAttack.get_targets_auto(user)
    
    def get_targets(user):
        ALL = False
        USER = False
        OPPOSITE = True
        SAME = False
        ALIVE = True
        DEAD = False

        validTargets = []
        selectedTargets = []
        index = 0
        for target in user.BC.battlers:
            if ((OPPOSITE and (user.isHero != target.isHero)) or (SAME and (user.isHero == target.isHero))):
                if ((ALIVE and (target.HP > 0)) or (DEAD and (target.HP == 0))):
                    validTargets.append(target)
            index += 1

        user.BC.change_state(BattleState.TARGET)
        user.BC.UI.get_target(user, validTargets)
        user.BC.queuedAction = CmdAttack.execute

    def get_targets_auto(user, mostAggro=True):
        if mostAggro:
            bestAggro = -1
        else:
            bestAggro = 101
        bestTarget = None
        for target in user.BC.battlers:
            if (user.isHero != target.isHero and target.HP > 0):
                if mostAggro:
                    if target.aggro > bestAggro:
                        bestAggro = target.aggro
                        bestTarget = target
                else:
                    if target.aggro < bestAggro:
                        bestAggro = target.aggro
                        bestTarget = target
                        
        CmdAttack.execute(user, bestTarget)
    
    def execute(user, target):
        #for target in targets:
        user.BC.UI.print_line(user.NAME + " attacks " + target.NAME)
        print(user.NAME + " attacks " + target.NAME)
        if user.BC.hit_calc(user, target):
            if not user.BC.dodge_calc(user, target):
                dmg = user.BC.phys_dmg_calc(user, target)
                if user.BC.crit_calc(user, target):
                    dmg*=2
                    target.stun()
                dmg -= user.BC.phys_def_calc(user, target)
                if (dmg < 0):
                    dmg = 0
                user.aggro_up()
                target.take_damage(dmg, DamageType.PHYS)

        user.after_turn()

class CmdDefend():

    def name():
        return "Defend"

    def start(user):
        CmdDefend.execute(user, user)

    def execute(user, target):
        user.BC.UI.print_line(user.NAME + " is defending.")
        print (user.NAME + " is defending.")
        user.mods[BattlerStatus.DEFEND] += 1

        user.after_turn()
