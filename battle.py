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
        self.battlers = []

        args = {}
        #hero 1
        isHero = True
        NAME = "Asa"
        LV = 1
        HP = 10
        SP = 10
        ATK = 8
        DEF = 5
        MATK = 5
        MDEF = 5
        AGI = 2
        LCK = 5
        HIT = 80
        EVA = 5
        self.battlers.append( BattleActor(self, isHero, NAME, LV, HP, SP, ATK, DEF, MATK, MDEF, AGI, LCK, HIT, EVA))
        #hero 2
        isHero = True
        NAME = "Lux"
        LV = 1
        HP = 10
        SP = 10
        ATK = 4
        DEF = 3
        MATK = 5
        MDEF = 5
        AGI = 8
        LCK = 100
        HIT = 95
        EVA = 8
        self.battlers.append( BattleActor(self, isHero, NAME, LV, HP, SP, ATK, DEF, MATK, MDEF, AGI, LCK, HIT, EVA)) 
        #enemy
        isHero = False
        NAME = "Slime"
        LV = 1
        HP = 8
        SP = 10
        ATK = 4
        DEF = 6
        MATK = 5
        MDEF = 5
        AGI = 3
        LCK = 5
        HIT = 95
        EVA = 8
        self.battlers.append( BattleActor(self, isHero, NAME, LV, HP, SP, ATK, DEF, MATK, MDEF, AGI, LCK, HIT, EVA))         
        #enemy
        isHero = False
        NAME = "Bear"
        LV = 1
        HP = 12
        SP = 10
        ATK = 10
        DEF = 5
        MATK = 5
        MDEF = 5
        AGI = 2
        LCK = 5
        HIT = 50
        EVA = 2
        self.battlers.append( BattleActor(self, isHero, NAME, LV, HP, SP, ATK, DEF, MATK, MDEF, AGI, LCK, HIT, EVA))

        self.rounds = 0
        self.turnQueue = []
        self.turnFinder = {}

        

    def update(self):
        if self.enemies_alive() and self.heroes_alive():
            #ACTOR ACTIONS
            if self.turnQueue:
                priority, count, battler = heapq.heappop(self.turnQueue)
                if battler != None:
                    battler.take_turn()
            else:
                self.next_round()
        else:
            if self.enemies_alive():
                self.BATTLE_STATE = BattleState.LOSE
            else:
                self.BATTLE_STATE = BattleState.WIN 

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
        self.output = []
        self.cursorPos = (0,0)
        self.cursorImage = pygame.image.load("spr/cursor-h.png")
        self.cursorRect = self.cursorImage.get_rect()
        self.heroStatusAnchors = [(2, 4), (66, 4), (110, 4)]
        self.cmdAnchors = [(8,100), (8, 110)]
        self.tgtAnchors = [(8,100), (8, 110)]
        self.outAnchors = [(2, 88), (2, 80), (2,72), (2,64), (2,56), (2, 48), (2, 40), (2,32), (2,24)]
        self.cursorIndex = 0

    def get_command(self, user):
        g.CURSOR_TIMER = 0
        g.CONFIRM_TIMER = g.CONFIRM_DELAY
        command = None
        self.cursorIndex = 0

        while not command:
            callback = self.process_input(0, len(user.commands)-1)
            if (callback > -1):
                command = user.commands[callback]
            self.render_command_window(user.commands)
        return command

    def get_target(self, user, validTargets):
        g.CURSOR_TIMER = 0
        g.CONFIRM_TIMER = g.CONFIRM_DELAY
        targets = []
        self.cursorIndex = 0
        while not targets:
            callback = self.process_input(0, len(validTargets)-1)
            if (callback > -1):
                targets.append(validTargets[callback])
            self.render_target_window(validTargets)
        return targets

    def render_command_window(self, commands):
        self.BC.CONTROLLER.VIEW_SURF.fill(g.WHITE)

        index = 0
        for command in commands:
            self.BC.CONTROLLER.TEXT_MANAGER.draw_text(command.name(), self.cmdAnchors[index])
            index += 1
        self.BC.CONTROLLER.VIEW_SURF.blit(self.cursorImage, utility.add_tuple(self.cmdAnchors[self.cursorIndex],(-self.cursorImage.get_width(),0)))
        
        self.update()

    def render_target_window(self, validTargets):
        self.BC.CONTROLLER.VIEW_SURF.fill(g.WHITE)

        index = 0
        for target in validTargets:
            self.BC.CONTROLLER.TEXT_MANAGER.draw_text(target.NAME, self.tgtAnchors[index])
            index += 1
        self.BC.CONTROLLER.VIEW_SURF.blit(self.cursorImage, utility.add_tuple(self.tgtAnchors[self.cursorIndex],(-self.cursorImage.get_width(),0)))
        
        self.update()

    def render_hero_status(self):
        vOffset = (0, 8)
        index = 0
        for hero in self.BC.battlers:
            if (hero.isHero):
                self.BC.CONTROLLER.TEXT_MANAGER.draw_text(hero.NAME, self.heroStatusAnchors[index])
                self.BC.CONTROLLER.TEXT_MANAGER.draw_text("HP:" + str(hero.HP), utility.add_tuple(self.heroStatusAnchors[index], utility.scale_tuple(vOffset, (1,1))))
                self.BC.CONTROLLER.TEXT_MANAGER.draw_text("SP:" + str(hero.SP), utility.add_tuple(self.heroStatusAnchors[index], utility.scale_tuple(vOffset, (1,2))))
                index += 1

    def render_output(self, maxLines = 6):
        lineCount = 0
        for line in reversed(self.output):
            self.BC.CONTROLLER.TEXT_MANAGER.draw_text(line, self.outAnchors[lineCount])
            lineCount += 1
            if lineCount > maxLines-1:
                break

    def update(self):
        self.render_hero_status()
        self.render_output()
        self.BC.CONTROLLER.window_render()

    def print_line(self, string):
        self.output.append(string)

    def process_input(self, cMin, cMax):
        if (g.CURSOR_TIMER > 0):
            g.CURSOR_TIMER -= 1
        if (g.CONFIRM_TIMER > 0):
            g.CONFIRM_TIMER -= 1    
        
        self.BC.CONTROLLER.event_loop()
        if self.BC.CONTROLLER.KEYS[g.KEY_DOWN]:
            if not g.CURSOR_TIMER:
                g.CURSOR_TIMER = g.CURSOR_DELAY
                self.cursorIndex += 1
                if self.cursorIndex > cMax:
                    self.cursorIndex = cMin
        elif self.BC.CONTROLLER.KEYS[g.KEY_UP]:
            if not g.CURSOR_TIMER:
                g.CURSOR_TIMER = g.CURSOR_DELAY
                self.cursorIndex -= 1
                if self.cursorIndex < cMin:
                    self.cursorIndex = cMax
        elif self.BC.CONTROLLER.KEYS[g.KEY_CONFIRM]:
            if not g.CONFIRM_TIMER:
                g.CURSOR_TIMER = g.CURSOR_DELAY
                return self.cursorIndex
            
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
        self.mods[BattlerStatus.DEFEND] -= 1
        self.mods[BattlerStatus.SLEEP] -= 1
        self.mods[BattlerStatus.PARALYZE] -= 1
        for mod in self.mods:
            if (self.mods[mod] < 0):
                self.mods[mod] = 0

    def after_turn(self):
        self.mods[BattlerStatus.STUN] = 0

    #needs to be implemented per object
    def take_turn(self):
        self.before_turn()
        
        if (self.can_act()):
            if (not self.isAI):

                #TODO: Move to UI
