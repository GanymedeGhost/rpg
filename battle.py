import random
import heapq
import pygame
import pygame.locals
import my_globals as g
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

class UIState():
    DEFAULT = 0
    TARGET = 1
    COMMAND = 2
    SKILL = 3
    ITEM = 4
    

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

        args = {}
        #hero 1
        isHero = True
        NAME = "Asa"
        LV = 1
        HP = 10
        SP = 10
        ATK = 6
        DEF = 5
        MATK = 6
        MDEF = 5
        AGI = 5
        LCK = 5
        HIT = 95
        EVA = 5
        battler = BattleActor(self, isHero, NAME, LV, HP, SP, ATK, DEF, MATK, MDEF, AGI, LCK, HIT, EVA)
        battler.img = pygame.image.load("spr/battle/hero-asa.png")
        battler.imgTurn = pygame.image.load("spr/battle/turn-asa.png")
        self.battlers.append(battler)
        #hero 2
        isHero = True
        NAME = "Lux"
        LV = 1
        HP = 18
        SP = 5
        ATK = 8
        DEF = 6
        MATK = 2
        MDEF = 2
        AGI = 4
        LCK = 7
        HIT = 90
        EVA = 5
        battler = BattleActor(self, isHero, NAME, LV, HP, SP, ATK, DEF, MATK, MDEF, AGI, LCK, HIT, EVA)
        battler.img = pygame.image.load("spr/battle/hero-lux.png")
        battler.imgTurn = pygame.image.load("spr/battle/turn-lux.png")
        self.battlers.append(battler)
        #hero 3
        isHero = True
        NAME = "Elle"
        LV = 1
        HP = 7
        SP = 15
        ATK = 3
        DEF = 4
        MATK = 8
        MDEF = 7
        AGI = 6
        LCK = 5
        HIT = 95
        EVA = 5
        battler = BattleActor(self, isHero, NAME, LV, HP, SP, ATK, DEF, MATK, MDEF, AGI, LCK, HIT, EVA)
        battler.img = pygame.image.load("spr/battle/hero-elle.png")
        battler.imgTurn = pygame.image.load("spr/battle/turn-elle.png")
        self.battlers.append(battler)
        #enemy
        isHero = False
        NAME = "Slime1"
        LV = 1
        HP = 8
        SP = 5
        ATK = 5
        DEF = 5
        MATK = 5
        MDEF = 5
        AGI = 5
        LCK = 5
        HIT = 95
        EVA = 5
        battler = BattleActor(self, isHero, NAME, LV, HP, SP, ATK, DEF, MATK, MDEF, AGI, LCK, HIT, EVA)
        battler.img = pygame.image.load("spr/battle/mon-slime.png")
        battler.imgTurn = pygame.image.load("spr/battle/mon-slime.png")
        self.battlers.append(battler)
        NAME = "Slime2"
        battler = BattleActor(self, isHero, NAME, LV, HP, SP, ATK, DEF, MATK, MDEF, AGI, LCK, HIT, EVA)
        battler.img = pygame.image.load("spr/battle/mon-slime.png")
        battler.imgTurn = pygame.image.load("spr/battle/mon-slime.png")
        self.battlers.append(battler)
        NAME = "Slime3"
        battler = BattleActor(self, isHero, NAME, LV, HP, SP, ATK, DEF, MATK, MDEF, AGI, LCK, HIT, EVA)
        battler.img = pygame.image.load("spr/battle/mon-slime.png")
        battler.imgTurn = pygame.image.load("spr/battle/mon-slime.png")
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

    def prev_state(self):
        self.BATTLE_STATE = self.PREV_BATTLE_STATE

    def update(self):
        
        if self.BATTLE_STATE == BattleState.COMMAND:
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
                        battler.take_turn()
                else:
                    self.next_round()
            else:
                if self.heroes_alive():
                    self.change_state(BattleState.WIN)
                else:
                    self.change_state(BattleState.WIN)

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

    #TODO: delegate to UI
##    def get_target(self, battler, opposite = True, same = False, alive = True, dead = False):
##        index = 0
##        for target in self.battlers:
##            if ((opposite and (battler.isHero != target.isHero)) or (same and (battler.isHero == target.isHero))):
##                if ((alive and (target.HP > 0)) or (dead and (target.HP == 0))):
##                    print (str(index) + ": " + target.NAME)
##            index += 1
##        targetString = input("Target #: ")
##        return self.battlers[int(targetString)]

    def hit_calc(self, user, target):
        roll = random.randint(0, 100)
        if roll < user.HIT:
            return True
        else:
            self.UI.print_line("Missed!")
            print ("Missed!")
            return False

    def dodge_calc(self, user, target):
        roll = random.randint(0, 100)
        if roll < target.EVA:
            self.UI.print_line("Dodged!")
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
        self.cmdAnchors = [(8,100), (8, 110)]
        self.tgtAnchors = [(8,100), (8, 110), (8,120)]
        self.outAnchors = [(2, 66), (2, 58), (2,50), (2,42), (2,34), (2, 26), (2, 18), (2,10), (2,2)]

        self.cursorIndex = 0
        self.commandCursor = 0
        self.targetCursor = 0
        self.skillCursor = 0
        self.itemCursor = 0

        self.windowImage = pygame.image.load("spr/battle/ui-window.png")
        self.windowAnchors = [(0,85)]

        self.currentUser = 0
        self.validTargets = []
        #self.commandList = []
        
        self.selectedThing = None
        self.queuedMethod = None
        
        

    def get_command(self, user):
        #self.BC.BATTLE_STATE = BattleState.WAITING
        
        self.currentUser = user
        self.selectedThing = None
        
        self.cursorIndex = self.targetCursor
        self.init_cursor()

        self.change_state(UIState.COMMAND)
            
