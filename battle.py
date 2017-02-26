import random
import heapq
import pygame
import pygame.locals
import my_globals as g
import utility

#ENUMS
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

class BattleController (object):
    def __init__(self):
        random.seed()
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

    def battle_loop(self):
        while (self.enemies_alive() and self.heroes_alive()):
            self.rounds += 1
            print ()
            print ("***********")
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
                
            #ACTOR ACTIONS
            while self.turnQueue and self.enemies_alive() and self.heroes_alive():
                priority, count, battler = heapq.heappop(self.turnQueue)
                if battler != None:
                    battler.take_turn()

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

    def get_target(self, battler, opposite = True, same = False, alive = True, dead = False):
        index = 0
        for target in self.battlers:
            if ((opposite and (battler.isHero != target.isHero)) or (same and (battler.isHero == target.isHero))):
                if ((alive and (target.HP > 0)) or (dead and (target.HP == 0))):
                    print (str(index) + ": " + target.NAME)
            index += 1
        targetString = input("Target #: ")
        return self.battlers[int(targetString)]

    def hit_calc(user, target):
        roll = random.randint(0, 100)
        if roll < user.HIT:
            return True
        else:
            print ("Missed!")
            return False

    def dodge_calc(user, target):
        roll = random.randint(0, 100)
        if roll < target.EVA:
            print ("Dodged!")
            return True
        else:
            return False

    def crit_calc(user, target):
        roll = random.randint(0, 255)
        #print ("Crit roll : " + str(roll))
        if roll < user.LCK:
            print ("Crit!")
            return True
        else:
            return False

    def phys_def_calc(user, target):
        modValue = 0
        if (target.mods[BattlerStatus.DEFEND] > 0):
            print (target.NAME + " has a defense bonus")
            modValue = target.DEF // 2
        defTotal = target.DEF + modValue
        #print ("DEF: " + str(target.DEF) + " (+" + str(modValue) + ")")
        return defTotal

    def phys_dmg_calc(user, target):
        dmgMax = user.ATK * 2
        dmgMin = dmgMax - (user.ATK // 2)
        dmg = random.randint(dmgMin, dmgMax)
        #print ("ATK: " + str(dmg) + " (" + str(dmgMin) + "," + str(dmgMax) + ")")
        if (dmg < 0):
            dmg = 0
        return dmg

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
            print (self.NAME + " is asleep.")
            return False
        elif (self.mods[BattlerStatus.STUN] > 0):
            print (self.NAME + " is stunned.")
            return False
        elif (self.mods[BattlerStatus.PARALYZE] > 0):
            print (self.NAME  + " is paralyzed.")
            return False
        else:
            print ("It's " + self.NAME + "'s turn.")
            return True

    def stun(self):
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
                print ("COMMANDS")
                
                index = 0
                for cmd in self.commands:
                    print (str(index) + ": " + cmd.name())
                    index += 1
                    
                cmdInput = input("# >> ")

                targets = self.commands[int(cmdInput)].get_targets(self)
                self.commands[int(cmdInput)].execute(self, targets)
            else:
                targets = self.commands[0].get_targets_auto(self)
                self.commands[0].execute(self, targets)

        self.after_turn()

    def take_damage(self, damage, damageType):
        #TODO: implement damage types and resistances
        self.HP -= damage
        self.aggro_down()
        print (self.NAME + " takes " + str(damage) + " damage!")
        
        if (self.HP < 0):
            self.HP = 0
        if (self.HP == 0):
            print (self.NAME + " died!")
            
##
##BATTLE COMMAND TEMPLATE
##
##class BattleCommand(object):
##    def __init__(self):
##        targetArgs = {}
##    
##    def get_targets(user):
##        if (user.isHero):
##            return user.BC.first_enemy()
##        else:
##            return user.BC.first_hero()
##        
##    def execute (user, target):
##        print ("execute...")

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
        targets = []
        index = 0
        for target in user.BC.battlers:
            if ((OPPOSITE and (user.isHero != target.isHero)) or (SAME and (user.isHero == target.isHero))):
                if ((ALIVE and (target.HP > 0)) or (DEAD and (target.HP == 0))):
                    print (str(index) + ": " + target.NAME)
            index += 1
        
        targetString = input("# >> ")
        targets.append(user.BC.battlers[int(targetString)])
        return targets

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
            print(user.NAME + " attacks " + target.NAME)
            if BattleController.hit_calc(user, target):
                if not BattleController.dodge_calc(user, target):
                    dmg = BattleController.phys_dmg_calc(user, target)
                    if BattleController.crit_calc(user, target):
                        dmg*=2
                        target.stun()
                    dmg -= BattleController.phys_def_calc(user, target)
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
        print (user.NAME + " is defending.")
        user.mods[BattlerStatus.DEFEND] += 1

if __name__=='__main__':
    BC = BattleController()

    BC.battle_loop()
    print ("***")
    print ("Battle over")
