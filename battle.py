import pygame
import pygame.locals
import utility
import random
import heapq

class BattleMod():
    DEFEND = 0
    POISON = 1
    SLEEP = 2
    SILENCE = 3
    STUN = 4
    PARALYZE = 5

class Battle (object):
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
        self.battlers.append( BattleActor(isHero, NAME, LV, HP, SP, ATK, DEF, MATK, MDEF, AGI, LCK, HIT, EVA))
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
        self.battlers.append( BattleActor(isHero, NAME, LV, HP, SP, ATK, DEF, MATK, MDEF, AGI, LCK, HIT, EVA)) 
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
        self.battlers.append( BattleActor(isHero, NAME, LV, HP, SP, ATK, DEF, MATK, MDEF, AGI, LCK, HIT, EVA))         
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
        self.battlers.append( BattleActor(isHero, NAME, LV, HP, SP, ATK, DEF, MATK, MDEF, AGI, LCK, HIT, EVA))

        self.rounds = 0
        self.turnQueue = []
        self.turnFinder = {}

    def battle_loop(self):
        while (self.enemies_alive() and self.heroes_alive()):
            self.rounds += 1
            print ("***********")
            print ("Round: " + str(self.rounds))
            print ("***********")
            self.list_heroes()
            self.list_enemies()
            self.get_turn_order()
            #ACTOR ACTIONS
            while self.turnQueue:
                priority, count, battler = heapq.heappop(self.turnQueue)
                if battler != None:
                    battler.before_turn()
                    if (battler.can_act()):
                        del self.turnFinder[battler]
                        if battler.isHero:
                            command = input("What will " + battler.NAME + " do? ")
                            if (command == "attack"):
                                battler.attack(self.get_target(battler))
                            elif (command == "defend"):
                                battler.defend()
                            else:
                                print("Invalid command!")
                        else:
                            AIRoll = random.randint(0, 5)
                            if AIRoll < 3 :
                                battler.attack(self.first_hero())
                            elif AIRoll >= 3:
                                battler.defend()
                    battler.after_turn()

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
        print("*ENEMIES*")
        for battler in self.battlers:
            if not battler.isHero:
                print (battler.NAME)
                if (battler.HP > 0):
                    print ("HP: " + str(battler.HP))
                else:
                    print ("DEAD")
        print("")

    def list_heroes(self):
        print("*HEROES*")
        for battler in self.battlers:
            if battler.isHero:
                print (battler.NAME)
                if (battler.HP > 0):
                    print ("HP: " + str(battler.HP))
                else:
                    print ("KO")
        print("")

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

class BattleActor (object):
    
    def __init__(self, isHero, NAME, LV = 1, HP=10, SP = 10, ATK = 5, DEF = 5, MATK = 5, MDEF = 5, AGI = 5, LCK = 5, HIT = 95, EVA = 5):
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
        
        self.mods = {}
        self.mods[BattleMod.DEFEND] = 0
        self.mods[BattleMod.SLEEP] = 0
        self.mods[BattleMod.POISON] = 0
        self.mods[BattleMod.SILENCE] = 0
        self.mods[BattleMod.STUN] = 0
        self.mods[BattleMod.PARALYZE] = 0
        

    def can_act(self):
        if (self.HP == 0 or
            self.mods[BattleMod.SLEEP] > 0 or
            self.mods[BattleMod.STUN] > 0 or
            self.mods[BattleMod.PARALYZE] > 0):
            return False
        else:
            return True

    def attack(self, target):
        if (random.randint(0, 100) < self.HIT):
            if (random.randint(0, 100) > target.EVA):
                if (target.mods[BattleMod.DEFEND] > 0):
                    defMod = target.DEF // 2
                else:
                    defMod = 0
                print ("defMod: " + str(defMod))
                defTotal = target.DEF + defMod
                damageMin = self.ATK + (self.ATK // 2) - defTotal
                damageMax = self.ATK * 2 - defTotal
                damage = random.randint(damageMin, damageMax)
                if (random.randint(0, 255) < self.LCK):
                    damage += self.ATK
                    target.stun()
                    print("CRITICAL HIT!")
                if (damage < 0):
                    damage = 0
                print (self.NAME + " does " + str(damage) + " damage to " + target.NAME)
                target.take_damage(damage)
            else:
                print (target.NAME + " avoided " + self.NAME + "'s attack!")
        else:
            print (self.NAME + "'s attack missed " + target.NAME)

    def stun(self):
        self.mods[BattleMod.STUN] += 1
        

    def defend(self):
        print (self.NAME + " is defending.")
        self.mods[BattleMod.DEFEND] += 1

    def after_turn(self):
        self.mods[BattleMod.STUN] = 0

    def before_turn(self):
        self.mods[BattleMod.DEFEND] -= 1
        self.mods[BattleMod.SLEEP] -= 1
        self.mods[BattleMod.PARALYZE] -= 1
        for mod in self.mods:
            if (self.mods[mod] < 0):
                self.mods[mod] = 0

    def take_damage(self, damage):
        self.HP -= damage
        
        if (self.HP < 0):
            self.HP = 0
        if (self.HP == 0):
            print (self.NAME + " died!")
            

if __name__=='__main__':
    BC = Battle()

    BC.battle_loop()
    print ("***")
    print ("Battle over")
        

    