##        command = None
##        self.cursorIndex = 0
##        while not command:
##            callback = self.process_input(0, len(user.commands)-1)
##            if (callback > -1):
##                command = user.commands[callback]
##            self.render_command_window(user.commands)
##        return command

    def get_target(self, user, validTargets):
        #self.BC.BATTLE_STATE = BattleState.WAITING
        
        self.currentUser = user
        self.validTargets = validTargets
        self.selectedThing = None
        
        self.cursorIndex = self.targetCursor
        self.init_cursor()

        self.change_state(UIState.TARGET)
        
##        targets = []
##        self.cursorIndex = 0
##        while not targets:
##            callback = self.process_input(0, len(validTargets)-1)
##            if (callback > -1):
##                targets.append(validTargets[callback])
##            self.render_target_window(validTargets)
##        return targets

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
        #self.BC.CONTROLLER.VIEW_SURF.fill(g.WHITE)

        index = 0
        for command in self.currentUser.commands:
            self.BC.CONTROLLER.TEXT_MANAGER.draw_text(command.name(), self.cmdAnchors[index], g.WHITE)
            index += 1
        self.BC.CONTROLLER.VIEW_SURF.blit(self.cursorImage, utility.add_tuple(self.cmdAnchors[self.cursorIndex],(-self.cursorImage.get_width(),0)))
        
        #self.update()

    def render_target_window(self):
        #self.BC.CONTROLLER.VIEW_SURF.fill(g.WHITE)

        index = 0
        for target in self.validTargets:
            self.BC.CONTROLLER.TEXT_MANAGER.draw_text(target.NAME, self.tgtAnchors[index], g.WHITE)
            index += 1
        self.BC.CONTROLLER.VIEW_SURF.blit(self.cursorImage, utility.add_tuple(self.tgtAnchors[self.cursorIndex],(-self.cursorImage.get_width(),0)))
        
        #self.update()

    def render_hero_status(self):
        self.BC.CONTROLLER.VIEW_SURF.blit(self.windowImage, self.windowAnchors[0])
        vOffset = (0, 8)
        index = 0
        for hero in self.BC.battlers:
            if (hero.isHero):
                self.BC.CONTROLLER.TEXT_MANAGER.draw_text(hero.NAME, self.heroStatusAnchors[index], g.WHITE)
                #self.BC.CONTROLLER.TEXT_MANAGER.draw_text("HP:" + str(hero.HP), utility.add_tuple(self.heroStatusAnchors[index], utility.scale_tuple(vOffset, (1,1))))
                #self.BC.CONTROLLER.TEXT_MANAGER.draw_text("SP:" + str(hero.SP), utility.add_tuple(self.heroStatusAnchors[index], utility.scale_tuple(vOffset, (1,2))))
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
        self.BC.CONTROLLER.VIEW_SURF.fill(g.WHITE)
        self.render_hero_status()
        if (self.UI_STATE == UIState.TARGET):
            self.process_get_target()
            self.render_target_window()
        elif (self.UI_STATE == UIState.COMMAND):
            self.process_get_command()
            self.render_command_window()
        self.render_output()
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
        
        self.BC.CONTROLLER.event_loop()
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

#################
##ACTOR CLASSES##
#################

class BattleActor (object):
    
    def __init__(self, BC, isHero, NAME, LV = 1, HP=10, SP = 10, ATK = 5, DEF = 5, MATK = 5, MDEF = 5, AGI = 5, LCK = 5, HIT = 95, EVA = 5):
        self.BC = BC
        self.isHero = isHero
        self.NAME = NAME
        self.LV = LV
        self.HP = HP
        self.SP = SP
        self.ATK = ATK
        self.DEF = DEF
        self.MATK = MATK
        self.MDEF = MDEF
        self.AGI = AGI
        self.LCK = LCK
        self.HIT = HIT
        self.EVA = EVA

        self.img = None
        self.imgTurn = None

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
            print (self.NAME + " is asleep.")
            return False
        elif (self.mods[BattlerStatus.STUN] > 0):
            self.BC.UI.print_line(" " + self.NAME + " can't move.")
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

    def take_damage(self, damage, damageType):
        #TODO: implement damage types and resistances
        self.HP -= damage
        self.aggro_down()
        self.BC.UI.print_line(self.NAME + " takes " + str(damage) + " damage!")
        print (self.NAME + " takes " + str(damage) + " damage!")
        
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