##                print ("COMMANDS")
##                index = 0
##                for cmd in self.commands:
##                    print (str(index) + ": " + cmd.name())
##                    index += 1
##                cmdInput = input("# >> ")
                #

                command = self.BC.UI.get_command(self)
                targets = command.get_targets(self)

                command.execute(self, targets)
##                targets = self.commands[int(cmdInput)].get_targets(self)
##                self.commands[int(cmdInput)].execute(self, targets)
            else:
                targets = self.commands[0].get_targets_auto(self)
                self.commands[0].execute(self, targets)

        self.after_turn()

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
    
    def get_targets(user):
        ALL = False
        USER = False
        OPPOSITE = True
        SAME = False
        ALIVE = True
        DEAD = False

        #Delegate this to a UI class
        validTargets = []
        selectedTargets = []
        index = 0
        for target in user.BC.battlers:
            if ((OPPOSITE and (user.isHero != target.isHero)) or (SAME and (user.isHero == target.isHero))):
                if ((ALIVE and (target.HP > 0)) or (DEAD and (target.HP == 0))):
                    validTargets.append(target)
            index += 1
            
        
        selectedTargets = user.BC.UI.get_target(user, validTargets)

        return selectedTargets

    def get_targets_auto(user, mostAggro=True):
        targets = []
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
        targets.append(bestTarget)
        return targets
    
    def execute(user, targets):
        for target in targets:
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

class CmdDefend():

    def name():
        return "Defend"

    def get_targets(user):
        return user

    def get_targets_auto(user, mostAggro=True):
        return user

    def execute(user, target):
        user.BC.UI.print_line(user.NAME + " is defending.")
        print (user.NAME + " is defending.")
        user.mods[BattlerStatus.DEFEND] += 1
